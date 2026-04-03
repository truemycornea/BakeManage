# BakeManage — Documentation Index

## User Guides

| Document | Description |
|---|---|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Step-by-step first-time user guide: login, ingestion, inventory, cost calculator, proofing, quality, recipes, media, health monitoring |

## Technical Reference

| Document | Description |
|---|---|
| [../README.md](../README.md) | Full technical README: architecture, API reference, RBAC, data models, test instructions, environment variables |

## Strategic Blueprints

| Document | Description |
|---|---|
| [../bakemanagerootv2.5.md](../bakemanagerootv2.5.md) | v2.5 enterprise architecture, 15-feature competitive matrix, V1-V5 roadmap, pricing strategy, VC P&L |
| [../bakemanagerootv2.md](../bakemanagerootv2.md) | v2 blueprint — persona analysis, tech stack choices, GST compliance workflow |
| [../bakemanagerootv1.5.md](../bakemanagerootv1.5.md) | v1.5 blueprint |
| [../bakemanagerootv1.md](../bakemanagerootv1.md) | v1 initial blueprint |

## Architecture Notes

- **Security**: HTTPS enforcement, PBKDF2 + Fernet, pinned dependencies, RBAC/PIN guardrails, supply-chain checks in Celery (`validate_requirements_locked`)
- **Performance**: Redis caching (Frappe Caffeine style) for inventory/quality/proofing; Celery workers for async costing
- **SRE**: Four Golden Signals monitoring with auto-remediation (cache clear / rollback) and anomaly score alerting
- **Ingestion**: Multimodal pipeline — Docling for structured docs, VLM simulation for handwritten receipts
- **Verticals**: Proofing telemetry, AI browning index, FEFO FIFO, Recipe BOM, Media library

## Platform Status (v2.1.0 — 2026-04-02)

- 19 modules implemented and tested (Phase 1 + Phase 2 hardening + Phase 3 enterprise ops + v2.1.0 add-ons)
- 97/97 tests passing (35 unit + 62 API integration)
- 5 Docker containers healthy
- 158 inventory SKUs, 13 recipes, 23 media assets, 12 loyalty customers, 12 supplier lead-time records seeded
- 3 new competitive modules: Recipe Batch Scaling, Waste Tracker, GST Calculator (CGST+SGST)
- Live at http://localhost:3001 (sandbox)

