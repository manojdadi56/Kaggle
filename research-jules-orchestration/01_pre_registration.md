# 01 — Pre-Registration

Stated **before** the deep investigation, to detect confirmation bias. Compared against reality in the meta-log / synthesis.

## Expected findings (E) and their disconfirmers (D)

**E-1.** Jules has a real REST API with key auth, create-task + poll-status + PR output.
- D-1: If Jules were UI-only or had no public API, the whole "trigger via API" design collapses.
- **Outcome: CONFIRMED and exceeded** — full `v1alpha` API, verified live (F-001..F-006). ✅

**E-2.** Jules executes on its own VM and can do arbitrary coding work including ML training.
- D-2: If the VM is constrained (no GPU, short runtime), it can't train models.
- **Outcome: PARTIALLY DISCONFIRMED — the important surprise.** Jules has no GPU (F-008); the Nemotron task *is* GPU training (F-024). Jules is reduced to a **code author**, not an end-to-end solver. This reshaped the architecture. ⚠️

**E-3.** Nemotron is a notebook/CSV competition where you submit predictions.
- D-3: If it's a training/artifact competition, "submit predictions" is wrong.
- **Outcome: DISCONFIRMED** — it's a LoRA-adapter-upload, host-scored competition (F-021, F-022). Second major surprise.

**E-4.** Claude Code can run headless and return structured output for an orchestrator to parse.
- D-4: If `-p` only returned freeform text, machine control would be brittle.
- **Outcome: CONFIRMED** — `--output-format json --json-schema` → `.structured_output` (F-011). ✅

**E-5.** Kaggle submission is automatable without a browser.
- D-5: If only the browser/MCP-OAuth path worked, unattended submit would be blocked.
- **Outcome: CONFIRMED** — kaggle CLI with env auth (F-017); MCP needs a bearer-header workaround (F-019). ✅

**E-6.** The SDLC skill is a generic project tracker.
- D-6: If it were just a checklist, it wouldn't inform contract design.
- **Outcome: DISCONFIRMED (pleasantly)** — it is a rigorous event-sourced, single-role-per-cycle, permissioned, idempotent orchestration contract that maps almost 1:1 onto this problem (F-027..F-036). It is the design DNA.

**E-7.** The main risk is wiring three APIs together.
- D-7: If a non-API constraint dominated, wiring would be secondary.
- **Outcome: DISCONFIRMED** — the dominant risks are **GPU compute** (F-024) and **time** (F-025, ~16 days), not API wiring (which is clean). This is the most important strategic takeaway.

## Net
4 of 7 expectations were disconfirmed or materially changed. The surprises (no-GPU Jules, training-not-prediction comp, compute/time as the real bottleneck) are exactly where the design value is — they move the plan from "wire 3 APIs" to "wire 3 APIs **plus** a GPU executor, baseline-first, under a deadline."
