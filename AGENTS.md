# AGENTS.md — Turd Eye Productions

**Purpose**: This file makes the entire project usable by any AI agent (Grok, Claude, Perplexity, Cursor, Windsurf, Aider, OpenHands, custom agents, etc.) without proprietary dependencies.

## Core Mission
Turn AI-generated music (and related audio files) into real, repeatable profit while staying legally and platform-safe.

## Operating Principles (always follow)
1. Prefer commercial-rights plans only.
2. Always disclose AI use where required.
3. Add human value (editing, curation, original lyrics, arrangement).
4. Custom commissions > pure streaming for fast profit.
5. Document rights (generation date + plan active).
6. Never clone real artist voices or styles without permission.
7. Avoid mass low-effort spam uploads.

## How an Agent Should Use This Repo

### When the user asks to generate / release / monetize music:
1. Read `docs/02-workflow.md` and `docs/01-quickstart.md` first.
2. Check current tool recommendations in `configs/tools.json`.
3. Use `templates/` for prompts, checklists, and client offers.
4. Log rights in the style of `templates/rights-log.md`.
5. Prefer the hybrid path: generate catalog + sell custom work.

### Decision Flow (agent should follow this)
```
Is the goal fast cash?
  → Yes → Custom commissions path (see docs/06-custom-commissions.md)
  → No  → Catalog building + streaming/YouTube

Does the tool grant commercial rights on the current plan?
  → No  → Switch plan or tool before generating
  → Yes → Proceed, then document generation timestamp + plan

Is the output pure AI with zero human edit?
  → Yes → Add light editing before release (copyright + quality)
```

### Required Outputs from Agents
When performing work, agents should produce:
- Clear step list of what was done
- Rights log entry (tool, plan, date, commercial status)
- Cost incurred this session
- Next recommended actions

### Safety Rules (non-negotiable)
- Do not generate or release content that impersonates living artists.
- Do not advise mass uploading of near-identical tracks.
- Always recommend disclosure on DistroKid / DSPs.
- Flag high-risk platforms (current: Udio for external distribution).

## File Map for Agents
- `README.md` → High-level overview + numbers
- `docs/` → Detailed operational guides
- `templates/` → Copy-paste ready assets
- `playbooks/` → Recurring processes
- `configs/tools.json` → Current recommended tools & costs

## Update Protocol
When tools, pricing, or platform policies change, update:
1. `configs/tools.json`
2. Relevant docs in `docs/`
3. This AGENTS.md if decision logic changes

This project is deliberately tool-agnostic and agent-agnostic. Any capable agent can operate it by reading these Markdown files.