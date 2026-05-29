# 00 — Research Plan

## Research question
What are the exact operational contracts and the file-based state machine required so a **local Python orchestrator** can trigger **Google Jules** (worker) and **Claude Code headless** (operator) to run an autonomous Kaggle-competition loop — for the NVIDIA Nemotron Model Reasoning Challenge first — with minimal/no human supervision? Produce an **implementation plan only** (no code execution), with trigger-prompt designs informed by the user's SDLC skill.

### Sub-questions
1. **Jules contract** — auth, source binding, session create/poll, output (PR/patch), limits, autonomy, AGENTS.md.
2. **Operator contract** — `claude -p` flags, structured output, unattended permissions, MCP loading, session continuity, SDK vs CLI.
3. **Kaggle contract** — MCP tools vs CLI; submission flow; auth without a browser; submission limits.
4. **Competition mechanics** — submission type, metric, format, daily limits, dataset, deadline, GPU needs.
5. **State machine** — how to adapt SDLC's event-sourced StatePatch/permission/lock model to `feedback.xlsx` + tasks + plan + `state.json`.
6. **Trigger prompts** — apply the SDLC 8-surface skeleton to a Jules-worker prompt and a Claude-planner/operator prompt.

## Scope
- **In:** the orchestration architecture, the three external contracts, the state-machine design, the trigger-prompt designs, a phased build roadmap, risks/decisions. Nemotron as the first competition.
- **Out:** writing the actual orchestrator/model code; designing the winning ML solution itself (beyond "fork the open baseline"); other competitions (the design is multi-competition-ready but only Nemotron is detailed).

## Success criteria
A reader can: (a) understand the corrected architecture (Jules ≠ trainer), (b) see the exact API calls/flags/tool names each contract needs, (c) understand the git-committed state machine and how the loop advances, (d) read the two trigger prompts, (e) follow a phased roadmap, and (f) see the open decisions that need the user before code starts.

## Depth calibration
**Maximum rigor** (user asked to "think long and hard iteratively with complete clarity"). Full artifact set + steel-man + live primary-source verification of the Jules contract.

## Methodology
**Technical Deep Dive + Decision Analysis.** Parallel multi-modal investigation (4 streams: SDLC digest, Jules API, Claude/Kaggle, competition), each returning sourced findings; one live API probe for primary-source verification; synthesis into a decision-bearing implementation plan.

## Milestones / quality gates
- G1 (→ investigate): question + scope fixed. ✅
- G2 (→ synthesize): ≥8 sources logged (31 logged), all High-priority Qs addressed or escalated, foundational assumptions validated/flagged. ✅
- G3 (→ report): ≥1 cross-finding pattern (got several: no-GPU × training-comp ⇒ GPU executor; SDLC contracts × 3-API wiring ⇒ trigger prompts), all contradictions analyzed, confidence assigned, steel-man done. ✅

## Risk register (research risks)
- Fast-moving products (Jules launched 2025; Kaggle MCP ~Nov 2025) → obsolescence risk; mitigated by live probe + dated sources.
- Login/JS-gated Kaggle pages → some facts (submission cap, exact rules) unverifiable remotely; escalated as Q-001/Q-002.
- Single-source items flagged at Medium confidence in the findings log.
