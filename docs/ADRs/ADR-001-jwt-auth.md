# ADR-001: JWT+PIN Authentication over Authentik OIDC (Cloud-First Mode)

**Status**: ✅ Accepted  
**Date**: 2026-04-04  
**Author**: GHCP  
**Story**: STORY-007 / EPIC-02  
**Sprint**: Ares

---

## Context

BakeManage requires authentication and role-based access control (RBAC). The Olympus.ai platform
provides Authentik as the canonical SSO provider. However, BakeManage is currently in
**cloud-first development mode** — the Olympus on-prem infrastructure (Authentik, NPM, Vault) is
not yet available (expected post-May 2026).

Two options were evaluated:

1. **Authentik OIDC** — integrate directly with `auth.olympus.ai` as the IdP
2. **JWT + PIN (local)** — implement local authentication with JWT tokens and hashed PINs

## Decision

**Use JWT + PIN local authentication** for cloud-first mode. Add an **Authentik SSO stub middleware**
(`_sso_middleware` in `app/main.py`) disabled by default (`SSO_ENFORCE=false`) so the codebase is
AGAM-ready for Authentik integration when the Olympus platform is live.

## Rationale

- Authentik is not reachable in cloud-first mode (no `auth.olympus.ai` FQDN)
- JWT+PIN is already implemented, tested (97/97 tests pass), and battle-tested in v2.1.0
- The SSO stub middleware reads `X-Auth-Request-*` headers that Authentik Outpost injects via NPM
  — this means zero code changes are required when switching to Authentik
- `SSO_ENFORCE=true` activates enforcement at runtime without a code deployment

## Consequences

**Positive**:
- No external dependency on Authentik during cloud-first development
- Seamless migration path to Authentik (set `SSO_ENFORCE=true` + configure NPM + Authentik)
- All existing tests continue to pass

**Negative**:
- Local JWT+PIN auth must be maintained until Authentik migration
- PIN complexity is limited (numeric only) — mitigated by PBKDF2+SHA256 hashing

## Migration Path (Sprint Hermes / post-May)

1. Run `> GHCP: onboard service bakemanage.olympus.ai` → GHCP authors NPM + Authentik OIDC artefacts
2. AGAM executes ingress onboarding artefacts
3. Set `SSO_ENFORCE=true` in production `.env`
4. Deprecate local JWT+PIN routes (keep for internal health checks)
