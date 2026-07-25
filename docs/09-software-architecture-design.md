# Software Architecture & Design Document (SADD)

**Project:** Turd Eye Productions  
**Type:** Knowledge + Tooling System (JAIOS Module)  
**Version:** 1.1  
**Date:** 2026-07-25  
**Status:** Knowledge layer complete · Tooling layer implemented, tested, and CI-gated · Notion sync outstanding  
**Owner:** JenR8ed (Jennifer McKinley)  
**Related:** [ARCHITECTURE.md](../ARCHITECTURE.md) · [AGENTS.md](../AGENTS.md) · [jaios.manifest.json](../jaios.manifest.json)

---

## 1. Introduction

### 1.1 Purpose
This document defines the software requirements, architecture, and design for **Turd Eye Productions** — a system that enables humans and AI agents to monetize AI-generated music safely, repeatably, and profitably.

It serves as the authoritative design reference for implementation, maintenance, and multi-agent operation.

### 1.2 Scope
**In scope:**
- Decision frameworks and operational workflows for AI music monetization
- Rights logging and cost/income tracking tooling
- Agentic-agnostic role definitions and operating rules
- Templates for commissions, releases, and client intake
- Integration with the JAIOS publishing pipeline (GitHub Actions, Notion Command Center readiness)

**Out of scope:**
- Full DAW / audio production software
- Direct integration with Suno/Udio/DistroKid APIs (manual or browser-based use is assumed)
- Payment processing or marketplace hosting
- Heavy multi-agent runtime (optional future phase)

### 1.3 Definitions

| Term | Meaning |
|------|--------|
| FSAD | File-System-as-Database — operational data lives in versionable files |
| Commercial rights | Explicit license from the AI tool allowing monetization of output |
| DSP | Digital Service Provider (Spotify, Apple Music, etc.) |
| JAIOS | JenR8ed AI OS / agentic automation platform |
| Agent | Any AI system (Grok, Claude, Cursor, etc.) that can read and act on this repo |

---

## 2. Stakeholders & Users

| Stakeholder | Role | Needs |
|-------------|------|-------|
| Operator (JenR8ed) | Primary user | Fast path to profit, low legal risk, clear process |
| AI Agents | Autonomous or assisted operators | Clear rules, decision flows, callable tools |
| Clients | Buyers of custom music | Simple briefs, reliable delivery |
| JAIOS ecosystem | Parent platform | Compliant module, Notion-visible, pipeline-ready |

---

## 3. Functional Requirements

### 3.1 Core Capabilities

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | System shall provide a documented workflow from generation → edit → distribute → monetize | Must |
| FR-02 | System shall support logging of generation rights (tool, plan, datetime, commercial status) | Must |
| FR-03 | System shall support logging of expenses and income with summary reporting | Must |
| FR-04 | System shall provide decision criteria for choosing AI music tools | Must |
| FR-05 | System shall provide templates for client briefs, Fiverr gigs, and release checklists | Must |
| FR-06 | System shall define clear safety rules (no voice cloning, disclosure required, etc.) | Must |
| FR-07 | System shall be operable by any capable AI agent via Markdown instructions | Must |
| FR-08 | System shall integrate with JAIOS publishing pipeline (quality gates + status) | Must |
| FR-09 | System shall support multi-agent role mapping (Generator, Rights, Editor, Sales, Catalog) | Should |
| FR-10 | System shall allow export of rights log to Markdown | Should |
| FR-11 | System shall machine-verify rights entries against the release rules (commercial rights + human edits recorded) | Should |
| FR-12 | System shall emit machine-readable (JSON) and report (Markdown) financial summaries | Should |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-01 | Scripts shall use only Python standard library (zero third-party deps) | Must |
| NFR-02 | All operational knowledge shall be human- and machine-readable Markdown/JSON | Must |
| NFR-03 | Data shall persist in plain CSV files under `data/` (FSAD) | Must |
| NFR-04 | System shall remain agent-agnostic (no lock-in to a single LLM or framework) | Must |
| NFR-05 | Quality pipeline shall fail on missing core files or invalid configs | Must |
| NFR-06 | Documentation shall be sufficient for a new agent to operate without prior context | Should |
| NFR-07 | All CLIs shall be operable headlessly — every input settable by flag, no step requiring a TTY or UI. Missing required input in non-interactive mode shall exit non-zero rather than block on a prompt | Must |
| NFR-08 | CLIs shall validate input and reject malformed entries before writing to the data layer | Must |
| NFR-09 | Tooling shall be covered by automated tests executed in CI, isolated from real operational data | Must |

