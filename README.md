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
| [ARCHITECTURE.md](ARCHITECTURE.md) | **End-to-end architecture & implementation roadmap** |
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

```bash
# Rights logging
python scripts/rights_logger.py add
python scripts/rights_logger.py list
python scripts/rights_logger.py export

# Cost & income tracking
python scripts/cost_tracker.py add-expense
python scripts/cost_tracker.py add-income
python scripts/cost_tracker.py summary
```

---

## JAIOS Publishing Pipeline

This repository follows the **Universal JAIOS Update & Sync Protocol** from [`jenr8ed-deploy-kit`](https://github.com/JenR8ed/jenr8ed-deploy-kit).

- Quality gates run on every push/PR (Python syntax + JSON validation + required files)
- Status job on `main` for visibility
- Designed for registration in the Notion JAIOS Command Center
- Zero-bloat, File-System-as-Database (FSAD) principles

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full layered design and implementation phases.

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