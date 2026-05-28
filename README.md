
<p align="center">
  <h1 align="center">SecureAgent AI</h1>
  <p align="center"><em>Autonomous DevSecOps — scan, prioritize, patch, and PR</em></p>

</p>

![Agenthon](https://img.shields.io/badge/Agenthon-Entry-brightgreen)

# SecureAgent AI

*Autonomous DevSecOps — scan, prioritize, patch, and PR*

A short description of the project: what it does and why it matters.

## Features
- Brief list of primary features or capabilities.

## Agentic AI Workflow
This project uses an agentic (multi-agent) orchestration pattern where specialized agents collaborate under a central orchestrator to perform detection, enrichment, prioritization, and remediation.

```mermaid
flowchart LR
  Trigger[User / CI Trigger] --> Orchestrator[Orchestrator]
  Orchestrator --> Scanner[Scanner Agent]
  Orchestrator --> ThreatIntel[Threat Intelligence Agent]
  Orchestrator --> Prioritizer[Risk Prioritization Agent]
  Orchestrator --> Fixer[Fix Recommendation Agent]
  Fixer --> PatchGen[Patch Generation Agent]
  PatchGen --> GitHub[GitHub / Remote Repo]
  Orchestrator --> Vector[Vector DB (Chroma)]
  Orchestrator --> LLM[LLM Provider (Gemini/OpenAI) or Mock]
  Orchestrator --> DB[(Database)]
```

- Trigger: a scan is initiated via the UI, API, or CI hook.
- Clone & Scan: `Scanner Agent` clones the repository and runs SAST tools (semgrep, bandit, gitleaks) or the fallback scanner.
- Enrich: `Threat Intelligence Agent` maps findings to CVEs/CVSS and annotates exploitability.
- Debate & Prioritize: `Risk Prioritization Agent` aggregates scanner severity and intel to assign final priority with reasoning recorded in the audit log.
- Remediate: `Fix Recommendation Agent` generates deterministic fixes via LLMs when available or uses rule-based templates as fallback.
- Patch & PR: `Patch Generation Agent` applies fixes to a branch and automatically opens a PR with rationale and links to evidence.

## Workflow steps

1. Trigger: a scan is initiated via the UI, API, or CI hook.
2. Clone & Scan: `Scanner Agent` clones the repository and runs SAST tools (semgrep, bandit, gitleaks) or the fallback scanner.
3. Enrich: `Threat Intelligence Agent` maps findings to CVEs/CVSS and annotates exploitability.
4. Debate & Prioritize: `Risk Prioritization Agent` aggregates scanner severity and intel to assign final priority with reasoning recorded in the audit log.
5. Remediate: `Fix Recommendation Agent` generates deterministic fixes via LLMs when available or uses rule-based templates as fallback.
6. Patch & PR: `Patch Generation Agent` applies fixes to a branch and automatically opens a PR with rationale and links to evidence.
- Trigger: a scan is initiated via the UI, API, or CI hook.
- Clone & Scan: `Scanner Agent` clones the repository and runs SAST tools (semgrep, bandit, gitleaks) or the fallback scanner.
- Enrich: `Threat Intelligence Agent` maps findings to CVEs/CVSS and annotates exploitability.
- Debate & Prioritize: `Risk Prioritization Agent` aggregates scanner severity and intel to assign final priority with reasoning recorded in the audit log.
- Remediate: `Fix Recommendation Agent` generates deterministic fixes via LLMs when available or uses rule-based templates as fallback.
- Patch & PR: `Patch Generation Agent` applies fixes to a branch and automatically opens a PR with rationale and links to evidence.


## Why agentic design

- Separation of concerns: agents are small, testable components focused on single responsibilities.
- Explainability: each agent writes structured logs that form an audit trail for judges and reviewers.
- Robustness: LLM calls are optional—fallbacks ensure demonstrations run reliably in offline environments.


## Requirements
- List of system requirements (Python version, Node, Docker, etc.).

## Installation
1. Clone the repository:

```bash
git clone <repository-url>
cd <repo-folder>
```

2. (Optional) Run with Docker Compose (recommended for complete stack):

```bash
docker-compose up --build
```

3. To run backend locally:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. To run frontend locally:

```bash
cd frontend
npm install
npm run dev
```

## Usage
- Describe common usage patterns, API endpoints, or how to trigger main flows.

## Configuration
- Environment variables and config files to set (e.g., `.env`, `DATABASE_URL`, API keys).

## Contributing
- Short guide: fork, branch, open PR. Include coding standards if any.

## License
- State the license or indicate if not specified.

## Contact
- Project owner and contact information.
