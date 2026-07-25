# Architecture — Turd Eye Productions (JAIOS-Compliant)

**Purpose**: Complete scaffolding for implementing, operating, and publishing this system through the JenR8ed / JAIOS GitHub publishing pipeline.

---

## 1. System Overview

Turd Eye Productions is a **knowledge + tooling** product inside the JAIOS ecosystem.

It turns AI-generated music into repeatable profit through:
- Decision frameworks and workflows
- Lightweight Python CLIs (rights + cost tracking)
- Agentic-agnostic role definitions
- Templates for commissions and releases

It is **not** a heavy web application. Primary outputs are documentation, scripts, and data logs that any agent or human can use.

---

## 2. Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Agent / Human Interface Layer                              │
│  AGENTS.md · Role definitions · Prompt templates            │
├─────────────────────────────────────────────────────────────┤
│  Knowledge Layer                                            │
│  docs/ · playbooks/ · templates/ · decision matrices        │
├─────────────────────────────────────────────────────────────┤
│  Tooling Layer                                              │
│  scripts/rights_logger.py · scripts/cost_tracker.py         │
├─────────────────────────────────────────────────────────────┤
│  Data Layer (FSAD)                                          │
│  data/rights_log.csv · data/costs.csv                       │
├─────────────────────────────────────────────────────────────┤
│  Integration & Publishing Layer (JAIOS Pipeline)            │
│  .github/workflows/ · Notion Command Center · GitHub Pages  │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility | Key Files |
|-------|----------------|-----------|
| Interface | How agents & humans interact with the system | `AGENTS.md`, role prompts |
| Knowledge | Operational truth (workflows, risks, pricing) | `docs/`, `templates/` |
| Tooling | Executable helpers | `scripts/*.py` |
| Data | Persistent logs (File-System-as-Database) | `data/` |
| Integration | CI/CD, visibility, publishing | `.github/workflows/`, Notion |

---

## 3. Implementation Roadmap (End-to-End)

### Phase 0 — Scaffold (Done)
- [x] Core docs & decision matrices
- [x] Rights logger + cost tracker
- [x] AGENTS.md + multi-agent role design
- [x] This architecture document

### Phase 1 — Operational Readiness
- [ ] Seed initial rights_log.csv and costs.csv with headers only
- [ ] Add `requirements.txt` or confirm stdlib-only
- [ ] Create simple `Makefile` or just document CLI usage
- [ ] Add GitHub Topics + badges

### Phase 2 — JAIOS Pipeline Integration
- [ ] Add `.github/workflows/deploy.yml` (adapted for docs + Python)
- [ ] Register project in Notion JAIOS Command Center
- [ ] Optional: GitHub Pages for rendered docs
- [ ] Link from jenr8ed-deploy-kit / org showcase

### Phase 3 — Agent Runtime (Optional)
- [ ] Map roles into CrewAI or LangGraph if multi-agent orchestration is desired
- [ ] Expose scripts as tools via MCP or simple shell wrappers
- [ ] Add a thin supervisor prompt that routes tasks

### Phase 4 — Monetization Loop
- [ ] Live custom commission pipeline using the templates
- [ ] Automated weekly cost/income summary
- [ ] Feedback loop into decision matrix updates

---

## 4. JAIOS Publishing Pipeline Compliance

This repo follows the **Universal JAIOS Update & Sync Protocol** (`jenr8ed-deploy-kit`).

### Required Elements

| Element | Status | Notes |
|---------|--------|-------|
| Clear README with JAIOS context | In progress | Updated in this PR series |
| `.github/workflows/` | To be added | Adapted quality + status workflow |
| FSAD (File-System-as-Database) | Yes | `data/` CSVs |
| Zero-bloat | Yes | stdlib Python only |
| Notion Command Center entry | Manual / future sync | Project name: Turd Eye Productions |
| Reference to deploy-kit | Yes | This document + README |

### Recommended Workflow for This Repo

Because this is primarily documentation + scripts (not a Vercel app):

1. Push to `main`
2. GitHub Actions runs:
   - Python syntax check on scripts
   - Markdown lint (optional)
   - Validates `configs/tools.json`
3. Optional: Deploy docs to GitHub Pages
4. Update Notion Command Center status (manual or via deploy-kit script)

---

## 5. Data Contracts

### rights_log.csv
```
track_title, tool, plan, generation_datetime_utc, commercial_rights, human_edits, distributor, notes, logged_at_utc
```

### costs.csv
```
date_utc, type (expense|income), category, amount_usd, description, logged_at_utc
```

Scripts create these files on first use. They are the single source of truth for operational history.

---

## 6. Multi-Agent Runtime Mapping

See `docs/08-multi-agent-frameworks.md` for full details.

| Role | Primary Responsibility | Tools / Files |
|------|------------------------|---------------|
| Generator | Create tracks on commercial plans | configs/tools.json, prompt templates |
| Rights & Compliance | Log + enforce rules | scripts/rights_logger.py, AGENTS.md |
| Editor | Light human value-add | release-checklist.md |
| Sales | Custom commissions | templates/fiverr-gig.md, client-brief.md |
| Catalog | Track performance & costs | scripts/cost_tracker.py |
| Supervisor | Route + enforce decision flow | AGENTS.md |

Any framework (CrewAI, LangGraph, custom) can implement these roles by reading this repo.

---

## 7. How to Publish / Go Live

1. Ensure this architecture and the workflow file are on `main`.
2. Add the project to the Notion JAIOS Command Center with:
   - Repo: https://github.com/JenR8ed/turd-eye-productions
   - Status: Live / Scaffold Complete
   - Platform: GitHub (docs + scripts)
3. (Optional) Enable GitHub Pages from `/docs` or a generated site.
4. Reference this repo from `jenr8ed-deploy-kit` org showcase if desired.

---

**Last Updated**: 2026-07-24  
**Aligned with**: jenr8ed-deploy-kit Universal Protocol
