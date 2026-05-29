"""Operator integration — drive Claude Code headless as the per-tick brain.

The Operator renders the tick prompt, calls an injected `invoke(prompt) -> dict`
(default shells `claude -p ... --output-format json --json-schema ...`), and
validates the returned decision against operator_decision.schema.json.

Tests inject a fake `invoke`, so no Anthropic calls happen offline.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Callable

from jsonschema import Draft202012Validator

from . import config


class OperatorError(RuntimeError):
    pass


def _render(template: str, context: dict) -> str:
    out = template
    for key, val in context.items():
        token = "{{" + key + "}}"
        if token in out:
            rendered = val if isinstance(val, str) else json.dumps(val, ensure_ascii=False, indent=2)
            out = out.replace(token, rendered)
    return out


class Operator:
    def __init__(
        self,
        schema_path: Path | None = None,
        system_prompt_path: Path | None = None,
        tick_prompt_path: Path | None = None,
        invoke: Callable[[str], dict] | None = None,
        model: str = "opus",
        session_id: str | None = None,
        cwd: Path | None = None,
        max_turns: int = 60,
    ):
        self.schema_path = Path(schema_path) if schema_path else (config.REPO_ROOT / "operator_decision.schema.json")
        self.system_prompt_path = Path(system_prompt_path) if system_prompt_path else (config.PROMPTS_DIR / "operator_system.md")
        self.tick_prompt_path = Path(tick_prompt_path) if tick_prompt_path else (config.PROMPTS_DIR / "operator_tick.md")
        self.model = model
        self.session_id = session_id
        self.cwd = Path(cwd) if cwd else config.REPO_ROOT
        self.max_turns = max_turns
        self._validator = Draft202012Validator(
            json.loads(self.schema_path.read_text(encoding="utf-8"))
        )
        self.invoke = invoke or self._default_invoke
        self._resume = False  # first tick assigns session id; later ticks resume

    def render_tick_prompt(self, context: dict) -> str:
        return _render(self.tick_prompt_path.read_text(encoding="utf-8"), context)

    def run_tick(self, context: dict) -> dict:
        prompt = self.render_tick_prompt(context)
        decision = self.invoke(prompt)
        errors = sorted(self._validator.iter_errors(decision), key=lambda e: e.path)
        if errors:
            msgs = "; ".join(e.message for e in errors[:5])
            raise OperatorError(f"operator decision failed schema validation: {msgs}")
        return decision

    # ---- default real invocation (not used in tests) ----
    def _default_invoke(self, prompt: str) -> dict:
        cmd = [
            "claude", "-p", prompt,
            "--output-format", "json",
            "--json-schema", str(self.schema_path),
            "--permission-mode", "acceptEdits",
            "--model", self.model,
            "--max-turns", str(self.max_turns),
            "--append-system-prompt-file", str(self.system_prompt_path),
        ]
        if self.session_id:
            cmd += (["--resume", self.session_id] if self._resume else ["--session-id", self.session_id])
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.cwd))
        if p.returncode != 0:
            raise OperatorError(f"claude headless failed (rc={p.returncode}): {p.stderr[:500]}")
        self._resume = True
        payload = json.loads(p.stdout)
        decision = payload.get("structured_output")
        if decision is None and isinstance(payload.get("result"), str):
            decision = json.loads(payload["result"])
        if decision is None:
            raise OperatorError("no structured_output in claude response")
        return decision
