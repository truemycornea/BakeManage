## Story Reference

<!-- Required: Link to the SCRUM story this PR addresses -->
Story: `STORY-NNN` | Epic: `EPIC-NN` | Sprint: `<SprintName>`

## Summary

<!-- What does this PR do? 2–4 sentences. -->

## Changes Made

<!-- List the files/components changed and why -->

## Definition of Done Checklist

- [ ] Story/ticket reference in title (`[STORY-NNN]`)
- [ ] No secrets, API keys, or tokens in the diff
- [ ] CI is green (all tests pass)
- [ ] `/healthz` returns `{"status": "ok"}` (verified locally or via CI health step)
- [ ] Docs updated in the same PR (if behaviour changes)
- [ ] `docs/SOVEREIGN_SCRUM.md` story status updated
- [ ] `docs/ACTION_LOG.md` entry added with timestamp and evidence
- [ ] Breaking changes flagged and approved by human operator

## Evidence

<!-- Paste test output, health check response, or link to CI run -->

```
# Example: curl http://localhost:8000/healthz
{"status":"ok","version":"2.0.0","timestamp":"2026-04-04T16:57:00Z"}
```

## Security Check

- [ ] No hardcoded secrets (`(password|secret|token|key)\s*=\s*['"]\S+['"]` scan clean)
- [ ] No hardcoded IPs that should be FQDNs
- [ ] `.env.example` unchanged or uses placeholder values only

## Type of Change

<!-- Check all that apply -->
- [ ] `feat` — new feature
- [ ] `fix` — bug fix
- [ ] `docs` — documentation only
- [ ] `refactor` — code change without behaviour change
- [ ] `test` — adding or updating tests
- [ ] `chore` — build, tooling, or dependency update
- [ ] `security` — security-related change (requires 2 reviews)
- [ ] `schema` — DB schema change (requires DBA sign-off + 2 reviews)

## Merge Gate

| Change Type | Auto-merge Eligible |
|---|---|
| Documentation only | ✅ Yes (after CI) |
| Feature (non-breaking) | ✅ Yes (1 review + CI green) |
| Schema / migration | ❌ No (2 reviews + DBA sign-off) |
| Destructive operation | ❌ No (human explicit approval) |
| Security-related | ❌ No (security audit + 2 reviews) |
