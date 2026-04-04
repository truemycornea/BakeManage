# 🧠 BakeManage — Wisdom Log
<!-- Known errors, root cause analyses, and remediations -->
<!-- Add entries when a new error pattern is encountered and resolved -->
<!-- Format: ## ERR-NNN: <Title> -->

---

## How to Use

1. Before debugging any error → search this file first
2. If the error is here → use the known fix
3. If not here → debug, resolve, then add an entry
4. Escalate to PPRO (Perplexity Pro) for unknown patterns needing external research

---

## ERR-001: `JWT_SECRET must be set to a strong secret in non-development environments`

**Context**: FastAPI startup fails with `ValueError` from `app/config.py`  
**Root Cause**: `ENVIRONMENT` is not `development` but `JWT_SECRET` is still the default `change-this-secret`  
**Remediation**:
1. Set `JWT_SECRET` to a strong secret: `python -c "import secrets; print(secrets.token_hex(32))"`
2. Inject via GitHub Secrets (CI) or Vault (Olympus platform)
3. Confirm `ENVIRONMENT=development` for local dev  
**Vault path**: `kv/antigravity/bakemanage/jwt_secret`

---

## ERR-002: `Dependencies must be pinned with '=='`

**Context**: App startup fails with `RuntimeError` from `app/main.py` `_ensure_requirements_locked()`  
**Root Cause**: A dependency in `requirements.txt` uses `>=` or `~=` instead of `==`  
**Remediation**:
1. Run `pip freeze > requirements.txt` to pin all dependencies
2. Audit new libraries before adding — use `==` with specific version
3. Check: `grep -v '==' requirements.txt | grep -v '^#' | grep -v '^$'`

---

## ERR-003: Docker health check fails on `/healthz` — 404 Not Found

**Context**: `docker compose up` shows `api` container unhealthy  
**Root Cause**: App was started without the latest code that includes the `/healthz` endpoint  
**Remediation**:
1. Rebuild image: `docker compose build api`
2. Restart: `docker compose up -d api`
3. Verify: `curl http://localhost:8000/healthz`

---

## ERR-004: `celery inspect ping` times out in worker health check

**Context**: Worker container shows unhealthy in `docker compose ps`  
**Root Cause**: Celery broker (Redis) is unreachable or worker hasn't fully started yet  
**Remediation**:
1. Check Redis: `docker compose exec redis redis-cli ping`
2. Check worker logs: `docker compose logs worker`
3. Increase `start_period` in docker-compose.yml worker health check if needed
4. Verify `CELERY_BROKER_URL` matches the redis service

---

## ERR-005: SSO middleware returns 401 unexpectedly

**Context**: API returns 401 on all routes after setting `SSO_ENFORCE=true`  
**Root Cause**: Authentik Outpost is not injecting `X-Auth-Request-User` headers (NPM not configured)  
**Remediation**:
1. Confirm `SSO_ENFORCE=false` in dev (env var not set or set to `false`)
2. For Olympus: run `> GHCP: onboard service bakemanage.olympus.ai` to generate NPM + Authentik OIDC artefacts
3. Verify NPM is routing correctly: `curl -I https://bakemanage.olympus.ai/healthz`
4. Check Authentik outpost logs for authentication errors
