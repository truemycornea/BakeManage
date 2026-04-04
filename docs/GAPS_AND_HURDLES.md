# 🚧 BakeManage — Gaps & Hurdles
<!-- Known blockers, gaps, and open questions -->
<!-- Updated by GHCP at session end; read by AGAM at session start -->

---

## Active Blockers

| ID | Description | Severity | Owner | Status |
|---|---|---|---|---|
| GAP-001 | Olympus LXC not yet allocated (post-May) | 🟡 HIGH | Human operator | ❌ Blocked on timeline |
| GAP-002 | Vault not yet configured for BakeManage secrets | 🟡 HIGH | AGAM (post-May) | ❌ Deferred |
| GAP-003 | NPM/AdGuard ingress not yet set up for `bakemanage.olympus.ai` | 🟡 HIGH | AGAM (post-May) | ❌ Deferred |
| GAP-004 | Authentik OIDC application not yet created | 🟡 HIGH | AGAM (post-May) | ❌ Deferred |
| GAP-005 | Prometheus scrape target not registered in HomeLab repo | 🟢 LOW | GHCP/Human | ❌ Open |
| GAP-006 | hvac library not in requirements.txt (needed for Vault consumption) | 🟢 LOW | GHCP | ❌ Open (add when Vault is live) |
| GAP-007 | structlog not in requirements.txt (needed for JSON logging) | 🟢 LOW | GHCP | ❌ Open (Sprint Hermes) |

---

## Atlas GitHub Copilot CLI — Setup & Interaction Protocol

### Installing GitHub Copilot CLI on Atlas

```bash
# 1. Install GitHub CLI
sudo apt install gh  # or brew install gh

# 2. Authenticate
gh auth login

# 3. Install Copilot CLI extension
gh extension install github/gh-copilot

# 4. Verify installation
gh copilot --version
```

### GHCP Skill Invocations from Atlas (AGAM)

```bash
# Trigger GHCP skills from Atlas terminal using gh copilot CLI
gh copilot suggest "> GHCP: scrum gap analysis"
gh copilot suggest "> GHCP: security audit"
gh copilot suggest "> GHCP: author playbook bakemanage-deploy"
gh copilot suggest "> GHCP: ethos check"
gh copilot suggest "> GHCP: obs audit"
```

### AGAM Session End — SISA Commit Protocol

```bash
# After executing AGAM-ready artefacts, commit evidence:
git checkout -b agam/evidence-$(date +%Y-%m-%d)
git add docs/ACTION_LOG.md docs/DAILY_STATE.md docs/SOVEREIGN_SCRUM.md
git commit -m "[PROTOCOL] SISA SYNC: AGAM executed <describe what was deployed>"
git push origin agam/evidence-$(date +%Y-%m-%d)
gh pr create --title "[AGAM EVIDENCE] Sprint Ares execution" --body "Evidence of AGAM execution. See ACTION_LOG.md for details."
```

---

## Open Questions

| ID | Question | Priority | Assignee |
|---|---|---|---|
| Q-001 | Which LXC ID will BakeManage be allocated? | 🟡 HIGH | Human operator |
| Q-002 | Will `diplomat.olympus.ai` replace direct Gemini API calls? | 🟢 LOW | GHCP decision |
| Q-003 | Should Celery workers and API be on the same LXC or separate? | 🟡 HIGH | Human operator |

---

## Known Technical Debt

| ID | Description | Impact | Sprint Target |
|---|---|---|---|
| TD-001 | CORS middleware uses `allow_origins=["*"]` — should be domain-scoped in production | Security | Hermes |
| TD-002 | `/health/metrics` is auth-required but public `/metrics` exposes same data without auth — intentional for Prometheus | Acceptable | — |
| TD-003 | `test_india_comprehensive.py` is excluded from CI (requires live server) — needs mock/refactor | Test coverage | Athena |
| TD-004 | `unhandled_exception_handler` has `pragma: no cover` — add integration test coverage | Test quality | Hermes |
