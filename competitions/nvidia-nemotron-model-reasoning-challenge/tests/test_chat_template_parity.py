import json
import os
import sys
import pytest

# Need to append eval dir so we can import from vllm_eval
eval_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "eval")
sys.path.append(eval_dir)

from vllm_eval import build_prompt

@pytest.fixture
def chat_template_fixture():
    fixture_path = os.path.join(eval_dir, "chat_template_fixture.jsonl")
    data = []
    with open(fixture_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

@pytest.mark.xfail(reason="TODO: harness uses hardcoded template, must load official HF template instead")
def test_chat_template_parity(chat_template_fixture):
    # This tests the fallback harness builder vs the expected exact HF template render
    # Currently vllm_eval.py's build_prompt uses a hard-coded naive prompt:
    # <|im_start|>user\n{problem}<|im_end|>\n<|im_start|>assistant\n
    #
    # But the expected HF rendering includes system reasoning_on token structure.
    for item in chat_template_fixture:
        rendered = build_prompt(item)
        expected = item["expected_rendered"]

        # We assert byte-equality (exact string match)
        assert rendered == expected, f"Rendered prompt does not match exactly.\nExpected:\n{expected!r}\nGot:\n{rendered!r}"
