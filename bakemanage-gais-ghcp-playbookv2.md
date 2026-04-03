# BakeManage GAIS + GHCP Implementation Playbook

This document is the operating manual for using **Google AI Studio / Gemini (GAIS)** and **GitHub Copilot (GHCP)** together on the **BakeManage** repository. It is intended to be committed into the repository so both humans and AI assistants can use the same rules, workflow, prompts, and execution model. Google documents that Gemini custom tools are executed by the application, not by AI Studio directly, and GitHub documents that Copilot coding agent operates inside repository and pull-request workflows.[cite:2][cite:23]

The core principle is simple: **GAIS plans and orchestrates, the backend executes GitHub API actions, GHCP collaborates inside GitHub, and the human user remains the final approver for credentials, permissions, and merges**.[cite:2][cite:23][cite:29]

## Purpose

The purpose of this playbook is to achieve these BakeManage objectives in a controlled way:

- Let GAIS read and understand the BakeManage repository through backend-executed tools.[cite:2]
- Let GAIS propose or implement minimal changes through feature branches and draft pull requests only.[cite:2][cite:23]
- Let GHCP collaborate as coder and reviewer within GitHub pull request workflows.[cite:23]
- Minimize manual user work by using automation first where GAIS or GHCP can safely do the work.[cite:2][cite:23]
- Clearly identify the exact user steps that must still be done manually, especially around secrets, permissions, and approval gates.[cite:4][cite:21][cite:29]

## Decision rules

Use these rules throughout the project:

1. If GAIS can safely reason, plan, summarize, or call an already-implemented backend tool, let GAIS do it first.[cite:2]
2. If GHCP can safely generate code, refine code, review code, or operate in a pull request workflow, let GHCP do it first inside GitHub.[cite:23]
3. If a task involves secrets, account settings, billing, organization policy, repository permissions, protected branches, or app installation, the user must do it manually.[cite:21][cite:29]
4. If a task changes authentication, authorization, production configuration, CI/CD, or infrastructure, require human approval before implementation.[cite:23][cite:29]
5. Never put secrets into prompts, repository files, pull request comments, or browser code.[cite:4][cite:21]

## Who does what

| Actor | Primary role | What this actor should do first |
|---|---|---|
| User | Credentials, repository settings, approvals, app install, final merge | Perform only the minimum steps that cannot be automated safely.[cite:21][cite:29] |
| GAIS | Planning, repo understanding, implementation orchestration via backend tools | Read this playbook, inspect repo, produce plans, call declared tools only.[cite:2] |
| GHCP | Backend code generation, code review, PR fixes, GitHub-native collaboration | Use repository workflows and improve implementation or review output.[cite:23] |
| Backend service | Actual execution layer for GitHub API calls | Receive tool calls from GAIS and safely perform them.[cite:2] |

## Secret handling policy

These locations are mandatory:

| Secret | Correct location | Forbidden location |
|---|---|---|
| `GEMINI_API_KEY` | Backend environment variable or secret manager | GitHub repo, committed `.env`, frontend code, PR comments, prompt text.[cite:4] |
| `GITHUB_TOKEN` | Backend environment variable or secret manager for prototype only | AI Studio prompt text, repo files, browser code.[cite:21][cite:2] |
| `GITHUB_APP_PRIVATE_KEY` | Backend environment variable or secret manager for production | GitHub repo, prompt text, frontend code.[cite:35] |
| `GITHUB_APP_ID` / installation info | Backend environment variable or secret manager | Prompt text or committed secret files.[cite:35] |

## High-level rollout

This rollout is the standard path:

1. User creates the minimum required credentials manually.[cite:4][cite:21]
2. GHCP helps generate the backend tool implementation code in the repository.[cite:23]
3. GAIS uses the implemented tools to inspect and plan changes.[cite:2]
4. GAIS uses write tools only after approval and only through feature branches and draft PRs.[cite:2][cite:23]
5. GHCP reviews or improves PRs inside GitHub.[cite:23]
6. User approves and merges manually.[cite:23]

---

# Phase 1 - Foundational setup

## Concept and purpose

Phase 1 establishes the minimum secure foundation so GAIS can later understand BakeManage and GHCP can later collaborate on backend and repository work. The purpose is to complete the smallest number of manual steps first, then let AI do as much as possible after that.[cite:2][cite:23]

## Step 1 - User creates Gemini API key

### Who performs this step

**User manually**.[cite:4]

### Why this step exists

