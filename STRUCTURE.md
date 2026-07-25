# Project Structure — Turd Eye Productions

```
turd-eye-productions/
├── AGENTS.md                     # How any AI agent should operate this repo
├── README.md                     # Overview + core numbers
├── STRUCTURE.md                  # This file
├── LICENSE                       # MIT
│
├── scripts/                      # Executable helpers (stdlib Python)
│   ├── rights_logger.py          # Log generation rights
│   └── cost_tracker.py           # Track expenses & income
│
├── data/                         # Runtime data (created by scripts)
│   └── README.md
│
├── docs/                         # Operational guides
│   ├── 01-quickstart.md
│   ├── 02-workflow.md
│   ├── 03-decision-matrix.md
│   ├── 04-cost-profit.md
│   ├── 05-risk-mitigation.md
│   ├── 06-custom-commissions.md
│   └── 08-multi-agent-frameworks.md
│
├── templates/                    # Copy-paste assets
│   ├── fiverr-gig.md
│   ├── client-brief.md
│   ├── release-checklist.md
│   └── rights-log.md
│
├── playbooks/
│   └── daily-ops.md
│
└── configs/
    └── tools.json                # Current recommended tools & costs
```

## Design Goals
- **Agentic-agnostic**: Any LLM or agent can read and act on these files.
- **Human-readable**: Clear, imperative language.
- **Modular**: Agents and humans can load only what they need.
- **Living documentation**: Update `configs/tools.json` when prices or policies change.
- **Lightweight automation**: Scripts use only the Python standard library.
