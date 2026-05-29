# US-6 — Mine community discussions & notebooks to improve experiments

> As the system, I want the best community discussions and notebooks continuously mined into a concrete, ranked technique backlog, so each experiment starts from proven settings instead of guesses.

**Recurring story.** No-GPU, high-leverage → ideal for Jules. Extends US-1 (one-shot analysis) into an ongoing intel loop: read items are fetched/summarized to JSON, the operator synthesizes a digest + ranked backlog, and the highest-ranked reproducible items become US-3/US-4/US-5 tasks. Re-run when the leaderboard moves or new strong notebooks appear.

## Artifacts
- Digest: `references/DIGEST-community.md` (themed: data/synthetic · training/LoRA · prompting · eval · reproducibility, with concrete settings + URL citations).
- Per-item files: `references/discussions/*.md`, `references/notebooks/*.md` (one per fetched source; gated pages note the recovery source).
- Ranked technique backlog: feeds `plan.md` "technique backlog" section and spawns tasks.

## Acceptance criteria
- [ ] `references/DIGEST-community.md` exists, groups findings by the 5 themes, and every concrete setting cites a source URL.
- [ ] Backlog is **ranked** with rationale + effort (S/M/L) + expected_gain, biased toward what's reproducible on free Kaggle 2×T4 first.
- [ ] Winner's verbatim recipe captured: base model, LoRA rank 32 (MLP+attn+unembed), LR 2e-4 step-linear-decay, batch 64 / micro 16, 1 epoch, max_len 8192, cross-entropy SFT.
- [ ] 2×T4 reproducibility constraints recorded (4-bit QLoRA + max_memory sharding + offload, `transformers>=4.45,<5`, `mamba-ssm`/`causal-conv1d`, explicit Mamba-mixer LoRA targeting to avoid the MoE-scan hang and merge mismatch).
- [ ] Host eval params captured for the CV harness (vLLM temp 0, top_p 1, max_tokens 7680, max_model_len 8192, `\boxed{}` exact / ±1e-2).
- [ ] Top-ranked reproducible items converted into TASK-3.x / TASK-4.x / TASK-5.x with the source linked.
- [ ] Gated sources note how content was recovered (e.g. winner repo `tonghuikang/nemotron`), not presented as verbatim notebook cells.

## Key takeaway driving the backlog
Win condition is the **deterministic per-category solver + verified-CoT data engine** (CPU-only, reproducible anywhere), not RL or big compute. LB ladder 0.65→0.85 is almost entirely data quality. Port the winner's data half locally; do the 30B LoRA SFT on the GPU executor (2×T4 via QLoRA, or the 40 GB box once configured).

Tasks: TASK-6.1 (operator fetch/summarize new sources → JSON) → TASK-6.2 (synthesize digest + ranked backlog) → spawn TASK-3.x/4.x/5.x from top items.
Done when `references/DIGEST-community.md` + ranked backlog exist and at least the top reproducible technique is filed as a concrete task.

## Links
- Digest: [`references/DIGEST-community.md`](../references/DIGEST-community.md)
- This story: `user-stories/US-6-mine-community.md`
- Per-item source files: `references/discussions/`, `references/notebooks/`
- Primary source of truth: https://github.com/tonghuikang/nemotron

## Artifacts (as stored)
- Digest: `references/DIGEST-community.md`
- Per-item sources (all 22): `references/community-sources.md`
- Ranked experiments: `references/technique-backlog.md`
- Index: `references/INDEX.md`
- Primary source of truth: https://github.com/tonghuikang/nemotron (+ discussion 689915)
