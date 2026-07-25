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
4. Log rights using `scripts/rights_logger.py` or the Markdown template.
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
- Cost incurred this session (log via cost_tracker if possible)
- Next recommended actions

### Safety Rules (non-negotiable)
- Do not generate or release content that impersonates living artists.
- Do not advise mass uploading of near-identical tracks.
- Always recommend disclosure on DistroKid / DSPs.
- Flag high-risk platforms (current: Udio for external distribution).

## Available Scripts (stdlib Python, headless-safe)

Both CLIs accept every field as a flag, so you can run them without a TTY. If a
required field is missing and there is no interactive terminal, the command exits
non-zero with a clear message instead of hanging on a prompt. Add `--help` for full usage.

```bash
python scripts/rights_logger.py add --title "..." --tool Suno --plan Pro \
    --commercial yes --human-edits "..." --distributor DistroKid --notes "..."
python scripts/rights_logger.py list --limit 5
python scripts/rights_logger.py verify --strict    # non-zero if any entry breaks the rules below
python scripts/rights_logger.py export             # -> data/rights_log.md

python scripts/cost_tracker.py add-expense --category Suno --amount 10 --description "..."
python scripts/cost_tracker.py add-income --category Commission --amount 300 --description "..."
python scripts/cost_tracker.py summary --json      # machine-readable totals
python scripts/cost_tracker.py summary --markdown  # -> data/cost_summary.md
python scripts/cost_tracker.py list --limit 10
```

`rights_logger verify` machine-checks two of the operating principles above: every
entry must have commercial rights recorded (principle 1) and human edits recorded
(principle 3). Run it before advising a release.

Set `TEP_DATA_DIR` to override where `data/` lives.

## Multi-Agent Collaboration
See `docs/08-multi-agent-frameworks.md` for the 2026 landscape and the recommended role design (Generator, Rights, Editor, Sales, Catalog, Supervisor).

## File Map for Agents
- `README.md` → High-level overview + numbers
- `docs/` → Detailed operational guides
- `templates/` → Copy-paste ready assets
- `scripts/` → Executable helpers
- `playbooks/` → Recurring processes
- `configs/tools.json` → Current recommended tools & costs

## Update Protocol
When tools, pricing, or platform policies change, update:
1. `configs/tools.json`
2. Relevant docs in `docs/`
3. This AGENTS.md if decision logic changes

This project is deliberately tool-agnostic and agent-agnostic. Any capable agent can operate it by reading these Markdown files.