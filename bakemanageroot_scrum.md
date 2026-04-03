# BakeManage SCRUM Root Plan

This root document maps the strategic blueprints (`bakemanagerootv1.md`, `bakemanagerootv1.5.md`, `bakemanagerootv2.md`) into a SCRUM-ready execution plan with epics, stories, and AI-assistable steps. It cross-references the existing strategy docs and the working service described in `README.md`.

- Strategy baselines: [v1](./bakemanagerootv1.md), [v1.5](./bakemanagerootv1.5.md), [v2](./bakemanagerootv2.md)
- Implementation context: [README.md](./README.md)
- Testing entry point: `pytest` (see `pytest.ini`)

## Epics with Major/Minor Objectives and Sample Stories

| Epic | Major Objective | Minor Objectives | Sample User Stories |
| --- | --- | --- | --- |
| E1. Multimodal Ingestion | Accept and normalize PDFs/images/handwritten receipts | Simulate Docling parse; VLM JSON mapping; upload validations | “As an accounts user, I can upload a crumpled receipt and receive structured JSON so that AP is auto-filled.” |
| E2. Data Layer & FEFO Inventory | Persist invoices, inventory, recipes with FEFO-aware stock moves | UOM/category flexibility; BOM authoring; FEFO picklists | “As a storekeeper, I see the next-to-expire batch first when creating an issue note.” |
| E3. Security & Compliance | Enforce transport security and secret hygiene | TLS-only posture; Fernet for API keys; PBKDF2+SHA256 for passwords | “As an admin, credentials are stored encrypted so a DB leak does not expose secrets.” |
| E4. Performance & Resilience | Redis caching (Frappe Caffeine style) and Celery auto-remediation | Cache warming; health signals (latency/traffic/errors/saturation); rollback/clear-cache playbooks | “As an SRE, if latency spikes above threshold, a rollback playbook triggers automatically.” |
| E5. Margin Defense & Analytics | Cost roll-up and margin drop detection | Evented margin alerts; recipe scaling for demand spikes | “As an owner, I get a warning when butter price hikes push croissant margin below target.” |
| E6. Governance & VC Data Room | Maintain investor-ready /docs layout and auditability | Cap table + IP assignment references; sprint artifacts preserved | “As a VC reviewer, I can open /docs and see the roadmap, risks, and financial guardrails.” |

## Sprinting Model (SCRUM)

- **Cadence:** 2-week sprints; daily standup; sprint review/demo; retro.
- **Definitions:**
  - DoR: Story has acceptance criteria, data contracts, negative paths, and test hooks.
  - DoD: Merged, tested (`pytest`), docs updated, feature flags/config toggles documented.
- **Backlog grooming:** Keep epic priorities E1 → E2 → E3 → E4 → E5 → E6; pull only DoR-ready stories.
- **Increment checkpoints:** Each sprint must ship at least one production-hardening item (E3/E4) plus one value item (E1/E5).

## Implementation Plan (Actions & Owners)

1) **Backlog setup**
   - Derive story cards per epic from the table above; include acceptance criteria and test notes.
   - Link stories back to this file and the relevant strategy doc (v2 preferred for cited details).

2) **Architecture and scaffolding**
   - Keep FastAPI/Celery/SQLAlchemy/Redis baseline (see `README.md`).
   - Align DB schemas to FEFO/BOM flexibility; keep cache layer abstraction to allow Redis toggles.

3) **Execution lanes**
   - **AI lane (GAIS)**: Generate stubs/tests from prompts (see below); propose data contracts.
   - **Copilot lane (GHCP)**: Inline code completions tied to active stories; avoid schema drift.
   - **Human lane**: Code review, threat modeling, perf and SRE playbook verification.

4) **Quality gates**
   - Unit/integration: `pytest` (see `tests/test_ingestion.py`, `tests/test_costing.py`).
   - Security: verify TLS enforcement, Fernet key handling, PBKDF2 password hashing remain intact.
   - Resilience: simulate cache flush/rollback playbooks in Celery tasks where applicable.

5) **Release and observability**
   - Tag increments per sprint; record release notes linking to epics/stories.
   - Track Four Golden Signals; store anomaly thresholds alongside remediation steps.

## AI Execution Prompts (GAIS & GHCP)

Use these anchored prompts to keep AI outputs consistent with the backlog and strategy docs.

- **GAIS (e.g., external LLM or orchestration agent)**
  - System context: “You are implementing BakeManage per `bakemanagerootv2.md` and `bakemanageroot_scrum.md`. Keep FastAPI/Celery/SQLAlchemy/Redis stack. Enforce TLS-only, Fernet for API keys, PBKDF2+SHA256 for passwords. Target FEFO inventory and Docling+VLM ingestion.”
  - Task pattern: “Generate code/tests for [Story ID] under Epic [E#]. Acceptance criteria: [...]. Touch only relevant modules. Add/adjust pytest cases. Summarize changes and commands to run `pytest`.”

- **GHCP (GitHub Copilot)**
  - Inline hint: “Copilot, implement [Story ID] for BakeManage. See `bakemanagerootv2.md` for domain rules and `bakemanageroot_scrum.md` for DoD. Respect existing API shapes and SQLAlchemy models.”
  - Use comment headers in code changes only when matching existing style; avoid new global patterns.

## Cross-References

- Strategy narrative and citations: [bakemanagerootv2.md](./bakemanagerootv2.md)
- Architecture/services overview: [README.md](./README.md)
- Tests to extend: [tests/test_ingestion.py](./tests/test_ingestion.py), [tests/test_costing.py](./tests/test_costing.py)
- Future data room structure: `/docs` (as defined in v2 “VC Data Room” section)
