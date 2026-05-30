# Jules VM setup — granting Kaggle access (one-time, web UI only)

Jules runs each task in its own short-lived VM. To let Jules read Kaggle, push
kernels, and prepare submission uploads, you set the Kaggle credentials **once
on jules.google's Configuration page** (never in the repo, never in a prompt).

## Steps (5 min, one time)

1. Open <https://jules.google.com> → **Sources** → **manojdadi56/Kaggle** → **Configuration**.
2. Under **Environment → Environment variables**, add:
   - `KAGGLE_USERNAME` = `sai1881`
   - `KAGGLE_API_TOKEN` = `KGAT_840d019061e85f8ee3523a530c6c5ca8`  *(the KGAT you shared)*
3. Under **Environment → Setup script**, paste:
   ```bash
   pip install --quiet httpx jsonschema
   echo "kaggle_lite ready"
   ```
4. Click **Save** then **Take snapshot** so the next task starts with the env baked in.

That's it. Future Jules sessions on this source can now run `python tools/kaggle_lite.py …`.

## Verifying it worked

The next operator tick will dispatch **TASK-K0** (Kaggle access smoke test).
On its PR you should see a one-line `kaggle_lite whoami` result with `ok: true`
and the `kaggle_user`. If `ok: false`, the PR body's NEEDS_INFO will say why
(usually a typo in the env-var name).

## What Jules is *allowed* to do with Kaggle

See `AGENTS.md` "Kaggle access" — read, kernel push/poll/pull, and submission
blob-upload (handoff). **Direct competition submission is operator-only** to
protect the 5/day cap; Jules prepares the zip + cv_score and the operator
runs the gate.

## Security

- `KAGGLE_API_TOKEN` lives only on Jules's per-source env and your laptop's
  gitignored `.env`. It is never committed and never appears in task prompts.
- The deep-worker prompt explicitly forbids printing the token in PR bodies,
  commit messages, or logs.
- Rotate the KGAT at <https://www.kaggle.com/settings/account> whenever you
  want; update both places (Jules env + laptop `.env`).
