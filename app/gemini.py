# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""
Gemini AI client for BakeManage.

Model: gemini-3-flash-preview (Google AI Studio)
SDK:   google-genai v1.x

Thinking budget strategy (based on empirical probe of gemini-3-flash-preview):
  - budget=0 means thinking is fully OFF → fast (2-3s), clean STOP, resp tokens unconstrained
  - budget>0 with low maxOutputTokens → thinking consumes output budget, response gets starved → MAX_TOKENS
  - Rule: thinkingBudget=0 + maxOutputTokens=500 for OPERATIONAL queries (expiring, daily, waste)
          thinkingBudget=0 + maxOutputTokens=700 for INSIGHT queries (multi-module summaries)
          no thinkingConfig + maxOutputTokens=1800 for ANALYTICAL queries (forecast, what-if)
          — auto mode lets the model decide its own thinking depth, no token starvation risk

Query complexity is detected by keyword signals from the incoming prompt.
Caller can also override complexity explicitly.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from .config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Complexity levels
# ---------------------------------------------------------------------------


class QueryComplexity(str, Enum):
    OPERATIONAL = (
        "operational"  # Status, expiring stock, daily check — budget=0, 500 tok
    )
    INSIGHT = "insight"  # Multi-module summary, menu eng, vendor — budget=0, 700 tok
    ANALYTICAL = (
        "analytical"  # Demand forecast, what-if, deep strategy — auto think, 1800 tok
    )


_ANALYTICAL_SIGNALS = {
    "forecast",
    "predict",
    "projection",
    "trend",
    "what if",
    "simulate",
    "optimise",
    "optimize",
    "strategy",
    "recommend",
    "plan",
    "next week",
    "next month",
    "compare",
    "analyse",
    "analyze",
    "deep dive",
}
_INSIGHT_SIGNALS = {
    "insight",
    "summary",
    "overview",
    "menu",
    "vendor",
    "engineering",
    "performance",
    "report",
    "breakdown",
    "highlight",
    "top",
    "best",
}


def detect_complexity(prompt: str) -> QueryComplexity:
    lower = prompt.lower()
    if any(s in lower for s in _ANALYTICAL_SIGNALS):
        return QueryComplexity.ANALYTICAL
    if any(s in lower for s in _INSIGHT_SIGNALS):
        return QueryComplexity.INSIGHT
    return QueryComplexity.OPERATIONAL


# ---------------------------------------------------------------------------
# Generation config per complexity
# ---------------------------------------------------------------------------

_CONFIGS: dict[QueryComplexity, dict[str, Any]] = {
    QueryComplexity.OPERATIONAL: {
        "max_output_tokens": 500,
        "thinking_budget": 0,  # OFF — fast and accurate for status queries
    },
    QueryComplexity.INSIGHT: {
        "max_output_tokens": 700,
        "thinking_budget": 0,  # OFF — structured multi-module output, no benefit from thinking
    },
    QueryComplexity.ANALYTICAL: {
        "max_output_tokens": 1800,
        "thinking_budget": None,  # AUTO — model decides; high output tokens prevent starvation
    },
}

_SYSTEM_PROMPT = (
    "You are BakeManage AI, an embedded ERP assistant for an Indian bakery. "
    "You receive live operational data from the BakeManage platform and respond "
    "with concise, actionable insights. Always be specific. Use ₹ for currency. "
    "Format: bullet points unless a table is explicitly requested. "
    "Never hallucinate numbers — use only the data provided."
)


def _model() -> str:
    return settings.gemini_model or "gemini-3-flash-preview"


# ---------------------------------------------------------------------------
# Client — lazy singleton
# ---------------------------------------------------------------------------

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file and restart the API container."
        )
    try:
        from google import genai  # noqa: PLC0415

        _client = genai.Client(api_key=settings.gemini_api_key)
        logger.info("Gemini client initialised — model: %s", _model())
        return _client
    except ImportError as exc:
        raise RuntimeError(
            "google-genai SDK not installed. "
            "Add `google-genai` to requirements.txt and rebuild the image."
        ) from exc


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


def ask(
    prompt: str,
    *,
    context_data: dict[str, Any] | None = None,
    complexity: QueryComplexity | None = None,
) -> dict[str, Any]:
    """
    Send a prompt (with optional structured context) to Gemini and return:
      {
        "text": <model response>,
        "model": "gemini-3-flash-preview",
        "complexity": "operational|insight|analytical",
        "thinking_budget": 0 | None,
        "tokens": {"prompt": N, "response": N, "thoughts": N, "total": N},
      }

    Raises RuntimeError if GEMINI_API_KEY is not configured or SDK is missing.
    Raises google.genai.errors.APIError on upstream failures.
    """
    client = _get_client()

    if complexity is None:
        complexity = detect_complexity(prompt)

    cfg_raw = _CONFIGS[complexity]

    # Attach context data as a structured JSON block if provided
    full_prompt = f"{_SYSTEM_PROMPT}\n\n"
    if context_data:
        import json

        full_prompt += f"Live platform data:\n```json\n{json.dumps(context_data, default=str, indent=2)}\n```\n\n"
    full_prompt += prompt

    from google.genai import types  # noqa: PLC0415

    thinking_budget = cfg_raw["thinking_budget"]
    if thinking_budget is not None:
        thinking_cfg = types.ThinkingConfig(thinking_budget=thinking_budget)
    else:
        thinking_cfg = None  # auto — model decides

    gen_config_kwargs: dict[str, Any] = {
        "max_output_tokens": cfg_raw["max_output_tokens"],
    }
    if thinking_cfg is not None:
        gen_config_kwargs["thinking_config"] = thinking_cfg

    response = client.models.generate_content(
        model=_model(),
        contents=full_prompt,
        config=types.GenerateContentConfig(**gen_config_kwargs),
    )

    usage = response.usage_metadata
    return {
        "text": response.text,
        "model": _model(),
        "complexity": complexity.value,
        "thinking_budget": thinking_budget,
        "tokens": {
            "prompt": getattr(usage, "prompt_token_count", 0),
            "response": getattr(usage, "candidates_token_count", 0),
            "thoughts": getattr(usage, "thoughts_token_count", 0),
            "total": getattr(usage, "total_token_count", 0),
        },
    }
