# BakeManage GAIS-GHCP Playbook

## Objectives
- Establish a seamless integration between Google AI Studio (GAIS) and GitHub Copilot (GHCP).
- Automate the scaffolding and deployment of backend services for the BakeManage ERP.
- Maintain a secure, full-stack architecture with clear separation of concerns.

## Phases

### Phase 1: Infrastructure Scaffolding (COMPLETED)
- **Objective:** Set up the basic full-stack environment and GitHub integration layer.
- **Tasks:**
  - [x] Convert to Full-Stack (Express + Vite).
  - [x] Install `@octokit/rest`.
  - [x] Create `githubService.ts` for backend logic.
  - [x] Create API routes for GitHub interactions.
  - [x] Update `server.ts` to host the API and serve the frontend.
  - [x] Configure environment variables in `.env.example`.
- **Status:** **SUCCESS**

### Phase 2: Playbook Definition (COMPLETED)
- **Objective:** Formally define the stages and next steps for the project.
- **Tasks:**
  - [x] Create `bakemanage-gais-ghcp-playbook.md`.
  - [x] Review objectives and phases with the user.
- **Status:** **SUCCESS**

### Phase 3: GitHub Repository Connection (COMPLETED)
- **Objective:** Connect the local scaffolding to a live GitHub repository.
- **Tasks:**
  - [x] Add "Test Connection" UI to Settings page.
  - [x] User provides `GITHUB_TOKEN`, `GITHUB_REPO_OWNER`, and `GITHUB_REPO_NAME`.
  - [x] Verify connection via `/api/github/tree` using the UI button.
- **Status:** **SUCCESS**

### Phase 3.1: Code Analysis & Planning (COMPLETED)
- **Objective:** Analyze the pulled codebase and integrate requirements into the implementation plan.
- **Status:** **SUCCESS**

### Phase 4: AI-Driven Implementation (COMPLETED)
- **Objective:** Use GAIS and GHCP to implement core ERP features and authentication.
- **Orchestration Loop:**
  1. **GAIS (Planner):** [x] Creates feature branch and proposes code changes via Draft PR.
  2. **GHCP (Coder/Reviewer):** [ ] Refines the code within GitHub, adds tests, and performs deep logic review.
  3. **User (Approver):** [ ] Performs final review and merges the PR.
- **Tasks:**
  - [x] Create `gemini/auth-integration` branch.
  - [x] Implement Local Auth logic in `app/main.py` (seeding).
  - [x] Create `scripts/bootstrap_users.py` for `rahul@olympus.ai` and `helen@olympus.ai`.
  - [x] Open Draft PR for review.
- **Status:** **SUCCESS** (Initial Implementation). PR created.

### Phase 5: Verification & Hardening (NEXT)
- **Objective:** Verify authentication flow and harden security rules.
- **Tasks:**
  - [ ] Run `scripts/bootstrap_users.py` in the environment.
  - [ ] Test login with `rahul@olympus.ai` and `helen@olympus.ai`.
  - [ ] Verify RBAC (Admin vs. Operations).
- **Status:** **PENDING**

---

## 🛡️ Collaboration Protocols (GAIS ↔ GHCP)

To prevent destructive changes and ensure seamless development across environments, the following protocols are in place:

### 1. Environment & Role Definition
*   **GAIS (The Implementer/Prototyper):** Operates in the **AI Studio Sandbox (Cloud Run)**. Responsible for rapid scaffolding, UI components, and initial feature implementation on `gemini/*` branches.
*   **GHCP (The Architect/Hardener):** Operates on the **GitHub Repository**. Responsible for production-grade logic, security hardening, unit testing, and deployment to the **Real Compute (Proxmox/LXC)** stack.

### 2. Branching & Merge Strategy
*   **Isolation:** GAIS MUST only push to branches prefixed with `gemini/`.
*   **Review Flow:** GAIS creates a **Draft PR**. GHCP reviews the PR, adds tests, and refines the logic.
*   **Final Approval:** The **User** is the final authority who merges the refined PR into `main`.

### 3. State Synchronization
*   **Pull Before Push:** GAIS always reads the latest state from `main` before initiating a implementation loop.
*   **No Direct Main Commits:** Neither AI should commit directly to `main` without a PR process.

### 4. Environment Isolation
*   **Sandbox (GAIS):** Uses Vite/Express/Cloud Run for previewing.
*   **Real Compute (GHCP/User):** Uses Proxmox/Docker/FastAPI for production testing.
*   **Truth:** The GitHub Repository is the single source of truth for both environments.

---

## Next Step: User Action Required
The infrastructure is ready. The next step is for the **User** to provide the necessary GitHub credentials in the environment settings to enable the live connection.
