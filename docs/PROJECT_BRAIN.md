# 🧠 BakeManage — Project Brain
<!-- Infrastructure state, integration map, and platform reference -->
<!-- Updated by GHCP when architecture changes; reviewed by AGAM at session start -->

---

## Repository Classification

**Type**: APP-ONLY (docker-compose.yml at root, no Ansible infra scope)  
**Platform Target**: Olympus.ai (post-May on-prem) | Cloud-first (current)  
**Repo**: `https://github.com/truemycornea/BakeManage`  
**Current Version**: v2.1.0  
**Deployment FQDN** _(planned)_: `bakemanage.olympus.ai`

---

## Application Stack

| Layer | Technology | Version |
|---|---|---|
| API Framework | FastAPI | 0.135.x |
| Language | Python | 3.11 |
| Database | PostgreSQL | 16 |
| Cache/Broker | Redis | 7 |
| Task Queue | Celery | 5.x |
| AI/VLM | Google Gemini (GAIS_BM_APIK) | gemini-3-flash |
| Auth | JWT + PIN (local) → Authentik OIDC (Olympus) | — |
| Ingestion | Docling + VLM simulation | — |
| Frontend | Nginx + static SPA | alpine |

---

## Olympus Platform Integration Map

| Service | FQDN | Role | Status |
|---|---|---|---|
| SSO | `auth.olympus.ai` | Authentik OIDC provider | ❌ Not yet integrated (stub middleware in place) |
| Secrets | `vault.olympus.ai` | HashiCorp Vault KV | ❌ Deferred (env fallback active, see ADR-002) |
| Proxy | `proxy.olympus.ai` | Nginx Proxy Manager | ❌ Pending NPM onboarding artefact |
| DNS | `dns.olympus.ai` | AdGuard Home | ❌ Pending FQDN registration |
| AI Router | `diplomat.olympus.ai` | LLM routing | ❌ Deferred (direct Gemini API active) |
| AI Inference | `ai.atlas.olympus.ai` | Ollama GPU inference | ❌ Not required yet |
| Monitoring | `monitor.olympus.ai` | Prometheus scrape | ❌ Pending scrape target registration |
| Dashboards | `mlv.olympus.ai` | Grafana | ❌ Pending dashboard creation |
| Uptime | `up.olympus.ai` | Uptime Kuma `/healthz` | ❌ Pending monitor setup |
| MCP Hub | `vishnu.olympus.ai` | Vishnu AI tri-bridge | ❌ Active post-May |
| App Control | LXC 199 (App Control Plane) | Ansible execution | ❌ Active post-May |

---

## LXC Allocation (Planned)

| Service | LXC IP | Port | Status |
|---|---|---|---|
| BakeManage API | `<pending allocation>` | 8000 | ❌ Not yet allocated |
| BakeManage Frontend | same LXC | 3001 | ❌ Not yet allocated |

_Request LXC allocation from Olympus operator when ready for on-prem deployment._

---

## AGAM Interaction Points

| Artefact | Path | Status |
|---|---|---|
| Ansible deploy playbook | `infra/ansible/gap_bakemanage_001_deploy.yml` | 🔷 CODED |
| Inventory | `infra/ansible/inventory/olympus.yml` | 🔷 CODED |
| Secret injection script | `scripts/inject_secrets.py` | 🔷 CODED |

---

## Environment Variables Reference

| Variable | Required | Source | Notes |
|---|---|---|---|
| `DATABASE_URL` | ✅ | Vault / env | PostgreSQL connection string |
| `CELERY_BROKER_URL` | ✅ | env | Redis URL for Celery broker |
| `REDIS_URL` | ✅ | env | Redis URL for cache |
| `JWT_SECRET` | ✅ | Vault / GitHub Secrets | Minimum 32 chars; rotate every 90 days |
| `DEFAULT_ADMIN_PIN` | ✅ | Vault / GitHub Secrets | Numeric; inject via Vault post-May |
| `BOOTSTRAP_PIN` | CI only | GitHub Secrets | Same as DEFAULT_ADMIN_PIN in CI |
| `OLYMPUS_APP_NAME` | ✅ | env | Used for Vault path: `kv/antigravity/bakemanage/` |
| `VAULT_ADDR` | Platform | env | `https://vault.olympus.ai` when on-prem |
| `VAULT_TOKEN` | Platform | Vault agent | Injected at container start by AGAM |
| `SSO_ENFORCE` | Platform | env | `false` (dev) / `true` (Olympus with Authentik) |
| `DIPLOMAT_URL` | Platform | env | `http://diplomat.olympus.ai:8000` when routing via Diplomat |
| `GAIS_BM_APIK` | Optional | Vault / env | Gemini API key; used for VLM invoice OCR |

---

## Security State

| Check | Status | Notes |
|---|---|---|
| `.env.example` has no real values | ✅ | Placeholder values only |
| JWT_SECRET validated at startup | ✅ | RuntimeError if default in non-dev |
| Fernet key derived from JWT_SECRET | ✅ | Or explicit FERNET_KEY |
| PBKDF2+SHA256 for PIN hashing | ✅ | `security.py` |
| TLS enforcement | ✅ | `ENFORCE_HTTPS=true` in production |
| Secrets scan in CI | ✅ | `ci.yml` lint-and-security job |

---

## ADR Index

| ADR | Title | Status |
|---|---|---|
| ADR-001 | JWT+PIN auth over Authentik (cloud-first) | ✅ Accepted |
| ADR-002 | Vault consumption deferred (cloud-first mode) | ✅ Accepted |