GAIS needs a Gemini API key so the backend can call Gemini. Google documents API key creation and recommends secure server-side handling of the Gemini API key.[cite:4]

### Step in detail

1. Open a browser.
2. Go to `https://aistudio.google.com` or the current Google AI Studio page for Gemini access.[cite:4]
3. Sign in with the Google account that will own the Gemini usage.
4. In Google AI Studio, find **Get API key**.
5. Click **Get API key**.[cite:4]
6. Click **Create API key**.[cite:4]
7. If prompted to select a Google Cloud project:
   - Choose an existing project if one already exists for BakeManage, or
   - Create a new project named something like `bakemanage-gemini-dev`.
8. Copy the generated key immediately.
9. Store it in a password manager or secure note.
10. Label it clearly, for example: `BakeManage GEMINI_API_KEY DEV`.
11. Do **not** paste it into the GitHub repository, AI prompts, or frontend code.[cite:4]

### Output of this step

The user now has a Gemini API key stored securely and ready to be added to the backend runtime.

### Prompt for GAIS after Step 1

Use this prompt only after the backend is available to store and use the key:

```text
The Gemini API key has been created and stored securely outside the repository.
Use this playbook as the operating policy.
Do not request the raw key value in prompts or comments.
Proceed by planning the minimal backend architecture needed for BakeManage GitHub integration.
```

## Step 2 - User creates GitHub authentication for prototype or production

### Who performs this step

**User manually**.[cite:21][cite:29]

### Why this step exists

The backend must authenticate to GitHub to read files, create branches, update files, and open pull requests. GitHub supports fine-grained PATs for limited prototype work and recommends GitHub Apps for long-lived integrations.[cite:21][cite:29]

### Choose one path

- **Path A - Prototype**: fine-grained PAT.[cite:21]
- **Path B - Production**: GitHub App.[cite:29][cite:35]

## Step 2A - Fine-grained PAT for prototype

### Step in detail

1. Open `https://github.com`.
2. Sign in to the account that has admin or owner access to BakeManage.
3. In the upper-right corner, click your **profile picture**.[cite:21]
4. In the dropdown menu, click **Settings**.[cite:21]
5. In the left sidebar, scroll down and click **Developer settings**.[cite:21]
6. In the Developer settings sidebar, click **Personal access tokens**.
7. Click **Fine-grained tokens**.[cite:21]
8. Click **Generate new token**.[cite:21]
9. In **Token name**, type:
   - `BakeManage Gemini Prototype`
10. If there is a description or note field, type:
   - `Fine-grained token for BakeManage GAIS backend proof of concept`
11. In **Expiration**, choose:
   - `30 days` for a short prototype, or
   - `90 days` if needed.
12. In **Resource owner**, select the owner of the BakeManage repository.[cite:21]
13. If GitHub asks for a justification, type:
   - `Repository-scoped token for AI-assisted BakeManage backend integration using PR-only workflow`
14. Under **Repository access**, select:
   - **Only select repositories**.[cite:21]
15. Select the `BakeManage` repository only.[cite:21]
16. Under repository permissions, set at minimum:
   - **Metadata** → `Read-only`
   - **Contents** → `Read and write`
   - **Pull requests** → `Read and write`
   - **Issues** → `Read and write` only if issue comments or PR comment workflows are required.[cite:21]
17. Scroll down and click **Generate token**.[cite:21]
18. Copy the token immediately.
19. Store it securely in a password manager or secret note.
20. Label it clearly, for example: `BakeManage GITHUB_TOKEN PROTOTYPE`.
21. Do **not** paste it into AI Studio prompt text or commit it into the repo.[cite:21][cite:2]

### Output of this step

The user now has a repository-scoped prototype token for the backend.

### Prompt for GHCP after Step 2A

```text
Assume a secure backend environment variable named GITHUB_TOKEN will be provided outside the repository.
Do not request or print the token value.
Generate backend code for BakeManage that reads GITHUB_TOKEN from environment variables only.
Prepare the code so it can later be migrated to GitHub App auth.
```

## Step 2B - GitHub App for production

### Step in detail

1. Open `https://github.com`.
2. Sign in with a user that can create a GitHub App under the personal account or organization that owns BakeManage.[cite:73]
3. In the upper-right corner, click your **profile picture**.
4. Choose one of these paths:
   - For a personal account app: click **Settings**.[cite:73]
   - For an organization app: click **Your organizations**, then find the organization, then click **Settings** next to it.[cite:73][cite:78]