---

## 4. System Architecture

### 4.1 High-Level View

```
┌─────────────────────────────────────────────────────────────┐
│  Interface Layer                                            │
│  AGENTS.md · Role definitions · Human CLI                   │
├─────────────────────────────────────────────────────────────┤
│  Knowledge Layer                                            │
│  docs/ · templates/ · playbooks/ · configs/tools.json       │
├─────────────────────────────────────────────────────────────┤
│  Tooling Layer                                              │
│  rights_logger.py · cost_tracker.py                         │
├─────────────────────────────────────────────────────────────┤
│  Data Layer (FSAD)                                          │
│  data/rights_log.csv · data/costs.csv                       │
├─────────────────────────────────────────────────────────────┤
│  Integration Layer                                          │
│  GitHub Actions · jaios.manifest.json · Notion-ready        │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Component Design

| Component | Type | Responsibility | Interface |
|-----------|------|----------------|-----------|
| AGENTS.md | Spec | Operating rules & decision flow for agents | Read by any agent |
| docs/* | Knowledge | Workflows, matrices, risk, commissions | Human + agent |
| templates/* | Assets | Copy-paste ready client & release materials | Human + agent |
| rights_logger.py | CLI Tool | Append/list/verify/export generation rights | CLI flags or prompts |
| cost_tracker.py | CLI Tool | Log expenses/income + summary (text/JSON/Markdown) | CLI flags or prompts |
| tests/ | Tests | Verify CLI behaviour, validation, and exit codes | `unittest discover` |
| tools.json | Config | Current recommended tools & costs | JSON |
| deploy.yml | CI | Quality gates + status | GitHub Actions |
| jaios.manifest.json | Manifest | Registration metadata for Command Center | JSON |

Both CLIs are flag-driven so that agents and CI can invoke them without a terminal;
interactive prompting is a fallback used only when `stdin` is a TTY (NFR-07).

### 4.3 Data Design

**rights_log.csv**
```
track_title, tool, plan, generation_datetime_utc,
commercial_rights, human_edits, distributor, notes, logged_at_utc
```

**costs.csv**
```
date_utc, type (expense|income), category, amount_usd,
description, logged_at_utc
```

Both files are created on first use by their respective scripts. They are the single source of truth for operational history.

---

## 5. Agent Interaction Model

### 5.1 Decision Flow (required)

```
Goal = fast cash?
  → Yes → Custom commissions path
  → No  → Catalog + streaming/YouTube

Tool grants commercial rights on current plan?
  → No  → Switch plan/tool before generating
  → Yes → Generate, then log rights

Output is pure AI with zero human edit?
  → Yes → Add light editing before release
