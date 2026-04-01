# BakeManage Data Room (v1)

- **Architecture & Strategy**: see `../bakemanagerootv1.md`, `../bakemanagerootv1.5.md`, `../bakemanagerootv2.md`, `../bakemanagerootv2.5.md` for the staged GTM and platform blueprint.
- **Security & Compliance**: HTTPS enforcement, PBKDF2 + Fernet key handling, pinned dependencies, RBAC/PIN guardrails; supply-chain checks wired into Celery (`validate_requirements_locked`).
- **Operations Runbooks**: health monitoring follows Four Golden Signals with auto-remediation (cache clear/rollback) and human-notify triggers on budget impact.
- **Vertical Modules**: proofing telemetry ingestion, AI visual quality scoring, FEFO inventory with multi-vertical categories/UOM for kirana + restaurant workflows.
- **Performance Layer**: Redis caching (“Frappe Caffeine” style) for inventory/quality/proofing snapshots; Celery workers for async costing and resilience.
