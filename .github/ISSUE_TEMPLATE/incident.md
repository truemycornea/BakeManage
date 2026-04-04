---
name: Incident Report
about: Report a production or staging incident — follow the EMER protocol for critical outages
title: "[INCIDENT] "
labels: incident
assignees: ''
---

## Incident ID

`INC-YYYY-MM-DD-NNN`

## Severity

- [ ] P0 — Complete outage (all users affected)
- [ ] P1 — Partial outage (critical path affected)
- [ ] P2 — Degraded performance (SLO at risk)
- [ ] P3 — Minor degradation (SLO not at risk)

## Timeline

| Timestamp (UTC) | Event |
|---|---|
| YYYY-MM-DD HH:MM | Incident detected |
| YYYY-MM-DD HH:MM | On-call paged |
| YYYY-MM-DD HH:MM | Root cause identified |
| YYYY-MM-DD HH:MM | Mitigation applied |
| YYYY-MM-DD HH:MM | Incident resolved |

## Impact

<!-- Which services, users, or data were affected? -->

## Root Cause

<!-- What caused the incident? Reference `docs/WISDOM_LOG.md` if known pattern. -->

## Mitigation Applied

<!-- What was done to resolve the incident? -->

## Evidence

```
# Paste health check, log excerpts, or alert screenshots (no secrets)
curl http://localhost:8000/healthz
```

## SCRUM Impact

<!-- Did this incident create new stories or block existing ones? -->
Conflict registered: `C-NNN` _(if applicable)_
Story affected: `STORY-NNN`

## Action Items (Post-Incident)

- [ ] Add root cause to `docs/WISDOM_LOG.md`
- [ ] Create follow-up story to prevent recurrence
- [ ] Update `docs/ACTION_LOG.md` with incident record
- [ ] Update `docs/GAPS_AND_HURDLES.md` if a systemic gap was identified

## Notifications

- [ ] Human operator notified
- [ ] GHCP session opened with EMER context (if AGAM execution required)
