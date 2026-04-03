# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""
Unit tests for the Google AI Studio (Gemini) API-key validation logic introduced in
the google-ai-integration.yml workflow.

These tests verify:
  1. The model defaults to ``gemini-2.5-flash`` when ``GEMINI_MODEL`` is not set.
  2. The model is overridable via the ``GEMINI_MODEL`` environment variable.
  3. A successful Gemini response is accepted without error.
  4. A failed Gemini call (e.g. 404 / deprecated model) causes exit code 1.
  5. ``_gemini_vlm_ocr`` in ingestion.py respects ``GEMINI_MODEL`` too.
"""
from __future__ import annotations

import importlib
import os
import sys
import types
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helper: run the inline validation script extracted from the workflow
# ---------------------------------------------------------------------------

def _run_validation(api_key: str, model_env: str | None, mock_client_cls) -> int:
    """Simulate the inline Python script from the workflow's validation step.

    Returns the exit code (0 = success, 1 = failure).
    """
    env_patch: dict[str, str] = {"GAIS_BM_APIK": api_key}
    if model_env is not None:
        env_patch["GEMINI_MODEL"] = model_env

    genai_mod = types.ModuleType("google.genai")
    genai_mod.Client = mock_client_cls  # type: ignore[attr-defined]

    google_mod = types.ModuleType("google")
    google_mod.genai = genai_mod  # type: ignore[attr-defined]

    with patch.dict(os.environ, env_patch, clear=False):
        with patch.dict(sys.modules, {"google": google_mod, "google.genai": genai_mod}):
            # Inline script logic (mirrors the workflow step exactly)
            import os as _os
            import sys as _sys
            from google import genai  # noqa: PLC0415

            _api_key = _os.environ["GAIS_BM_APIK"]
            _model = _os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
            _client = genai.Client(api_key=_api_key)

            try:
                _response = _client.models.generate_content(
                    model=_model,
                    contents="Reply with only the word: OK",
                )
                _response.text.strip()
                return 0
            except Exception:
                return 1


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGeminiModelDefault:
    """GEMINI_MODEL env var handling."""

    def test_default_model_is_gemini_25_flash(self) -> None:
        """When GEMINI_MODEL is unset the script must use gemini-2.5-flash."""
        captured_model: list[str] = []

        class FakeClient:
            def __init__(self, api_key: str) -> None:
                pass

            class models:
                @staticmethod
                def generate_content(model: str, contents: str):  # noqa: D401
                    captured_model.append(model)
                    resp = MagicMock()
                    resp.text = "OK"
                    return resp

        # Remove GEMINI_MODEL from env to test the default
        with patch.dict(os.environ, {"GAIS_BM_APIK": "test-key"}, clear=False):
            os.environ.pop("GEMINI_MODEL", None)
            _run_validation("test-key", None, FakeClient)

        assert captured_model == ["gemini-2.5-flash"]

    def test_model_overridable_via_env(self) -> None:
        """When GEMINI_MODEL is set, the script must use that model."""
        captured_model: list[str] = []

        class FakeClient:
            def __init__(self, api_key: str) -> None:
                pass

            class models:
                @staticmethod
                def generate_content(model: str, contents: str):
                    captured_model.append(model)
                    resp = MagicMock()
                    resp.text = "OK"
                    return resp

        _run_validation("test-key", "gemini-2.0-pro", FakeClient)

        assert captured_model == ["gemini-2.0-pro"]


class TestGeminiValidationSuccess:
    """Happy-path: valid API key + reachable model."""

    def test_successful_response_returns_exit_0(self) -> None:
        class FakeClient:
            def __init__(self, api_key: str) -> None:
                pass

            class models:
                @staticmethod
                def generate_content(model: str, contents: str):
                    resp = MagicMock()
                    resp.text = "OK"
                    return resp

        exit_code = _run_validation("valid-key", None, FakeClient)
        assert exit_code == 0


class TestGeminiValidationFailure:
    """Failure path: deprecated / unavailable model should cause exit code 1."""

    def test_404_error_returns_exit_1(self) -> None:
        class FakeClient:
            def __init__(self, api_key: str) -> None:
                pass

            class models:
                @staticmethod
                def generate_content(model: str, contents: str):
                    raise Exception(
                        "404 NOT_FOUND: This model models/gemini-2.0-flash is "
                        "no longer available to new users."
                    )

        exit_code = _run_validation("valid-key", None, FakeClient)
        assert exit_code == 1

    def test_invalid_api_key_returns_exit_1(self) -> None:
        class FakeClient:
            def __init__(self, api_key: str) -> None:
                pass

            class models:
                @staticmethod
                def generate_content(model: str, contents: str):
                    raise Exception("401 UNAUTHENTICATED: API key not valid.")

        exit_code = _run_validation("bad-key", None, FakeClient)
        assert exit_code == 1


class TestIngestionGeminiModel:
    """_gemini_vlm_ocr should honour the GEMINI_MODEL env var."""

    def test_ingestion_uses_gemini_model_env(self) -> None:
        """Verify that GEMINI_MODEL is forwarded to generate_content in ingestion."""
        captured: list[str] = []

        mock_response = MagicMock()
        mock_response.text = (
            '{"vendor_name":"Acme","invoice_number":"001",'
            '"invoice_date":"2026-01-01","total_amount":"10.00",'
            '"items":[{"item_name":"Flour","quantity":1,"unit_price":"10.00",'
            '"tax_rate":"0","expiration_date":null,"category":"dry",'
            '"unit_of_measure":"kg","vertical":"bakery"}]}'
        )

        mock_models = MagicMock()
        mock_models.generate_content.side_effect = (
            lambda model, contents: (captured.append(model), mock_response)[1]
        )
        mock_client = MagicMock()
        mock_client.models = mock_models

        mock_pil_image = MagicMock()

        with patch.dict(os.environ, {"GEMINI_MODEL": "gemini-2.5-pro"}, clear=False):
            with patch("app.ingestion._google_genai") as mock_genai:
                mock_genai.Client.return_value = mock_client
                with patch("PIL.Image.open", return_value=mock_pil_image):
                    # Force _GENAI_AVAILABLE = True for this test
                    import app.ingestion as ingestion_mod
                    original = ingestion_mod._GENAI_AVAILABLE
                    ingestion_mod._GENAI_AVAILABLE = True
                    try:
                        ingestion_mod._gemini_vlm_ocr(b"fake-image", "test-api-key")
                    except Exception:
                        pass  # JSON parsing irrelevant here
                    finally:
                        ingestion_mod._GENAI_AVAILABLE = original

        assert captured == ["gemini-2.5-pro"], (
            f"Expected model 'gemini-2.5-pro' but got {captured}"
        )

    def test_ingestion_default_model_is_gemini_25_flash(self) -> None:
        """When GEMINI_MODEL is absent, ingestion defaults to gemini-2.5-flash."""
        captured: list[str] = []

        mock_response = MagicMock()
        mock_response.text = (
            '{"vendor_name":"Acme","invoice_number":"001",'
            '"invoice_date":"2026-01-01","total_amount":"10.00",'
            '"items":[{"item_name":"Flour","quantity":1,"unit_price":"10.00",'
            '"tax_rate":"0","expiration_date":null,"category":"dry",'
            '"unit_of_measure":"kg","vertical":"bakery"}]}'
        )

        mock_models = MagicMock()
        mock_models.generate_content.side_effect = (
            lambda model, contents: (captured.append(model), mock_response)[1]
        )
        mock_client = MagicMock()
        mock_client.models = mock_models

        mock_pil_image = MagicMock()

        env_without_model = {k: v for k, v in os.environ.items() if k != "GEMINI_MODEL"}
        with patch.dict(os.environ, env_without_model, clear=True):
            with patch("app.ingestion._google_genai") as mock_genai:
                mock_genai.Client.return_value = mock_client
                with patch("PIL.Image.open", return_value=mock_pil_image):
                    import app.ingestion as ingestion_mod
                    original = ingestion_mod._GENAI_AVAILABLE
                    ingestion_mod._GENAI_AVAILABLE = True
                    try:
                        ingestion_mod._gemini_vlm_ocr(b"fake-image", "test-api-key")
                    except Exception:
                        pass
                    finally:
                        ingestion_mod._GENAI_AVAILABLE = original

        assert captured == ["gemini-2.5-flash"], (
            f"Expected default model 'gemini-2.5-flash' but got {captured}"
        )
