# 06 — Source Log

Quality scale: **A** = official primary docs / live API response; **B** = official-but-secondary (changelog, announcement); **C** = credible third-party (vendor catalog, hands-on walkthrough, competitor repo restating rules); **D** = promotional / low-detail.

| ID | Source | Type | Quality | Used for |
|----|--------|------|---------|----------|
| S-001 | Live `GET https://jules.googleapis.com/v1alpha/sources` with the user's key (probed 2026-05-30) | Primary / live API | **A** | F-001, F-002, F-016 — auth works, source format, **Kaggle repo is connected** |
| S-002 | jules.google/docs/api/reference/authentication/ | Official docs | A | F-001 auth header, base URL |
| S-003 | jules.google/docs/api/reference/sessions/ | Official docs | A | F-004, F-005, F-006 session create/poll/output, approvePlan, sendMessage |
| S-004 | jules.google/docs/api/reference/sources/ | Official docs | A | F-002 source object/list |
| S-005 | jules.google/docs/api/reference/types/ | Official docs | A | F-005, F-006 state enum, automationMode, PullRequest/outputs/gitPatch |
| S-006 | developers.google.com/jules/api(/reference/rest) | Official docs (Google) | A | F-001, F-003, F-004 REST resource paths |
| S-007 | jules.google/docs/usage-limits/ | Official docs | A | F-007 tier task/concurrency limits |
| S-008 | jules.google/docs/environment/ | Official docs | A | F-008 VM, preinstalled runtimes, **no GPU**, AGENTS.md, setup script |
| S-009 | jules.google/docs/changelog/2026-01-26-4/ | Official changelog | B | F-006 file outputs (gitPatch), createTime activity filter, repoless sessions |
| S-010 | github.com/google-labs-code/jules-action | Official Action repo | A | F-009 GitHub Action option |
| S-011 | github.com/google-labs-code/jules-sdk | Official TS SDK | B | F-009 SDK surface (TS only) |
| S-012 | github.com/AsyncFuncAI/jules-agent-sdk-python | Community Python SDK | C | F-009 community Python wrapper (unofficial, early) |
| S-013 | code.claude.com/docs/en/headless | Official docs | A | F-010, F-011 `claude -p`, output formats, `--bare` |
| S-014 | code.claude.com/docs/en/cli-reference | Official docs | A | F-011, F-012 flags: permission-mode, mcp-config, session, max-turns, model |
| S-015 | code.claude.com/docs/en/mcp | Official docs | A | F-013 MCP config shape, tool naming `mcp__server__tool`, strict-mcp-config |
| S-016 | code.claude.com/docs/en/agent-sdk/overview | Official docs | A | F-014 Python `claude-agent-sdk` recommended for automation |
| S-017 | support.claude.com/.../15036540 (Agent SDK billing) | Official support | B | F-014 Agent SDK credit billing from 2026-06-15 |
| S-018 | kaggle.com/product-announcements/635978 + x.com/kaggle status | Official announcement | B | F-018 Kaggle MCP exists, official, ~Nov 2025 |
| S-019 | kaggle.com/docs/mcp | Official docs (JS-rendered, not directly readable) | A* | F-018 tool surface (could not load verbatim) |
| S-020 | medium.com/@ibrahim313 — submit to Kaggle via MCP (Apr 2026) | Hands-on walkthrough | C | F-018, F-019 submission flow, bearer KGAT auth, 57 tools |
| S-021 | composio.dev/toolkits/kaggle | Vendor tool catalog | C | F-018 competition tool names + params |
| S-022 | github.com/Galaxy-Dawn/kaggle-mcp, github.com/54yyyu/kaggle-mcp | Community MCP servers | C | F-018 `competition_submit`/`blob_file_tokens`, KGAT format |
| S-023 | npmjs.com/package/mcp-remote + github.com/geelen/mcp-remote | Official package | A | F-019 OAuth flow, `--header`, `~/.mcp-auth` caching |
| S-024 | github.com/Kaggle/kaggle-cli/blob/main/docs/competitions.md | Official CLI docs | A | F-020 `kaggle competitions submit -f / -k / -v` |
| S-025 | competehub.dev — Nemotron competition mirror | Third-party mirror | C | F-021..F-025 task, metric, timeline, prizes |
| S-026 | github.com/yunior123/nvidia-nemotron-reasoning (README) | Competitor repo restating rules | C | F-021, F-022, F-023 adapter-zip + server-side vLLM, metric, inference params |
| S-027 | github.com/SebAustin/NVIDIA-Nemotron-Model-Reasoning-Challenge (README) | Competitor repo | C | F-022 adapter-zip, base model, rank ≤ 32, QLoRA/T4 |
| S-028 | github.com/tonghuikang/nemotron + blog.huikang.dev (2026-05-02) | Progress-prize winner repo/blog | C | F-021, F-026 best reference solution, midpoint won |
| S-029 | kaggle.com/code/ryanholbrook/nvidia-nemotron-submission-demo | Official starter notebook (title-only fetch) | A* | F-026 official starter exists |
| S-030 | `C:\Users\Manoj Sai\Downloads\Archive (3)\Archive\sdlc` (SKILL.md, references/, scripts/, schemas/) | User's local skill (read directly) | A | F-027..F-036 SDLC contract patterns |
| S-031 | kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/rules | Official rules (reCAPTCHA-blocked) | A* | Q-001, Q-002 submission limit + eligibility (NOT readable) |

`A*` = authoritative source that exists but could not be read directly (JS-rendered / login / reCAPTCHA); facts came from corroborating C-grade sources and are flagged accordingly.