```

### 5.2 Recommended Roles

| Role | Responsibility |
|------|----------------|
| Generator | Create tracks on commercial plans |
| Rights & Compliance | Enforce rules + run rights logger |
| Editor | Guide/perform light human value-add |
| Sales | Handle briefs, packages, delivery |
| Catalog | Track performance & costs |
| Supervisor (optional) | Route tasks and enforce AGENTS.md |

Roles may be implemented by separate agents, separate sessions, or a single agent following the flow.

---

## 6. Deployment & Publishing Design

### 6.1 Pipeline

1. Open a pull request against `main` (direct pushes to `main` are not permitted)
2. GitHub Actions (`deploy.yml`) `quality` job:
   - Byte-compile `scripts/` and `tests/`
   - Run the `unittest` suite
   - Run a headless CLI smoke test (no TTY, mirroring agent/CI invocation)
   - Assert stdlib-only (fails if a dependency manifest appears)
   - Validate `configs/tools.json` and `jaios.manifest.json`
   - Assert required architecture files exist
3. Merge when green; `status` job then reports on `main`
4. Manual update to the Notion JAIOS Command Center — no API credential is
   provisioned, so this step is not automated

### 6.2 Constraints
- Primary platform is GitHub (knowledge + scripts), not Vercel
- No third-party runtime dependencies for core scripts
- Must remain compatible with `jenr8ed-deploy-kit` Universal Protocol

---

## 7. Constraints, Assumptions & Risks

### Assumptions
- Operator has (or will obtain) paid commercial plans on chosen AI music tools
- Distribution is performed via DistroKid or equivalent with AI disclosure
- Agents can execute shell commands to run the Python CLIs when needed

### Constraints
- Pure AI output generally lacks strong U.S. copyright protection → human editing is required for robustness
- Platform policies (Spotify, YouTube, Tidal, etc.) change; docs must be kept current
- Udio is currently unsuitable for external distribution (walled garden)

### Key Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Tool removes commercial rights | Only generate on confirmed paid plans; log immediately |
| Platform demonetizes AI content | Disclose, avoid spam, add human value, diversify channels |
| Legal exposure from training data | Prefer lower-risk tools (Soundraw, licensed models) for client work |
| Agent ignores safety rules | Encode rules in AGENTS.md and require rights log before release |

---

## 8. Traceability

| Requirement | Implemented By |
|-------------|----------------|
| FR-01 Workflow | docs/01, 02, 06 + ARCHITECTURE.md |
| FR-02 Rights logging | scripts/rights_logger.py + templates/rights-log.md |
| FR-03 Cost tracking | scripts/cost_tracker.py |
| FR-04 Tool decisions | docs/03 + configs/tools.json |
| FR-05 Templates | templates/* |
| FR-06 Safety rules | AGENTS.md + docs/05 |
| FR-07 Agent operability | AGENTS.md + STRUCTURE.md |
| FR-08 JAIOS pipeline | .github/workflows/deploy.yml + jaios.manifest.json |
| FR-09 Multi-agent roles | docs/08-multi-agent-frameworks.md |
| FR-10 Export | rights_logger.py export command |
| FR-11 Rights verification | rights_logger.py verify [--strict] |
| FR-12 Machine-readable summaries | cost_tracker.py summary --json / --markdown |
| NFR-01 stdlib-only | Enforced by the "Confirm stdlib-only" CI step |
| NFR-07 Headless operation | argparse flags on both CLIs + CI headless smoke test |
| NFR-08 Input validation | valid_date / money / normalize_yes_no / valid_generation_datetime |
| NFR-09 Automated tests | tests/test_cost_tracker.py, tests/test_rights_logger.py (CI) |

---

## 9. Future Extensions (Out of Current Scope)

- Direct API integrations with generators/distributors
- Automated Notion sync on every deploy
- Full CrewAI / LangGraph runtime mapping
- Web dashboard over the CSV data layer
- Payment and delivery automation for commissions

---

## 10. Approval & Change Control

- This document is the design baseline for v1.
- Material changes to requirements or architecture should update this file and `ARCHITECTURE.md` in the same change set.
- Operational tool/pricing changes update `configs/tools.json` and relevant docs only.

---

**Document Control**  
Version 1.0 — 2026-07-24 — Initial formal SADD for Turd Eye Productions (JAIOS module).  
Version 1.1 — 2026-07-25 — Added FR-11/FR-12 (rights verification, machine-readable
summaries) and NFR-07/08/09 (headless operation, input validation, automated tests) to
match the implemented tooling. Updated §4.2, §6.1, and §8 traceability. No change to the
data contracts in §4.3.
