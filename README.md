# Turd Eye Productions

**JAIOS Module — Agentic-agnostic AI Music Monetization System**

Part of the [JenR8ed / JAIOS](https://github.com/JenR8ed) ecosystem.  
Practical playbooks + lightweight tooling for turning AI-generated music into real income.

Designed so any human or AI agent (Grok, Claude, Perplexity, Cursor, OpenHands, etc.) can operate it cleanly.

[![JAIOS Pipeline](https://github.com/JenR8ed/turd-eye-productions/actions/workflows/deploy.yml/badge.svg)](https://github.com/JenR8ed/turd-eye-productions/actions/workflows/deploy.yml)

---

## Quick Links

| File | Purpose |
|------|--------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | End-to-end architecture & implementation roadmap |
| [docs/09-software-architecture-design.md](docs/09-software-architecture-design.md) | **Formal Software Architecture & Design / Requirements (SADD)** |
| [AGENTS.md](AGENTS.md) | Start here if you are an AI agent |
| [STRUCTURE.md](STRUCTURE.md) | Full project map |
| [docs/01-quickstart.md](docs/01-quickstart.md) | Get to first dollar fast |
| [docs/06-custom-commissions.md](docs/06-custom-commissions.md) | Main profit engine |
| [docs/08-multi-agent-frameworks.md](docs/08-multi-agent-frameworks.md) | Multi-agent roles & frameworks |
| [configs/tools.json](configs/tools.json) | Current tools & costs |

---

## Core Pipeline

| Stage | What You Do | Tools | Cost (USD) |
|-------|-------------|-------|------------|
| Generate | Create tracks with commercial rights | Suno Pro (primary) | $10/mo |
| Edit | Light arrangement & cleanup | Audacity (free) | $0 |
| Distribute | Upload to DSPs | DistroKid | $25/year |
| Sell | Custom commissions | Fiverr / direct | Time only |

**Starter cost**: ~$35 first month → ~$12–15/month ongoing.

---

## Realistic Profit Paths (USD)

| Path | Content Needed | Realistic Monthly (after 2–4 mo) |
|------|----------------|----------------------------------|
| Streaming only | 80–150+ songs | $20 – $150 |
| YouTube channel | 30–60 videos | $50 – $400 |
| **Custom commissions** | 5–10 samples | **$300 – $1,500+** |
| Hybrid (recommended) | 40–60 + samples | $400 – $2,000 |

**Primary recommendation**: Focus on custom commissions first.

---

## Tooling

Both CLIs are stdlib-only and fully **headless** — every field can be passed as a flag,
so agents and CI can drive them without a terminal. Omit a flag while at an interactive
terminal and you'll be prompted for it instead.

```bash
# Rights logging
python scripts/rights_logger.py add --title "Neon Drift" --tool Suno --plan Pro \
    --commercial yes --human-edits "trimmed intro" --distributor DistroKid
python scripts/rights_logger.py list --limit 5
python scripts/rights_logger.py verify --strict   # enforce AGENTS.md release rules
python scripts/rights_logger.py export            # -> data/rights_log.md

# Cost & income tracking
python scripts/cost_tracker.py add-expense --category Suno --amount 10 --description "Pro plan"
python scripts/cost_tracker.py add-income --category Commission --amount 300 --description "Client track"
python scripts/cost_tracker.py summary
python scripts/cost_tracker.py summary --json      # machine-readable
python scripts/cost_tracker.py summary --markdown  # -> data/cost_summary.md
python scripts/cost_tracker.py list --limit 10
```

Add `--help` to any command for the full flag list. Data is written to `data/` by
default; set `TEP_DATA_DIR` to redirect it (used by the tests and CI).

```bash
# Tests (stdlib unittest, no dependencies)
python -m unittest discover -s tests
```

---

## JAIOS Publishing Pipeline

This repository follows the **Universal JAIOS Update & Sync Protocol** from [`jenr8ed-deploy-kit`](https://github.com/JenR8ed/jenr8ed-deploy-kit).

- Quality gates run on every PR: byte-compile, unit tests, headless CLI smoke test,
  stdlib-only assertion, JSON validation, and required-file checks
- Status job on `main` for visibility
- All changes go through a pull request — no direct pushes to `main`
- Notion JAIOS Command Center registration is still a manual step (no API credential wired up)
- Zero-bloat, File-System-as-Database (FSAD) principles

See [ARCHITECTURE.md](ARCHITECTURE.md) and the formal [SADD](docs/09-software-architecture-design.md) for full design,
and [`jaios.manifest.json`](jaios.manifest.json) for a per-component breakdown of what is
implemented versus documented-only.

---

## Key Rules

- Generate only on paid commercial-rights plans.
- Always disclose AI use.
- Add human editing.
- Never clone real artists’ voices.
- Log every track.

---

**Turd Eye Productions** · JAIOS Module  
Built to turn AI files into actual cash — cleanly and repeatably.
