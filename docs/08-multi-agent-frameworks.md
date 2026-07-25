# 08 — Multi-Agent Collaborator Frameworks (2026)

## Landscape Snapshot (July 2026)

| Framework                  | Style                    | Best For                          | Maturity     | Learning Curve |
|---------------------------|--------------------------|-----------------------------------|--------------|----------------|
| **LangGraph**             | Graph / state machine    | Production, complex stateful flows| Highest      | Steep          |
| **CrewAI**                | Role-based crews         | Fast prototypes, role collaboration | High       | Easy           |
| **OpenAI Agents SDK**     | Handoff-based            | Simple multi-agent + OpenAI stack | High         | Easy           |
| **Microsoft Agent Framework** | Conversational + graph | Enterprise / .NET + Python        | High         | Medium         |
| **AutoGen / AG2**         | Conversational agents    | Research, debate-style            | Medium       | Medium         |
| Custom + AGENTS.md        | Prompt + file driven     | Maximum portability               | N/A          | Lowest         |

**Key takeaway**: LangGraph leads production deployments. CrewAI remains the fastest way to stand up role-based teams. For maximum agent-agnosticism we stay framework-light and define clear roles that any system can implement.

## Recommended Role Design for Turd Eye Productions

These roles work whether you use CrewAI, LangGraph, a custom supervisor, or just multiple chat sessions:

1. **Generator Agent**  
   - Creates tracks on commercial-rights plans  
   - Follows niche strategy and prompt templates  
   - Outputs raw audio + generation metadata

2. **Rights & Compliance Agent**  
   - Runs / updates the rights logger  
   - Verifies commercial rights and disclosure requirements  
   - Blocks releases that violate safety rules

3. **Editor Agent**  
   - Performs light human-style editing guidance (or actual DAW instructions)  
   - Improves structure, removes artifacts, prepares final files

4. **Sales / Commission Agent**  
   - Handles client briefs  
   - Generates Fiverr/Upwork responses and package recommendations  
   - Tracks order status

5. **Catalog & Analytics Agent**  
   - Monitors streaming performance  
   - Suggests which niches to double down on  
   - Updates cost tracker with income figures

6. **Supervisor / Orchestrator** (optional)  
   - Routes tasks between the above agents  
   - Enforces the decision flow in `AGENTS.md`

## How to Use Without Lock-in

- Keep all operational knowledge in the Markdown files of this repo.
- Any agent can read `AGENTS.md` + the relevant docs and act.
- When you adopt a framework, map the roles above to its constructs (CrewAI Agents, LangGraph nodes, etc.).
- The Python scripts (`rights_logger.py`, `cost_tracker.py`) remain callable tools for any agent that can run shell commands.

## Suggested Starting Point

1. Begin with clear role prompts + this repo (no framework).
2. If coordination becomes painful, try **CrewAI** for rapid role-based crews.
3. Move to **LangGraph** when you need durable state, retries, or human-in-the-loop approvals.

This keeps Turd Eye Productions portable across Perplexity, Grok, Claude, Cursor, OpenHands, or any future agent runtime.