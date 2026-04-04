# 📋 BakeManage — Sovereign SCRUM Register
<!-- STORY-REF: EPIC-01 | Sprint: Ares | Status: 🔶 IN PROGRESS -->
<!-- Last updated: 2026-04-04 by GHCP -->

---

## 🔁 Sync Table — GHCP Authored vs. AGAM Executed

| Story | GHCP Authored | AGAM Executed | Status | Evidence |
|---|---|---|---|---|
| STORY-001 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR: scrum-pipe-and-ai-leverage |
| STORY-002 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR: scrum-pipe-and-ai-leverage |
| STORY-003 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR: scrum-pipe-and-ai-leverage |
| STORY-004 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR: scrum-pipe-and-ai-leverage |
| STORY-005 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR: scrum-pipe-and-ai-leverage |
| STORY-006 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR: scrum-pipe-and-ai-leverage |
| STORY-007 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | PR: scrum-pipe-and-ai-leverage |
| STORY-008 | ✅ 2026-04-04 | ❌ Pending | 🔷 CODED | `infra/ansible/gap_bakemanage_001_deploy.yml` |

---

## ⚠️ Conflict Register

| ID | Description | Root Cause | Resolution Path | Status |
|---|---|---|---|---|
| — | No conflicts registered | — | — | — |

---

## 📚 EPIC Register

| Epic | Domain | Priority | Owner | Status |
|---|---|---|---|---|
| EPIC-01 | Governance & Olympus Alignment | 🔴 Critical | GHCP | 🔶 IN PROGRESS |
| EPIC-02 | Security Hardening (Secrets, Auth) | 🔴 Critical | GHCP | 🔶 IN PROGRESS |
| EPIC-03 | Observability (healthz, metrics, logs) | 🟡 High | GHCP | 🔶 IN PROGRESS |
| EPIC-04 | CI/CD Pipeline | 🟡 High | GHCP | 🔶 IN PROGRESS |
| EPIC-05 | Multimodal Ingestion (Docling/VLM) | Feature | GHCP/GAIS | 🔶 IN PROGRESS |
| EPIC-06 | FEFO Inventory & Recipe Engine | Feature | GHCP | ✅ DONE (v2.1) |
| EPIC-07 | GST Compliance & Analytics | Feature | GHCP | ✅ DONE (v2.1) |
| EPIC-08 | AGAM-Ready Deployment Artefacts | Platform | GHCP | 🔷 CODED |
| EPIC-09 | AI Interaction Protocol (GHCP↔AGAM) | Platform | GHCP | 🔶 IN PROGRESS |

---

## 📖 Sprint Breakdown

### 🔱 Sprint 1 — ARES (Foundation & Hardening)

**Status**: 🔷 CODED | **Target**: 2026-04-04 → 2026-04-18

| Story | Title | Epic | Status | Evidence Anchor |
|---|---|---|---|---|
| STORY-001 | Olympus docs scaffold | EPIC-01 | 🔷 CODED | `docs/` directory created |
| STORY-002 | Harden `.env.example` | EPIC-02 | 🔷 CODED | No guessable values |
| STORY-003 | Docker Compose: restart + network isolation | EPIC-03 | 🔷 CODED | `docker-compose.yml` |
| STORY-004 | `/healthz` + `/metrics` endpoints | EPIC-03 | 🔷 CODED | `app/main.py` |
| STORY-005 | PR template + issue templates | EPIC-01 | 🔷 CODED | `.github/` |
| STORY-006 | CI: secrets scan + healthz probe | EPIC-04 | 🔷 CODED | `.github/workflows/ci.yml` |
| STORY-007 | SSO stub middleware | EPIC-02 | 🔷 CODED | `app/main.py` SSO middleware |
| STORY-008 | AGAM-ready Ansible deploy playbook | EPIC-08 | 🔷 CODED | `infra/ansible/gap_bakemanage_001_deploy.yml` |

**Definition of Done** (Sprint Ares):
- [x] All STORY-001 to STORY-008 marked 🔷 CODED with artefacts committed
- [ ] AGAM executes artefacts → stories promoted to ✅ DONE with evidence
- [ ] `/healthz` passing in CI health check step
- [ ] Secrets scan step passing (no hardcoded credentials)

---

### 📋 Sprint 2 — HERMES (Backlog — not started)

| Story | Title | Epic | Status |
|---|---|---|---|
| STORY-009 | structlog JSON logging + correlation IDs | EPIC-03 | ❌ OPEN |
| STORY-010 | Authentik OIDC wiring (SSO_ENFORCE=true) | EPIC-02 | ❌ OPEN |
| STORY-011 | Vault secret consumption (hvac integration) | EPIC-02 | ❌ OPEN |
| STORY-012 | Prometheus scrape target registration (HomeLab) | EPIC-03 | ❌ OPEN |
| STORY-013 | Grafana dashboard for BakeManage | EPIC-03 | ❌ OPEN |

---

## 🔄 Loop Invariants (Ethos Compliance)

These must remain true at all times:

1. No PR merges without CI green
2. No secrets in any committed file (`.env.example` has placeholder values only)
3. `/healthz` endpoint exists and returns `{"status": "ok", "version": "...", "timestamp": "..."}`
4. All AGAM-executed stories have an evidence PR (`agam/evidence-YYYY-MM-DD` branch)
5. `docs/ACTION_LOG.md` updated every session
6. `docs/DAILY_STATE.md` updated at session start and end