5. In the left sidebar, click **Developer settings**.[cite:73]
6. In the left sidebar, click **GitHub Apps**.[cite:73]
7. Click **New GitHub App**.[cite:73]
8. Under **GitHub App name**, type a short unique name, for example:
   - `BakeManage Gemini Integrator`
   GitHub states the name must be unique and no longer than 34 characters.[cite:73]
9. Under **Homepage URL**, enter your backend URL, for example:
   - `https://bakemanage-gemini.example.com`
10. Under **Description**, type:
   - `Backend integration for GAIS and GHCP collaboration on the BakeManage repository`
11. Under **Webhook URL**, if webhooks will be used later, enter a URL such as:
   - `https://bakemanage-gemini.example.com/webhooks/github`
12. Under **Webhook secret**, enter a long random secret and store it securely.
13. Under **Repository permissions**, set:
   - **Metadata** → `Read-only`
   - **Contents** → `Read & write`
   - **Pull requests** → `Read & write`
   - **Issues** → `Read & write` only if comment-driven workflows are needed.[cite:78]
14. Under **Subscribe to events**, select later-needed events such as:
   - `Pull request`
   - `Issue comment`
   - `Pull request review comment`
15. Under **Where can this GitHub App be installed?**, choose the narrowest applicable scope such as **Only on this account** if appropriate.[cite:78]
16. Click **Create GitHub App**.[cite:78]
17. On the App settings page, note the **App ID**.[cite:78]
18. In the **Private keys** section, click **Generate a private key**.[cite:78]
19. Save the downloaded `.pem` file securely.
20. Click **Install App**.[cite:81]
21. Click **Install** next to the correct user or organization account.[cite:81]
22. When prompted for repository selection, choose **Only select repositories**.
23. Select only `BakeManage`.
24. Complete the installation.[cite:81]
25. Store these values securely outside the repo:
   - `GITHUB_APP_ID`
   - `GITHUB_APP_PRIVATE_KEY`
   - installation details or installation ID if required by implementation.[cite:35][cite:78]

### Output of this step

The user now has production-grade GitHub authentication set up using a GitHub App installed only on BakeManage.[cite:29][cite:35]

### Prompt for GHCP after Step 2B

```text
Assume GitHub App credentials will be provided securely outside the repository as environment variables.
Do not output or request raw secret values.
Generate BakeManage backend code that authenticates with GitHub App credentials and performs repository-scoped actions only on the installed BakeManage repository.
```

## Step 3 - User enables repository protections

### Who performs this step

**User manually**.[cite:23]

### Why this step exists

All AI-generated changes must go through feature branches and pull requests. Branch protection or rulesets enforce that workflow.[cite:23][cite:76]

### Step in detail

1. Open the `BakeManage` repository in GitHub.
2. Click the **Settings** tab on the repository page. If the tab is missing, the user likely does not have sufficient admin rights.[cite:46]
3. Find the repository section that controls branch protection or rulesets.
4. Create a rule or ruleset for the default branch such as `main`.
5. Configure the rule to require pull requests before merge.[cite:76]
6. Configure the rule to require at least one approval.
7. If CI exists, require status checks before merge.
8. Prevent direct pushes to the protected branch.
9. Save the rule.

### Output of this step

The repository now forces AI and humans into a PR-based workflow.

### Prompt for GAIS after Step 3

```text
The BakeManage default branch is protected and all changes must go through pull requests.
Use this rule in every implementation plan.
Never propose or assume direct writes to the protected branch.
```

---

# Phase 2 - Backend implementation using GHCP first

## Concept and purpose

This phase creates the actual backend tool functions that GAIS will later call. Since the functions are backend code, GHCP should be used first to generate and refine the implementation inside GitHub because this is exactly the kind of repository-native development workflow GHCP is designed to assist with.[cite:23]

## Step 4 - GHCP generates the backend skeleton

### Who performs this step

- **GHCP first**, if available and enabled.[cite:23]
- **User manually** only if GHCP cannot perform the work.

### Why this step exists

GAIS cannot execute GitHub actions unless the backend tool functions exist. Google documents that Gemini custom tools must be implemented and executed by the application.[cite:2]

### Step in detail

1. Open the BakeManage repository in GitHub.
2. Open GitHub Copilot Chat or the coding-agent workflow if available.[cite:23]
3. Submit the GHCP prompt below.
4. Ask GHCP to create a backend folder, implementation files, and documentation in a feature branch.
5. If GHCP creates a PR automatically, review it.
6. If GHCP can only suggest code and not create a PR, copy the generated file plan and implement manually or with local IDE assistance.

