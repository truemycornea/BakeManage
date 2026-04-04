---
name: Bug Report
about: Report a defect in BakeManage — include reproduction steps and evidence
title: "[BUG] "
labels: bug
assignees: ''
---

## Story Reference

<!-- If this bug is related to a SCRUM story, link it here -->
Story/Epic: `STORY-NNN` / `EPIC-NN` _(if known)_

## Description

<!-- Clear, concise description of the bug -->

## Steps to Reproduce

1. ...
2. ...
3. ...

## Expected Behaviour

<!-- What should happen? -->

## Actual Behaviour

<!-- What actually happens? Include error messages, status codes, stack traces -->

## Evidence

<!-- Attach logs, screenshots, or curl output -->
```
# Example
curl -sf http://localhost:8000/healthz
```

## Environment

- **Version**: `vX.Y.Z`
- **Environment**: `development` | `staging` | `production`
- **Deployment**: Local Docker | Olympus LXC | CI
- **Python version**: 
- **OS**:

## Severity

- [ ] 🔴 CRITICAL — blocking, must resolve before next story
- [ ] 🟡 HIGH — resolve within current sprint
- [ ] 🟢 LOW — nice to have, backlog

## Relevant Log Output

```
# Paste relevant log lines here (ensure no secrets included)
```
