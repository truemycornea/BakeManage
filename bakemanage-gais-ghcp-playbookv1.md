# BakeManage AI Collaboration Playbook

This document defines how BakeManage should use **Google AI Studio / Gemini (GAIS)** and **GitHub Copilot (GHCP)** together to safely analyze, implement, review, and improve the repository through a pull-request-based workflow. Google documents that Gemini custom tools are executed by the application, not by AI Studio directly, and GitHub documents that Copilot coding agent works through repository and pull request workflows.[cite:2][cite:23]

The target operating model is: **GAIS plans and orchestrates**, **the backend executes GitHub API actions**, and **GHCP collaborates inside GitHub as coder/reviewer**. GitHub recommends GitHub Apps for long-lived integrations, while fine-grained personal access tokens can be used for early proof-of-concept work.[cite:29][cite:21]

## Objectives

The objectives of this setup are:

- Allow GAIS to read the BakeManage repository, understand code, produce plans, and propose minimal changes through declared tools executed by a secure backend.[cite:2]
- Allow GHCP to review pull requests, suggest code changes, and make or refine changes inside pull-request workflows when enabled by repository or organization policy.[cite:23]
- Keep all repository changes controlled through feature branches and pull requests, never through direct writes to the protected default branch.[cite:23]
- Ensure that secrets such as the Gemini API key and GitHub credentials are stored in backend environment variables or secret management systems, not in prompts, committed files, or browser code.[cite:4][cite:21]

## Operating model

### Tool ownership

The following responsibilities must be separated clearly:

| Component | Responsibility | Notes |
|---|---|---|
| GAIS | Planning, tool selection, implementation reasoning, PR summaries | Uses Gemini API and declared functions.[cite:2][cite:4] |
| Backend service | Executes GitHub API calls and returns results to Gemini | This is required by Gemini custom tool design.[cite:2] |
| GHCP | GitHub-native coding help, pull request review, follow-up changes | Works within GitHub workflows.[cite:23] |
| Human maintainer | Approvals, risk decisions, secret handling, final merge | Required for safe governance.[cite:23] |

### Secret placement

The following rules are mandatory:

| Secret | Store here | Never store here |
|---|---|---|
| `GEMINI_API_KEY` | Backend environment variable or secret manager | GitHub repository files, frontend code, PR comments, copied prompt text.[cite:4] |
| `GITHUB_TOKEN` or GitHub App credentials | Backend environment variable or secret manager | Google AI Studio prompt text, frontend code, committed `.env` files.[cite:21][cite:2] |

## Human tasks required

The user must perform these actions manually because neither GAIS nor GHCP should create or own sensitive credentials without human oversight:

1. Create the Gemini API key from Google AI Studio and store it in a secure password manager or secret store.[cite:4]
2. Create either a fine-grained GitHub PAT for initial testing or, preferably, a GitHub App for production use.[cite:21][cite:29]
3. Enable branch protection or rulesets so that all changes go through pull requests and review.[cite:23]
4. Enable GitHub Copilot features required by the repository or organization plan, because GitHub states coding agent availability depends on plan and admin enablement.[cite:23]
5. Install the GitHub App only on the BakeManage repository if the App path is used, because GitHub Apps support repository-scoped installation.[cite:29][cite:35]
6. Review and approve AI-generated pull requests before merge, especially for authentication, billing, CI/CD, infrastructure, data models, and production configuration changes.[cite:23]

## Delivery phases

## Phase 1 - Safe proof of concept

### Goal

Build a minimal repo-aware integration with read access first, then limited PR-based write access through a backend-controlled workflow.[cite:2][cite:21]

### Human steps

1. Confirm BakeManage repository admin access on GitHub.[cite:21]
2. Create `GEMINI_API_KEY` in Google AI Studio and save it securely.[cite:4]
3. Create a fine-grained PAT limited to the BakeManage repository for early testing, or skip directly to Phase 3 if the GitHub App will be created immediately.[cite:21][cite:29]
4. Protect the default branch and require pull requests before merge.[cite:23]
5. Create a backend project folder outside of the BakeManage frontend or application runtime if needed.[cite:2]

### Backend tool functions for Phase 1

Implement these tool functions first:

- `list_repo_tree`
- `get_file_content`

These functions let GAIS understand repository structure and inspect implementation files without any write capability.[cite:2]

### Expected behavior

- GAIS reads repository structure and selected files through backend tools.[cite:2]
- GAIS creates summaries, architecture notes, and change plans.[cite:2]
- GHCP can assist by generating backend code or improving repository documentation in normal GitHub workflows.[cite:23]

## Phase 2 - Controlled write workflow

### Goal

Add minimal write capability, but force every change through feature branches and draft pull requests.[cite:2][cite:23]

### Human steps

1. Review the Phase 1 behavior and confirm that only safe files are being read.
2. Expand GitHub permissions only if needed to allow branch creation and file updates.[cite:21]
3. Approve backend changes to include additional write tool functions.
4. Confirm branch protections prevent direct pushes to the default branch.[cite:23]

### Backend tool functions for Phase 2

Add these functions:

- `create_branch`
- `update_file`
- `create_pull_request`

These are the minimum safe write tools because they support PR-based change delivery without granting merge authority to the AI system.[cite:2][cite:23]

### Expected behavior

- GAIS inspects the repository first, then produces a proposed implementation plan.[cite:2]
- If approved by the human user, GAIS asks the backend to create a feature branch, update only the required files, and open a draft pull request.[cite:2]
- GHCP reviews the pull request, suggests changes, or makes targeted improvements when requested through GitHub-native workflows.[cite:23]

## Phase 3 - Production security with GitHub App

### Goal

Replace the temporary PAT with a GitHub App because GitHub recommends GitHub Apps for long-lived integrations with more secure, granular, and repository-scoped authentication.[cite:29][cite:35]

### Human steps

1. Open GitHub account or organization settings and create a new GitHub App.[cite:35]
2. Configure the App with only the BakeManage repository installation.[cite:29]
3. Set minimum repository permissions, typically metadata read, contents read/write, pull requests read/write, and issues read/write only if issue or PR comment workflows are needed.[cite:35][cite:21]
4. Generate and securely store the App private key, App ID, and installation details.[cite:35]
5. Replace the backend PAT-based authentication with GitHub App authentication.[cite:35]

### Expected behavior

- The backend generates short-lived installation tokens when it needs GitHub access.[cite:35]
- GAIS continues to use the same declared tool model, but the backend now executes GitHub actions through the App instead of a user token.[cite:2][cite:35]
- GHCP continues to operate inside GitHub PR workflows normally.[cite:23]

## Phase 4 - PR collaboration and two-way review loop

### Goal

Enable structured collaboration between GAIS and GHCP through pull requests, comments, reviews, and limited automated follow-up actions.[cite:23]

### Human steps

1. Enable GitHub Copilot coding agent if the organization or plan supports it, because GitHub documents that administrator enablement may be required.[cite:23]
2. Add repository instructions for coding style, test commands, branch naming, and PR expectations to help GHCP act consistently.[cite:23]
3. Configure GitHub webhooks or poll PR comments if the backend will react to labels or commands.[cite:35]
4. Decide which commands should trigger GAIS actions, such as `/gemini-plan`, `/gemini-fix`, or label-based workflows.

### Expected behavior

- GAIS opens or updates a PR through backend tools based on approved implementation goals.[cite:2]
- GHCP reviews the PR or is asked in comments to make targeted changes.[cite:23]
- Human reviewers add comments and approve or reject the direction.[cite:23]
- The backend may read PR comments and feed them back to GAIS for a controlled second iteration, but only with clear limits and human checkpoints.

## Guardrails

The following rules must always apply:

- Never store secrets in the repository, prompt text, or frontend code.[cite:4][cite:21]
- Never allow GAIS or GHCP to push directly to the protected default branch.[cite:23]
- Never allow automatic merge for risky changes without human approval.
- Always limit repository permissions to the minimum needed.[cite:21][cite:29]
- Treat these areas as high risk and require explicit human approval before changes: authentication, authorization, payments, secrets, CI/CD, infrastructure, billing, production environment variables, data migrations, and security controls.
- Limit automated revision loops so that GAIS and GHCP cannot endlessly react to each other without a human checkpoint.

## Backend function specifications

The backend should implement the following functions and expose them to Gemini as declared tools:[cite:2]

### `list_repo_tree`

Purpose: Return folders and files for a repository path and branch so GAIS can understand structure before planning changes.

Inputs:
- `owner`
- `repo`
- `path` (optional)
- `ref` (branch or commit, optional)

Validation rules:
- `owner` and `repo` must be from an approved allowlist.
- `path` must stay within the repository.
- Reject attempts to browse hidden secret files or any disallowed paths if policy requires.

### `get_file_content`

Purpose: Return the content of a specific file so GAIS can analyze relevant code and documentation.[cite:2]

Inputs:
- `owner`
- `repo`
- `path`
- `ref` (optional)

Validation rules:
- Only text-based files should be returned inline.
- Large files should be truncated safely or summarized.
- Binary files should be rejected or handled through metadata-only responses.

### `create_branch`

Purpose: Create a safe feature branch from the protected default branch.

Inputs:
- `owner`
- `repo`
- `new_branch`
- `base_branch`

Validation rules:
- Branch names should follow a controlled prefix such as `gemini/` or `ai/`.
- Reject direct writes to `main`, `master`, or any protected branch.

### `update_file`

Purpose: Write or replace the content of one file in the feature branch.

Inputs:
- `owner`
- `repo`
- `branch`
- `path`
- `content`
- `commit_message`

Validation rules:
- Reject writes to protected branches.
- Restrict file types if needed.
- Optionally require a dry-run diff before commit.
- Always log who requested the change and which prompt caused it.

### `create_pull_request`

Purpose: Open a draft pull request for human and GHCP review.

Inputs:
- `owner`
- `repo`
- `head_branch`
- `base_branch`
- `title`
- `body`

Validation rules:
- PRs should default to draft unless explicitly approved by the human user.
- Title and body must include implementation summary, impacted files, test notes, and risk notes.

