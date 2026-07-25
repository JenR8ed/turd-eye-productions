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
│  scripts/rights_logger.py · scripts/cost_tracker.py · tests/│
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
| Tooling | Executable helpers (headless, flag-driven) | `scripts/*.py`, `tests/` |
| Data | Persistent logs (File-System-as-Database) | `data/` |
| Integration | CI/CD, visibility, publishing | `.github/workflows/`, Notion |

---

## 3. Implementation Roadmap (End-to-End)

Status legend: `[x]` shipped and verified in CI · `[~]` partially shipped · `[ ]` not started.

### Phase 0 — Scaffold (Done)
- [x] Core docs & decision matrices
- [x] Rights logger + cost tracker
- [x] AGENTS.md + multi-agent role design
- [x] This architecture document

### Phase 1 — Operational Readiness
- [x] Data files created with headers on first script use — chosen over committing empty
      CSVs so each operator starts clean (see `data/README.md`)
- [x] Confirmed stdlib-only; now **enforced** in CI, which fails if a dependency
      manifest appears
- [x] CLI usage documented in `README.md` and `AGENTS.md` (no `Makefile` needed —
      both CLIs are self-documenting via `--help`)
- [x] Both CLIs are fully headless: every field is flag-settable, no step needs a TTY
- [x] Test suite (`tests/`, stdlib `unittest`) running in CI
- [ ] Add GitHub Topics — requires repo settings access, not doable from a PR

### Phase 2 — JAIOS Pipeline Integration
- [x] `.github/workflows/deploy.yml` — quality gates (compile, tests, headless smoke
      test, stdlib-only assertion, JSON validation, required-file check) + status job
- [x] CI status badge in `README.md`
- [ ] Register project in Notion JAIOS Command Center — needs `NOTION_API_KEY` secret;
      currently a manual step
- [ ] Optional: GitHub Pages for rendered docs — requires repo settings access
- [ ] Link from jenr8ed-deploy-kit / org showcase — lives in another repo

### Phase 3 — Agent Runtime (Optional)
- [ ] Map roles into CrewAI or LangGraph if multi-agent orchestration is desired
- [ ] Expose scripts as tools via MCP or simple shell wrappers
- [ ] Add a thin supervisor prompt that routes tasks

Note: Phase 3 would introduce third-party dependencies, which conflicts with NFR-01
(stdlib-only). Adopting it is a deliberate trade-off decision, not just an
implementation task.

### Phase 4 — Monetization Loop
- [ ] Live custom commission pipeline using the templates
- [~] Automated weekly cost/income summary — `cost_tracker.py summary --markdown`
      and `--json` generate the report; scheduling it (cron / `schedule:` workflow)
      is not wired up, since committing operational data back to the repo is an
      FSAD policy decision for the operator
- [x] Rights compliance is machine-checkable — `rights_logger.py verify --strict`
      enforces the commercial-rights and human-edit rules from AGENTS.md
- [ ] Feedback loop into decision matrix updates

---

## 4. JAIOS Publishing Pipeline Compliance

This repo follows the **Universal JAIOS Update & Sync Protocol** (`jenr8ed-deploy-kit`).

### Required Elements

| Element | Status | Notes |
|---------|--------|-------|
| Clear README with JAIOS context | Yes | Overview, pipeline, tooling usage, badge |
| `.github/workflows/` | Yes | `deploy.yml` — quality gates + status job, verified passing |
| FSAD (File-System-as-Database) | Yes | `data/` CSVs, created on first use |
| Zero-bloat | Yes | stdlib Python only, asserted in CI |
| Automated tests | Yes | `tests/` — stdlib `unittest`, runs in CI |
| Notion Command Center entry | Not done | Needs `NOTION_API_KEY`; manual step for now |
| Reference to deploy-kit | Yes | This document + README |

### Recommended Workflow for This Repo

Because this is primarily documentation + scripts (not a Vercel app):

1. Open a pull request against `main` — direct pushes to `main` are not permitted
   (No Blind Pushes)
2. GitHub Actions runs the `quality` job:
   - Byte-compiles everything under `scripts/` and `tests/`
   - Runs the `unittest` suite
   - Runs a headless CLI smoke test (no TTY available, mirroring agent/CI usage)
   - Asserts no dependency manifest exists (stdlib-only, NFR-01)
   - Validates `configs/tools.json` and `jaios.manifest.json`
   - Asserts the required architecture files are present
3. Merge once green; the `status` job then reports on `main`
4. Optional: Deploy docs to GitHub Pages
5. Update Notion Command Center status (manual — no API credential is wired up)

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

Scripts create these files on first use, headers included. They are the single source of truth for operational history.

### Derived artifacts (regenerable, not source of truth)
```
data/rights_log.md     ← rights_logger.py export
data/cost_summary.md   ← cost_tracker.py summary --markdown
```

### Storage location
Defaults to `data/` next to this file. Set `TEP_DATA_DIR` to redirect it — the test
suite and CI point it at a temporary directory so they never touch real operational data.

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

**Last Updated**: 2026-07-25  
**Aligned with**: jenr8ed-deploy-kit Universal Protocol