### Prompt for GHCP for Step 4

```text
Read the repository playbook and create the backend foundation for GAIS tool execution.

Goal:
Build a secure backend service for BakeManage that will later expose these Gemini-callable tool functions:
- list_repo_tree
- get_file_content
- create_branch
- update_file
- create_pull_request

Requirements:
- Use environment variables for all secrets
- Never hardcode GEMINI_API_KEY, GITHUB_TOKEN, or GitHub App secrets
- Prefer a simple Node.js or Python backend structure
- Add input validation and basic error handling
- Prepare the implementation so the read-only tools can be used first
- Add a .env.example file with placeholder variable names only
- Add a README section describing how the backend is started

If coding agent is enabled:
- create a feature branch
- implement the initial backend skeleton
- open a draft pull request

If coding agent is not enabled:
- say so clearly
- provide file-by-file code suggestions and exact manual steps for the user
```

### If GHCP cannot do this automatically

The user should then:

1. Open a local IDE such as VS Code.
2. Clone BakeManage locally.
3. Use Copilot Chat inside the IDE with the same prompt.
4. Create the backend skeleton manually from Copilot’s suggestions.
5. Commit to a feature branch and open a draft PR.

## Step 5 - Implement Phase 1 tool functions in detail

### Who performs this step

- **GHCP first** for code generation and PR creation.[cite:23]
- **User manually** for final review and approval.
- **GAIS later** for usage, not for initial implementation.[cite:2]

### Why this step exists

These are the first safe tool functions GAIS needs in order to inspect BakeManage without changing code.[cite:2]

## Tool function 1 - `list_repo_tree`

### Purpose

Return repository folders and files for a specific path and branch so GAIS can understand project structure before any implementation work.[cite:2]

### Who implements it

**GHCP first** in backend code.

### What it should do

- Accept repository owner, repo name, path, and branch/ref.
- Call GitHub’s repository content or tree APIs through the backend.
- Return a clean list of files and directories.
- Restrict access to approved repository names only.
- Reject disallowed paths if policy requires.

### Prompt for GHCP to implement `list_repo_tree`

```text
Implement a backend function named list_repo_tree for BakeManage.

Requirements:
- Read GitHub credentials from environment variables only
- Accept owner, repo, optional path, and optional ref
- Validate that repo access is limited to BakeManage or an approved allowlist
- Return a simplified JSON response with type, path, name, and sha where available
- Add error handling for invalid paths, unauthorized access, and missing refs
- Add a small usage example in comments or README
```

### How GAIS should use it later

GAIS should call `list_repo_tree` first before reading files or proposing changes.[cite:2]

### Prompt for GAIS to use `list_repo_tree`

```text
Use list_repo_tree to inspect the relevant BakeManage repository area before making any assumptions.
Do not propose changes until the repository structure has been inspected.
```

## Tool function 2 - `get_file_content`

### Purpose

Return the contents of a specific text file so GAIS can analyze the actual implementation before planning changes.[cite:2]

### Who implements it

**GHCP first** in backend code.

### What it should do

- Accept owner, repo, path, and optional ref.
- Read text-based file content only.
- Reject binary files or large unsafe content if policy requires.
- Optionally truncate large files safely.

### Prompt for GHCP to implement `get_file_content`

```text
Implement a backend function named get_file_content for BakeManage.

Requirements:
- Read GitHub credentials from environment variables only
- Accept owner, repo, path, and optional ref
- Restrict reads to approved repositories
- Return text content and useful metadata
- Reject or handle binary files safely
- Add size limits and clear error messages for oversized content
```

### Prompt for GAIS to use `get_file_content`

```text
Use get_file_content to inspect the exact BakeManage files related to the task.
Read only the files necessary to understand the problem before proposing a solution.
```

---

# Phase 3 - Controlled write tools

## Concept and purpose

This phase gives GAIS the minimum safe write capability needed to propose changes through pull requests. The goal is not direct automation of production code, but tightly controlled feature-branch and draft-PR delivery.[cite:2][cite:23]

## Step 6 - Implement `create_branch`

### Who performs this step

- **GHCP first** for backend code generation.[cite:23]
- **User manually** for review and approval.

### Purpose

Create a feature branch for AI-generated work so protected branches remain untouched.[cite:23]

### Prompt for GHCP

```text
Implement a backend function named create_branch for BakeManage.

Requirements:
- Accept owner, repo, new_branch, and base_branch
- Reject protected branch names for new_branch
- Enforce a naming prefix such as gemini/ or ai/
- Use GitHub API through the backend only
- Return clear success and failure messages
```

