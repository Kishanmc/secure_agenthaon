# SecureAgent AI — Agenthon Hackathon Entry

> Autonomous, end-to-end AI-driven DevSecOps platform that finds, prioritizes, and fixes application vulnerabilities — automatically.

Overview
--------
SecureAgent AI is an integrated multi-agent security platform built to demonstrate autonomous DevSecOps workflows for the Agenthon hackathon. It combines static analysis, threat intelligence, risk prioritization, AI-driven patch generation, and automated pull-request creation into a single pipeline so applications are scanned, triaged, and remediated with minimal human effort.

Why this wins
-------------
- End-to-end autonomy: clones repos, runs SAST, enriches findings, debates risk, and opens PRs.
- Actionable remediation: generated secure patches (LLM-driven or rule-based fallback) and automated PR creation.
- Explainability & traceability: every step is logged by agents into a queryable audit trail.
- Practical fallback design: works offline (mock AI) and with real LLMs (Gemini/OpenAI) when API keys are supplied.
- RAG-enabled Security Mentor: in-app assistant answers developer security questions using local vectors.

Key Features
------------
- Scanner orchestration (Semgrep / Bandit / Gitleaks) with AI/regex fallback
- Threat intelligence mapping (CVE/CVSS) and exploit availability estimation
- Agent debate for risk prioritization and business-impact reasoning
- Automated patch branch creation, commit, push, and GitHub PR generation
- Persistent vector store (Chroma) for RAG-driven mentoring and contextual answers

Architecture (high level)
------------------------
```mermaid
flowchart TD
  A[Trigger scan (API/UI)] --> B[Orchestrator]
  B --> C{Git Service}
  B --> D[Scanner Service]
  D --> E[Findings]
  E --> F[Threat Intelligence]
  E --> G[Risk Prioritization & Debate]
  G --> H[Fix Recommendation (LLM / Fallback)]
  H --> I[Patch Generation -> GitHub PR]
  I --> J[Reporting & Agent Logs]
  J --> K[Frontend Dashboard]
  J --> L[Vector DB for RAG]
```

Important files
---------------
- Orchestrator & core workflow: [backend/app/agents/orchestrator.py](backend/app/agents/orchestrator.py#L1)
- Scanner logic & SAST wrappers: [backend/app/services/scanner_service.py](backend/app/services/scanner_service.py#L1)
- Scan endpoints & trigger: [backend/app/routers/scans.py](backend/app/routers/scans.py#L1)
- Backend entrypoint: [backend/app/main.py](backend/app/main.py#L1)
- Docker compose for full-stack run: [docker-compose.yml](docker-compose.yml#L1)
- Frontend (Vite + React): [frontend/package.json](frontend/package.json#L1)

Quickstart (recommended: Docker Compose)
---------------------------------------
1. Build and run the full stack (Postgres + Chroma + Backend + Frontend):

```bash
docker-compose up --build
```

2. Backend only (dev):

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate    # on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Frontend (dev):

```bash
cd frontend
npm install
npm run dev
```

API highlights
--------------
- Trigger a scan (background task): POST `/api/scans/trigger/{repo_id}` (see router at [backend/app/routers/scans.py](backend/app/routers/scans.py#L1))
- Get scan logs (progress): GET `/api/scans/{scan_id}/logs`

Configuration
-------------
- Configure AI provider and API keys via environment variables or `.env`:
  - `AI_PROVIDER` = `mock` | `gemini` | `openai`
  - `GEMINI_API_KEY`, `OPENAI_API_KEY` when using real LLMs
- DB: `DATABASE_URL` defaults to SQLite but docker compose config uses Postgres.

How it works (concise)
----------------------
1. A scan is created (API/UI). The `Orchestrator` runs as a background job and logs each step.
2. The `GitService` clones the target repo into `data/clones/`.
3. `ScannerService` runs available SAST tools; if none are found it runs regex/AI fallback and inserts demo findings.
4. Findings are saved as `Vulnerability` records; `Threat Intelligence` enriches with CVE/CVSS.
5. Agents perform a short debate to determine final priority and business impact.
6. `Fix Recommendation Agent` asks the LLM (Gemini/OpenAI) for remediation or uses rule-based templates.
7. `Patch Generation Agent` can create a branch, apply the fix, commit, push, and open a GitHub PR.
8. `Reporting Agent` compiles metrics and completes the audit trail.

Winning pitch (elevator)
------------------------
SecureAgent AI demonstrates how autonomous agents can reduce time-to-remediation by automating the full triage → fix → PR loop while preserving human oversight via concise reports and PRs. For Agenthon judges: this project blends practical security tooling, explainable agent logs, and LLM-driven remediation to dramatically reduce developer toil and speed up secure delivery.

Demo suggestions for judges
--------------------------
- Show an automated scan run on one of the sample clones under `data/clones/` (e.g., `vulnerable-app`) and watch the agent logs stream to `/api/scans/{scan_id}/logs`.
- Trigger automated PR creation for a High/Critical finding and show the PR diff and commit message.
- Open the Security Mentor and ask for remediation advice (RAG + LLM) to demonstrate contextual answers.

Next steps & How you can extend
--------------------------------
- Add CI integration to auto-trigger scans on PRs.
- Add SSO and RBAC for enterprise deployments.
- Plug in additional vector sources for richer RAG context (internal KBs, infra runbooks).

Contributing
------------
We welcome improvements — submit PRs and issues. See code in `backend/app/` and frontend in `frontend/`.

License
-------
This project is provided for the Agenthon hackathon demonstration purposes. Feel free to relicense for the event; include attribution to the original authors.

Contact
-------
Project owner: Kishanmc — open to walkthroughs and live demos during Agenthon.
