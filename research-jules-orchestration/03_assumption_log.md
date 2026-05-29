# 03 — Assumption Log

Status: **Validated** · **Invalidated** · **Active** (unverified, load-bearing) · **Flagged** (risky).

| ID | Assumption | Status | Evidence / Note |
|----|-----------|--------|-----------------|
| A-001 | "Jules can do the competition work end-to-end (train the model)." | **INVALIDATED** | F-024 + F-008: the task is GPU LoRA training; Jules' VM has no GPU. Jules can only author/iterate *code*; a separate GPU executor is mandatory. This is the single most important correction to the original concept. |
| A-002 | The Kaggle repo must have the Jules GitHub App installed before we can trigger it. | **INVALIDATED** | F-016: live probe shows `sources/github/manojdadi56/Kaggle` is already connected. No setup step needed. |
| A-003 | Jules runs fully autonomously without human plan-approval clicks when triggered via API. | **Validated** | F-004: API-created sessions auto-approve plans by default; `automationMode:AUTO_CREATE_PR` opens the PR. |
| A-004 | A local Python script can serve as the always-on scheduler/orchestrator on the user's Windows laptop. | **Active** | User's chosen design. Caveat: it only runs while the laptop is on (accepted trade-off). Resilience handled via persisted state + idempotency. |
| A-005 | Claude Code in headless mode (`claude -p`) can act as the operator and return machine-readable decisions to the orchestrator. | **Validated** | F-010, F-011: `--output-format json --json-schema` → `.structured_output`. |
| A-006 | The Kaggle submission can be automated without a browser. | **Validated** (file path) | F-017: kaggle CLI submits with env-var auth, no browser. MCP needs bearer-header workaround (F-019). |
| A-007 | The competition allows scripted/automated submission (no anti-automation rule violation). | **Flagged** | Q-002: Kaggle prohibits multi-account & some automation; the gated `/rules` page must be confirmed before going live. Single-account scripted submit is normally fine, but verify. |
| A-008 | Daily submission limit is ~5/day (Kaggle default). | **Flagged** | Q-001: NOT confirmed — host-side LLM scoring is expensive, cap may be 1–3/day. Design must read remaining-submissions at runtime, not hard-code. |
| A-009 | The Excel feedback file is a safe single-writer store if only the operator writes it. | **Active** | Adopted from SDLC F-031. Risk: the user opening `feedback.xlsx` in Excel locks the file on Windows → orchestrator write fails. Mitigation: user edits via Claude chat (operator transcribes), or use a `.md`/`.csv` mirror the user edits and operator reads. |
| A-010 | Kaggle Notebooks (kernels) can be pushed/run/polled/pulled fully via the kaggle API for the GPU training step. | **Active** | F-017 + general kaggle CLI (`kernels push/status/output`). The free-GPU path is automatable end-to-end but compute-limited; needs validation that a 30B-MoE QLoRA fits and finishes in notebook limits. |
| A-011 | One competition active at a time is sufficient (user's choice). | **Validated (refined)** | One *active* competition, but each competition is a fully self-contained folder `competitions/<slug>/` (user correction 2026-05-30). Adding a comp = a new isolated folder; `state.json.active_competition` points at the live one. |
| A-017 | The user's 40 GB 2-GPU local system can be a primary trainer once configured. | **Active (to configure)** | User has a 40 GB 2-GPU box (details TBD, Q-014). 40 GB holds a 4-bit 30B QLoRA → strongest free option, likely > 2×T4. Added to the executor registry as `local_40g`; "keep ready, wire in later." It is the user's own hardware (not an alt account) — compliant. |
| A-018 | Parallel Jules sessions are safe for independent experiments. | **Active** | User correction 2026-05-30. Bounded by Jules tier concurrency (free = 3, F-007); operator must certify independence (disjoint `allowed_area` + own branch) and hold per-area locks; PRs merged one at a time. Risk: false independence → merge conflicts; mitigated by path-prefix locks + "if unsure, don't parallelize." |
| A-012 | The operator (Claude) can be granted authority to merge PRs and submit (user granted "full autonomy"). | **Validated** | User decision. Bounded by: 3 auto-submits/day then approval (user's submit policy), and git as the rollback safety net. |
| A-013 | Jules honors `AGENTS.md` for repo-specific build/test/style instructions. | **Validated** | F-008. We will ship an `AGENTS.md` so every Jules session inherits competition context + guardrails without re-prompting. |
| A-014 | The orchestrator's secrets can live only in a local gitignored `.env`, never in the repo. | **Active** (policy) | Required. Keys pasted in chat (Jules, Kaggle) should be rotated post-setup (A-015). |
| A-015 | The pasted keys are still valid for setup but should be rotated. | **Active** | Jules auto-disables publicly-exposed keys (F-001 note); both keys are now in the transcript. Plan assumes rotation before production. |
| A-016 | Using multiple Kaggle accounts to pool free GPU quota for one competition is acceptable. | **INVALIDATED (governance)** | F-037: violates Kaggle's one-account-per-participant rule → disqualification from the ~$106k prize + bans across all linked accounts. Marginal compute upside vs catastrophic downside. **Declined; not built.** Use one account + own/paid compute instead. |

## Locked user decisions (2026-05-30)
- **D-2 = Baseline-first**, then automate. ✅
- **D-3 = Chat-only feedback**: user talks to Claude; operator writes git-tracked `feedback.md` + a read-only `.xlsx` view. ✅
- **D-1 = compute: REOPENED.** User proposed multi-Kaggle-account pooling → declined on ToS/governance grounds (A-016/F-037). Awaiting a compliant compute choice.