### Prompt for GAIS

```text
Before any file update, use create_branch to create a new feature branch.
Use a branch name that clearly reflects the task and follows repository naming policy.
```

## Step 7 - Implement `update_file`

### Who performs this step

- **GHCP first** for backend code generation.[cite:23]
- **User manually** for review.

### Purpose

Update or create repository files only in a feature branch and only for approved changes.

### Prompt for GHCP

```text
Implement a backend function named update_file for BakeManage.

Requirements:
- Accept owner, repo, branch, path, content, and commit_message
- Reject writes to protected branches
- Validate file path and repository allowlist
- Return commit metadata on success
- Add logging and clear error handling
- Prepare for text-based code and documentation updates first
```

### Prompt for GAIS

```text
Use update_file only after the plan is approved.
Modify the minimum number of files necessary and keep changes narrowly scoped.
```

## Step 8 - Implement `create_pull_request`

### Who performs this step

- **GHCP first** for backend code generation.[cite:23]
- **User manually** for PR review and merge.

### Purpose

Open a draft pull request so GHCP and human reviewers can inspect the change before merge.[cite:23]

### Prompt for GHCP

```text
Implement a backend function named create_pull_request for BakeManage.

Requirements:
- Accept owner, repo, head_branch, base_branch, title, and body
- Default to draft pull requests when supported
- Ensure the title and body include summary, files changed, tests, risks, and rollback notes
- Return pull request URL and metadata
```

### Prompt for GAIS

```text
After changes are committed to a feature branch, use create_pull_request to open a draft PR.
Include summary, impacted files, test notes, risks, and reviewer checklist.
```

---

# Phase 4 - GHCP collaboration and review loop

## Concept and purpose

This phase formalizes how GHCP collaborates on PRs created by GAIS-backed workflows. GitHub documents that Copilot coding agent can work in the background, create pull requests, and make changes to existing pull requests when requested.[cite:23]

## Step 9 - User ensures GHCP is enabled

### Who performs this step

**User manually**, unless an organization admin must do it.[cite:23]

### Why this step exists

GHCP automation depends on GitHub plan and admin enablement. GitHub notes that organization or enterprise administrators may need to enable the coding agent policy.[cite:23]

### Step in detail

1. Open GitHub.
2. If BakeManage belongs to an organization, contact or act as the organization admin.
3. Confirm that the GitHub plan supports Copilot features needed for coding agent use.[cite:23]
4. Review organization or repository Copilot settings and enable the necessary policy if available.[cite:23]
5. Confirm that the repository has not opted out of Copilot coding agent if such a setting exists.
6. Re-open GitHub Copilot Chat or coding-agent workflow and verify the features are available.

### Prompt for GHCP if the user wants self-diagnosis guidance

```text
Check whether GitHub Copilot coding agent is available for the BakeManage repository.

If available:
- explain how to assign a task
- explain how to create or update a PR through the agent

If unavailable or you cannot confirm:
- explain the likely missing requirement such as plan or admin enablement
- tell the user what admin setting to verify
- provide the manual fallback steps instead of stopping
```

## Step 10 - Use GHCP for PR review and fixes

### Who performs this step

- **GHCP first** for review and code refinement.[cite:23]
- **User manually** for approval.

### Step in detail

1. Open a PR created from the GAIS workflow.
2. In PR comments or Copilot chat, ask GHCP to review the PR.
3. If issues are found, ask GHCP to address the specific comment or fix.
4. If GHCP can create changes automatically, review the resulting commits or PR updates.
5. If GHCP cannot make the change automatically, have it provide an exact patch plan for the user or GAIS-backed backend flow.

### Prompt for GHCP review

```text
Review this BakeManage pull request using the repository playbook.

Check for:
- correctness issues
- regression risks
- missing tests
- documentation gaps
- security, auth, CI/CD, or configuration risks

If you can make a safe targeted fix, do so in the PR workflow.
If not, provide exact file-level recommendations.
```

---

# Phase 5 - GAIS operational workflow

## Concept and purpose

This phase explains how GAIS should behave once the backend tools exist. GAIS is not the credential holder and is not the Git executor; it is the planner and tool-orchestrator.[cite:2]

## Step 11 - GAIS planning workflow

### Who performs this step

**GAIS first**, using the backend tools.[cite:2]

### Step in detail

