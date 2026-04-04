# 🔱 SPRINT 1 — OPERATION ARES
**Status**: 🔷 CODED | **Target**: 2026-04-04 → 2026-04-18

---

## Context

Sprint Ares is the foundation sprint for BakeManage's adoption of the Olympus.ai Sovereign
development framework. The goal is to bring the repository into compliance with the 12 ethos
principles and SCRUM pipeline defined in `copilot-instructions.md`, and to author all AGAM-ready
artefacts needed for on-prem deployment post-May.

BakeManage is an **APP-ONLY repo** in **cloud-first development mode**. All infra-scope concerns
(LXC provisioning, NPM ingress, Vault management) are platform concerns handled at the Olympus level.
This sprint focuses on governance, security hardening, observability, and CI.

---

## Pre-requisites

- [x] `copilot-instructions.md` reviewed and applicability mapped
- [x] Repository type identified: APP-ONLY (docker-compose.yml, no Ansible infra)
- [x] Existing test suite passes (97/97 pytest)
- [ ] AGAM (Atlas) has GitHub Copilot CLI installed (see `docs/GAPS_AND_HURDLES.md`)

---

## Context for Executor (AGAM / Human)

- App repo: `https://github.com/truemycornea/BakeManage`
- Branch: `copilot/scrum-pipe-and-ai-leverage`
- Local dev: `docker compose up` (PostgreSQL + Redis + API + Worker + Frontend)
- Vault: not yet configured — use `.env` file with secrets from `.env.example` template
- LXC: not yet allocated — track in `docs/PROJECT_BRAIN.md`

---

## Pre-flight (for AGAM execution)

```bash
# Verify docker compose is working
docker compose up -d
curl -sf http://localhost:8000/healthz
curl -sf http://localhost:8000/metrics

# Verify CI is passing (after PR merge)
gh run list --repo truemycornea/BakeManage --limit 5
```

---

## 🔷 STORY-001: Olympus Docs Scaffold (EPIC-01)

### OBJ-GOV-001: Create sovereign docs directory structure

- **Step 1**: Create `docs/SOVEREIGN_SCRUM.md` — live SCRUM register
- **Step 2**: Create `docs/DAILY_STATE.md` — GHCP↔AGAM shared state bus
- **Step 3**: Create `docs/PROJECT_BRAIN.md` — infrastructure state and integration map
- **Step 4**: Create `docs/ACTION_LOG.md` — time-series evidence log
- **Step 5**: Create `docs/WISDOM_LOG.md` — known errors and RCAs
- **Step 6**: Create `docs/GAPS_AND_HURDLES.md` — blockers and open questions
- **Validation**: All files exist under `docs/`
- **Evidence**: Committed to `copilot/scrum-pipe-and-ai-leverage` PR

---

## 🔷 STORY-002: Harden `.env.example` (EPIC-02)

### OBJ-SEC-001: Remove guessable values from example env file

- **Step 1**: Replace `JWT_SECRET=change-this-secret` → `JWT_SECRET=<generate-with-secrets.token_hex-32>`
- **Step 2**: Replace `DEFAULT_ADMIN_PIN=123456` → `DEFAULT_ADMIN_PIN=<your-admin-pin>`
- **Step 3**: Add Olympus platform variables: `OLYMPUS_APP_NAME`, `VAULT_ADDR` (commented), `SSO_ENFORCE`
- **Validation**: `grep -E '(=\S{6,}$)' .env.example` returns no unintentional real-looking values
- **Evidence**: `.env.example` diff in PR

---

## 🔷 STORY-003: Docker Compose Hardening (EPIC-03)

### OBJ-OBS-001: Add restart policies and network isolation

- **Step 1**: Add `restart: unless-stopped` to all 5 services
- **Step 2**: Add `bakemanage_net` named network and assign all services to it
- **Step 3**: Replace Python urllib health check with `wget` on `/healthz`
- **Step 4**: Add worker health check (celery inspect ping)
- **Step 5**: Change image tag from `:sandbox` to `:${VERSION:-latest}`
- **Validation**: `docker compose config` validates without errors
- **Evidence**: `docker compose up` succeeds; `docker compose ps` shows all healthy

