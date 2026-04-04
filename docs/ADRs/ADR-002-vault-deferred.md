# ADR-002: HashiCorp Vault Secret Consumption Deferred (Cloud-First Mode)

**Status**: ✅ Accepted  
**Date**: 2026-04-04  
**Author**: GHCP  
**Story**: STORY-002 / EPIC-02  
**Sprint**: Ares

---

## Context

The Olympus.ai Sovereign framework mandates **Vault-First Secrets** (Ethos Principle #2): all
credentials must be stored in HashiCorp Vault at `vault.olympus.ai` and injected at runtime.

BakeManage currently reads secrets from environment variables (e.g., `JWT_SECRET`, `DATABASE_URL`)
set via `.env` file locally and GitHub Secrets in CI.

The Vault instance at `vault.olympus.ai` is part of the Olympus on-prem infrastructure which is
not yet available (expected post-May 2026).

## Decision

**Defer Vault consumption to post-May deployment.** In the interim:

1. Cloud-first mode: secrets injected via `.env` file (local) and GitHub Secrets (CI)
2. Author `scripts/inject_secrets.py` — Vault-backed when `VAULT_ADDR` + `VAULT_TOKEN` are set,
   falls back to environment variables otherwise
3. Add `VAULT_ADDR`, `VAULT_TOKEN`, `OLYMPUS_APP_NAME` to `.env.example` as commented stubs
4. Document Vault path convention: `kv/antigravity/bakemanage/<key>`

## Rationale

- `vault.olympus.ai` is unreachable in cloud-first development mode
- `scripts/inject_secrets.py` is AGAM-ready — it auto-detects Vault availability at runtime
- GitHub Secrets in CI provide equivalent security for non-production secrets
- The `app/config.py` `model_validator` already enforces strong JWT_SECRET in non-dev environments

## Consequences

**Positive**:
- No external dependency on Vault during cloud-first development
- `inject_secrets.py` provides a clear migration path with zero app code changes
- `.env.example` documents the Vault path convention for AGAM

**Negative**:
- Secrets are managed via GitHub Secrets and `.env` files until Vault is live
- `hvac` library (HashiCorp Vault client) is not yet in `requirements.txt` — add when Vault is live

## Vault Path Convention

```
kv/antigravity/bakemanage/jwt_secret
kv/antigravity/bakemanage/default_admin_pin
kv/antigravity/bakemanage/bootstrap_pin
kv/antigravity/bakemanage/database_url
kv/antigravity/bakemanage/fernet_key
kv/antigravity/bakemanage/gais_bm_apik
```

## Migration Path (Sprint Hermes / post-May)

1. Confirm Vault is reachable: `curl -sf https://vault.olympus.ai/v1/sys/health`
2. Create Vault secrets at paths above (AGAM via Ansible)
3. Add `hvac==<version>` to `requirements.txt`
4. Set `VAULT_ADDR` and `VAULT_TOKEN` in production `.env` (injected by AGAM at container start)
5. Run `scripts/inject_secrets.py` — it will auto-detect Vault and switch from env fallback
6. Verify with `> GHCP: security audit` — Vault layer check should pass
