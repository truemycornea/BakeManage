# 📅 BakeManage — Daily State
<!-- Shared state bus between GHCP (GitHub) and AGAM (Atlas) -->
<!-- Updated at session start AND end by whichever agent is active -->

---

## Current Sprint

**Sprint**: Ares | **Status**: 🔶 IN PROGRESS | **Target close**: 2026-04-18

## Active Story

**STORY-008**: AGAM-Ready Ansible Playbook — waiting for AGAM execution

## Last GHCP Session

**Date**: 2026-04-04  
**Author**: GHCP  
**Session Summary**:
- Adopted Olympus.ai Sovereign framework (copilot-instructions.md)
- Created Sprint Ares artefacts: docs scaffold, CI workflow, PR template, issue templates
- Added `/healthz` and `/metrics` endpoints to FastAPI app
- Added Authentik SSO stub middleware (`SSO_ENFORCE=false`)
- Hardened `.env.example` (no guessable values)
- Added `restart: unless-stopped` and network isolation to `docker-compose.yml`
- Authored AGAM-ready Ansible playbook (`gap_bakemanage_001_deploy.yml`)
- Created `scripts/inject_secrets.py` (Vault-backed, env fallback)

**What is Next**:
- AGAM to execute `gap_bakemanage_001_deploy.yml` once LXC is allocated (post-May)
- Sprint Hermes: structlog JSON logging, Vault consumption, Prometheus scrape registration
- Test coverage for `/healthz` and `/metrics` endpoints

**Blockers Discovered**: None

---

## Last AGAM Session

**Date**: _(not yet active — post-May Olympus deployment)_  
**Author**: AGAM  
**Executed**: —  
**Evidence Branch**: —

---

## GHCP ↔ AGAM Interaction Protocol

```
GHCP (BakeManage GitHub Repo)
  ↓  authors artefacts (code, playbooks, configs) → pushes PR with label agam-execute
  ↓
GitHub PR merged to main
  ↓
AGAM (Atlas VS Code + GitHub Copilot CLI)
  ↓  reads docs/DAILY_STATE.md → identifies AGAM-ready artefacts
  ↓  runs: gh copilot suggest "> GHCP: scrum gap analysis"
  ↓
Vishnu MCP Hub (vishnu.olympus.ai)
  ↓  routes command to Ansible control plane (LXC 199 or Atlas)
  ↓
Ansible Playbook (infra/ansible/gap_bakemanage_NNN_*.yml)
  ↓  idempotent, Vault-backed, pre-flighted
  ↓
Docker Compose deployed on target LXC
  ↓
Evidence: AGAM commits to agam/evidence-YYYY-MM-DD branch → opens PR
  ↓
GHCP reviews evidence PR (GHCP-01) → marks story ✅ DONE in SOVEREIGN_SCRUM.md
```

### Triggering Rules

1. AGAM triggers on merge of any PR labelled `agam-execute`
2. AGAM reads this file to find the active story and AGAM-ready artefacts
3. AGAM commits evidence to `agam/evidence-YYYY-MM-DD` and opens a PR
4. If AGAM reports DONE but no evidence PR exists → GHCP classifies as ⚠️ CONFLICT C-NNN

### Atlas-Specific Setup

```bash
# On Atlas — install GitHub Copilot CLI
gh extension install github/gh-copilot

# Invoke GHCP skills from Atlas terminal
gh copilot suggest "> GHCP: scrum gap analysis"
gh copilot suggest "> GHCP: author playbook bakemanage-deploy"
gh copilot suggest "> GHCP: security audit"

# SISA commit phrase (AGAM, end of session)
git commit -m "[PROTOCOL] SISA SYNC: <session summary>"
```