---

## 🔷 STORY-004: `/healthz` + `/metrics` Endpoints (EPIC-03)

### OBJ-OBS-002: Add Olympus-standard observability endpoints

- **Step 1**: Add `GET /healthz` → `{"status": "ok", "version": "...", "timestamp": "..."}`
- **Step 2**: Add `GET /metrics` → public Prometheus text format
- **Validation**: `curl http://localhost:8000/healthz` returns 200 with version and timestamp
- **Validation**: `curl http://localhost:8000/metrics` returns Prometheus text format without auth
- **Evidence**: CI health check step uses `/healthz` and passes

---

## 🔷 STORY-005: GitHub Templates (EPIC-01)

### OBJ-GOV-002: Create PR and issue templates

- **Step 1**: Create `.github/PULL_REQUEST_TEMPLATE.md` with story reference and DoD checklist
- **Step 2**: Create `.github/ISSUE_TEMPLATE/bug_report.md`
- **Step 3**: Create `.github/ISSUE_TEMPLATE/feature_request.md`
- **Step 4**: Create `.github/ISSUE_TEMPLATE/incident.md`
- **Validation**: GitHub UI shows templates on new issue/PR creation
- **Evidence**: Files present in `.github/`

---

## 🔷 STORY-006: CI Pipeline Update (EPIC-04)

### OBJ-CI-001: Add secrets scan and split CI jobs

- **Step 1**: Add `lint-and-security` job (runs before `test`): secrets regex scan + requirements pin check
- **Step 2**: Update wait-for-API step to use `/healthz` instead of `/health`
- **Step 3**: Add `OLYMPUS_APP_NAME` to CI env vars
- **Validation**: CI passes on PR; secrets scan reports PASS
- **Evidence**: GitHub Actions run green

---

## 🔷 STORY-007: Authentik SSO Stub Middleware (EPIC-02)

### OBJ-SEC-002: Author SSO middleware (AGAM-ready, disabled by default)

- **Step 1**: Add `_sso_middleware` to `app/main.py` — reads `X-Auth-Request-*` headers
- **Step 2**: Gate on `SSO_ENFORCE=false` env var (no-op in dev)
- **Step 3**: Add `SSO_ENFORCE=false` to `.env.example`
- **Validation**: All existing tests pass; SSO_ENFORCE=false means no behaviour change
- **Evidence**: `pytest tests/ -v` passes; no new test failures

---

## 🔷 STORY-008: AGAM-Ready Ansible Deploy Playbook (EPIC-08)

### OBJ-AGAM-001: Author Ansible artefacts for Olympus deployment

- **Step 1**: Create `infra/ansible/gap_bakemanage_001_deploy.yml` with pre-flight, deploy, evidence tasks
- **Step 2**: Create `infra/ansible/inventory/olympus.yml` scaffold
- **Step 3**: Create `scripts/inject_secrets.py` (Vault-backed, env fallback)
- **Validation** (AGAM): `ansible-playbook ... --check --diff` dry-run passes
- **Evidence** (AGAM): Evidence task output committed to `agam/evidence-YYYY-MM-DD` branch

---

## Out of Scope

- OPNsense firewall rules
- Proxmox LXC provisioning
- Authentik application creation (GHCP-06 — deferred to Hermes)
- NPM/AdGuard DNS ingress artefacts (deferred to Hermes)
- Prometheus scrape target registration in HomeLab repo
- structlog JSON logging (deferred to Hermes)

---

## Definition of Done

- [x] All STORY-001 to STORY-008 artefacts committed to branch
- [ ] PR merged to `main` (CI green)
- [ ] AGAM executes STORY-008 and commits evidence PR
- [ ] `docs/SOVEREIGN_SCRUM.md` stories promoted to ✅ DONE with evidence anchors
- [ ] `docs/ACTION_LOG.md` updated with AGAM execution timestamp and result

## Rollback Criteria

If the CI pipeline breaks (test failures or secrets scan false positives):
1. Revert `ci.yml` to previous version: `git revert <commit> -- .github/workflows/ci.yml`
2. Investigate false positive in secrets scan regex
3. Add exclusion pattern to scan step
4. Re-push and re-run CI
