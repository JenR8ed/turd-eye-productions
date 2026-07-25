# Project Structure — Turd Eye Productions

```
turd-eye-productions/
├── AGENTS.md                     # How any AI agent should operate this repo
├── ARCHITECTURE.md               # End-to-end architecture & implementation roadmap
├── README.md                     # Overview + JAIOS context
├── STRUCTURE.md                  # This file
├── LICENSE                       # MIT
├── jaios.manifest.json           # Manifest for Notion / JAIOS Command Center
│
├── .github/
│   └── workflows/
│       └── deploy.yml            # JAIOS-compliant quality + status pipeline
│
├── scripts/                      # Executable helpers (stdlib Python)
│   ├── rights_logger.py
│   └── cost_tracker.py
│
├── data/                         # Runtime data (FSAD)
│   └── README.md
│
├── docs/
│   ├── 01-quickstart.md
│   ├── 02-workflow.md
│   ├── 03-decision-matrix.md
│   ├── 04-cost-profit.md
│   ├── 05-risk-mitigation.md
│   ├── 06-custom-commissions.md
│   ├── 08-multi-agent-frameworks.md
│   └── 09-software-architecture-design.md   # Formal SADD / requirements
│
├── templates/
│   ├── fiverr-gig.md
│   ├── client-brief.md
│   ├── release-checklist.md
│   └── rights-log.md
│
├── playbooks/
│   └── daily-ops.md
│
└── configs/
    └── tools.json
```

## Design Goals
- **Agentic-agnostic**: Any LLM or agent can read and act on these files.
- **JAIOS-compliant**: Follows the Universal Update Protocol from `jenr8ed-deploy-kit`.
- **Zero-bloat**: stdlib Python only.
- **File-System-as-Database**: Operational data lives in `data/`.
- **Living documentation**: Update `configs/tools.json` and docs when reality changes.