## Repository governance

The repository should contain these AI-governance files or sections:

- `docs/ai-playbook.md` or this document at the repository root
- `docs/ai-prompts.md` if prompt snippets are separated
- `docs/architecture.md` for module and system explanations
- `CONTRIBUTING.md` with branch naming, PR checklist, and review expectations
- `SECURITY.md` for secret-handling and high-risk areas

These documents help both GAIS and GHCP act consistently and reduce ambiguous decisions during implementation and review.

## Required manual configuration checklist

The user must manually complete the following items:

| Item | Manual action required | Owner |
|---|---|---|
| Gemini API key | Create and store securely | Human user/admin |
| GitHub auth | Create PAT for POC or GitHub App for production | Human user/admin |
| Backend secrets | Add all secrets to runtime environment or secret manager | Human user/admin |
| Branch protection | Require PRs and approvals | Human repo admin |
| Copilot policy | Ensure coding agent or Copilot features are enabled if needed | Human org/repo admin |
| App installation | Install GitHub App only on BakeManage | Human repo/org admin |
| Review & merge | Review AI-generated PRs and merge manually | Human maintainer |

## Prompt for GAIS

Use the following as the primary system instruction for GAIS when this repository is connected through the backend tools:

```text
You are the BakeManage implementation planner and orchestrator.

Read and follow the repository AI collaboration playbook before acting.
Your job is to understand the repository, create minimal and reversible implementation plans, and use only the declared backend tools.

You do not directly hold GitHub credentials.
You must never assume you can write directly to the protected default branch.
You must always inspect repository structure and the relevant files before proposing or making changes.

Tool policy:
1. Use list_repo_tree first to understand the repository area involved.
2. Use get_file_content to inspect the exact files relevant to the task.
3. Summarize the implementation plan before writing.
4. If approved, use create_branch for a new feature branch.
5. Use update_file only for the minimum required files.
6. Use create_pull_request to open a draft PR.
7. Never merge pull requests.

Risk policy:
- Mark authentication, authorization, billing, CI/CD, workflows, secrets, infrastructure, environment variables, and production configuration as high risk.
- For high-risk work, stop after planning unless the human explicitly approves.
- If a requested tool is missing, unavailable, or blocked by policy, say so clearly and stop.

Output policy:
- For planning tasks, return: summary, impacted files, implementation steps, risks, tests, and rollback notes.
- For write tasks, return: branch name, changed files, commit summary, PR title, PR body, reviewer checklist.
```

## Prompt for GHCP

Use the following as a Copilot Chat or Copilot coding-agent instruction prompt inside the BakeManage repository:

```text
You are the GitHub Copilot collaborator for the BakeManage repository.

Read and follow the repository AI collaboration playbook before acting.
Your job is to assist with implementation, review pull requests, make minimal safe changes, and preserve repository conventions.

Core rules:
- Never introduce secrets or hardcoded credentials.
- Never recommend direct pushes to the protected default branch.
- Prefer the smallest safe diff.
- Respect existing file structure, naming, code style, and tests.
- Highlight security, CI/CD, data model, billing, authentication, and infrastructure risks.

When reviewing a PR:
- Summarize what the PR changes.
- Identify correctness issues, regression risks, missing tests, and documentation gaps.
- Suggest the smallest safe improvement.

When implementing:
- Work in a branch or pull request workflow.
- Add or update tests where appropriate.
- Keep commit messages clear and reviewable.
- If agent execution is unavailable, explain exactly what a human user must do manually next.

If GitHub Copilot coding agent is not enabled or cannot operate automatically:
- Say that clearly.
- Explain that an administrator may need to enable the required Copilot plan or repository setting.
- Tell the user to verify organization or repository Copilot policy and supported plan.
- Continue by providing step-by-step manual instructions or patch suggestions instead of stopping silently.
```

## PR template guidance

Every AI-generated pull request should include these sections:

- Summary
- Why this change is needed
- Files changed
- Test impact
- Risks
- Rollback notes
- Reviewer checklist

This makes GAIS output reviewable and gives GHCP and human reviewers a consistent structure for collaboration.

## Suggested command patterns

These command patterns can be standardized in PR comments or issue comments:

- `/gemini-plan <task>` for GAIS planning only
- `/gemini-implement <task>` for GAIS implementation through branch + PR tools
- `@copilot review this PR for correctness and regressions` for GHCP review tasks.[cite:23]
- `@copilot address this comment with the smallest safe fix` for GHCP follow-up changes to an active PR.[cite:23]

## Success criteria

This integration is working successfully when all of the following are true:

- GAIS can inspect BakeManage safely through backend tools and produce useful implementation plans.[cite:2]
- GAIS can propose minimal code or document changes through feature branches and draft PRs only.[cite:2][cite:23]
- GHCP can review those PRs and help implement or refine changes inside GitHub workflows.[cite:23]
- Human maintainers remain in control of credentials, approvals, and merges.[cite:21][cite:23]
- The system can be upgraded from PAT-based proof of concept to GitHub App production auth without changing the high-level workflow.[cite:29][cite:35]