1. Read this playbook and any architecture documentation in the repository.
2. Use `list_repo_tree` to inspect the relevant area.[cite:2]
3. Use `get_file_content` for the exact files involved.[cite:2]
4. Produce a plan with impacted files, tests, risks, and rollback notes.
5. Stop for approval if the change is high-risk or policy-restricted.

### Prompt for GAIS planning

```text
Use the BakeManage playbook and inspect the repository before planning.
First call list_repo_tree for the relevant area.
Then call get_file_content for the minimum files needed.
Then return a plan with summary, impacted files, implementation steps, tests, risks, and rollback notes.
Stop and ask for approval before any write action.
```

## Step 12 - GAIS implementation workflow

### Who performs this step

**GAIS first**, using already-implemented backend tools.[cite:2]

### Step in detail

1. Confirm approval exists for the write action.
2. Use `create_branch` to create a feature branch.
3. Use `update_file` only for the minimum approved files.
4. Use `create_pull_request` to open a draft PR.
5. Return the PR URL and a concise summary.
6. Never merge the PR.

### Prompt for GAIS implementation

```text
Approval has been granted for the planned BakeManage change.
Use the backend tools in this order:
1. create_branch
2. update_file for the minimum required files
3. create_pull_request as a draft

Return the branch name, changed files, commit summary, PR title, PR body, tests, risks, and reviewer checklist.
Do not merge the PR.
```

---

# Manual fallback paths

## If GAIS cannot perform a step

The user or GHCP should:

1. Confirm the tool exists in the backend.
2. Confirm the backend has the required secret configuration.
3. Confirm the repository permissions allow the action.
4. Ask GHCP to generate or fix the missing backend implementation.
5. Retry the GAIS step only after the backend issue is resolved.

## If GHCP cannot perform a step

The user should:

1. Ask GHCP for manual file-by-file instructions rather than automation.
2. Ask whether a GitHub plan or admin setting is missing.[cite:23]
3. Use local IDE Copilot or manual coding steps if necessary.
4. Open the PR manually and continue the workflow.

---

# Repository structure recommendation

The repository should include these files to make GAIS and GHCP more effective:

- `docs/ai-playbook.md` or this file
- `docs/architecture.md`
- `docs/ai-prompts.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `.env.example` with placeholders only, never real secrets

---

# Master prompt for GAIS

```text
You are the BakeManage implementation planner and orchestrator.

Read and follow the repository AI collaboration playbook before acting.
You do not directly hold GitHub credentials.
You may only use declared backend tools.
You must inspect repository structure and relevant files before proposing or making changes.

Planning workflow:
1. Use list_repo_tree
2. Use get_file_content
3. Produce a plan
4. Stop for approval if the work is high-risk

Write workflow:
1. Use create_branch
2. Use update_file only for approved, minimum-scope changes
3. Use create_pull_request as a draft PR
4. Never merge

Risk workflow:
- Treat auth, secrets, payments, CI/CD, workflows, infra, production config, and data migrations as high-risk
- Require explicit approval before implementing high-risk changes

If a tool is unavailable, explain what is missing and what the user or GHCP must do next.
```

# Master prompt for GHCP

```text
You are the GitHub Copilot collaborator for the BakeManage repository.

Read and follow the repository AI collaboration playbook before acting.
Your job is to implement backend code, review pull requests, make minimal safe changes, and preserve repository conventions.

Rules:
- Never introduce secrets or hardcoded credentials
- Never recommend direct pushes to the protected default branch
- Prefer the smallest safe diff
- Highlight security, billing, auth, infrastructure, CI/CD, and configuration risks
- If automation is unavailable, provide exact manual next steps

Implementation mode:
- Generate backend functions needed by GAIS tool execution
- Use environment variables only for secrets
- Prepare code for migration from PAT to GitHub App auth

Review mode:
- Summarize the PR
- Identify correctness, regression, test, documentation, and security issues
- If possible, make the smallest safe fix in the PR workflow
- If not possible, provide file-level guidance
```

# Success criteria

The workflow is successful when:

- GAIS can inspect BakeManage through backend tools and produce reliable implementation plans.[cite:2]
- GHCP can help generate and refine backend code and review PRs within GitHub workflows.[cite:23]
- All write actions flow through feature branches and draft PRs.[cite:23]
- The user only performs the minimum manual steps needed for secrets, permissions, app installation, approvals, and merges.[cite:21][cite:29]
- The system can move from prototype PAT auth to production GitHub App auth without changing the overall operating model.[cite:29][cite:35]
