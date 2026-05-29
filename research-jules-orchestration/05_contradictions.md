# 05 — Contradictions

| ID | Conflict | Resolution |
|----|----------|------------|
| C-001 | User's notes name the Kaggle submit tool `kaggle_mcp_submit_to_competition` / `mcp_kaggle_start_competition_submission_upload`; the official catalog + community servers use `competition_submit` (+ an upload-URL tool). | **Resolved → use `competition_submit`** (F-018). The user's names are likely paraphrased from an older/marketing blurb. Verify exact upload-tool name live (Q-008). Even so, we prefer the **kaggle CLI** for the deterministic submit (F-020). |
| C-002 | Original concept: "Jules completes the work and submits results." vs reality: Nemotron is GPU LoRA training and Jules has no GPU. | **Resolved → split roles** (A-001 invalidated). Jules authors/iterates code & data-gen; a GPU executor trains; the operator packages + submits. |
| C-003 | One community write-up shows source format `sources/github-owner-repo` (dashes); official docs + live API use `sources/github/{owner}/{repo}` (slashes). | **Resolved → slashes** (F-002, confirmed live S-001). |
| C-004 | Kaggle default submission cap (~5/day) vs likely-lower cap for an expensive host-scored LLM comp. | **Unresolved → treat as unknown** (Q-001). Read remaining submissions at runtime; never hard-code. User's "3 auto-submits/day" must be clamped to the real cap. |
| C-005 | "Run seamlessly with minimal/no supervision" (user goal) vs the GPU-compute reality + tight 16-day window + login-gated submission rules. | **Partial tension, not a hard contradiction.** Achievable for the *code-iteration loop* (Jules + operator) with near-zero supervision; the *compute* and *first-time auth/rule-confirmation* steps need a one-time human setup. Documented as the central trade-off in the steel-man (10) and DECISIONS. |
