import pytest
import re

try:
    from transformers import AutoTokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

MODEL_ID = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"

@pytest.fixture(scope="module")
def tokenizer():
    if not HAS_TRANSFORMERS:
        pytest.xfail(reason="transformers library not installed or model inaccessible")
    try:
        # Load without requiring authentication, we just need the tokenizer
        return AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    except Exception as e:
        pytest.xfail(reason=f"Failed to load tokenizer: {e}")

def test_template_parity_system_prompt(tokenizer):
    """Test the rendering of a chat template with the expected system prompt."""

    msgs = [
        {"role": "system", "content": "reasoning_on"},
        {"role": "user", "content": "What is 2+2?"}
    ]

    out = tokenizer.apply_chat_template(
        msgs,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True
    )

    expected_out = (
        "<|im_start|>system\n"
        "reasoning_on<|im_end|>\n"
        "<|im_start|>user\n"
        "What is 2+2?<|im_end|>\n"
        "<|im_start|>assistant\n"
        "<think>\n"
    )

    assert out == expected_out, f"Expected:\n{repr(expected_out)}\nGot:\n{repr(out)}"

def test_template_parity_with_suffix(tokenizer):
    """Test the rendering of a chat template with the host competition suffix."""

    user_content = "What is 2+2?\nPlease put your final answer inside `\\boxed{}`. For example: `\\boxed{your answer}`"

    msgs = [
        {"role": "system", "content": "reasoning_on"},
        {"role": "user", "content": user_content}
    ]

    out = tokenizer.apply_chat_template(
        msgs,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True
    )

    expected_out = (
        "<|im_start|>system\n"
        "reasoning_on<|im_end|>\n"
        "<|im_start|>user\n"
        "What is 2+2?\n"
        "Please put your final answer inside `\\boxed{}`. For example: `\\boxed{your answer}`<|im_end|>\n"
        "<|im_start|>assistant\n"
        "<think>\n"
    )

    assert out == expected_out, f"Expected:\n{repr(expected_out)}\nGot:\n{repr(out)}"

    # Asserting the formatting substring exists in the expected location
    assert r"`\boxed{}`" in out
    assert r"`\boxed{your answer}`" in out

def test_template_parity_no_system_prompt(tokenizer):
    """Test rendering when no system prompt is provided, but thinking is enabled."""

    msgs = [
        {"role": "user", "content": "What is 2+2?"}
    ]

    out = tokenizer.apply_chat_template(
        msgs,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True
    )

    expected_out = (
        "<|im_start|>system\n"
        "<|im_end|>\n"
        "<|im_start|>user\n"
        "What is 2+2?<|im_end|>\n"
        "<|im_start|>assistant\n"
        "<think>\n"
    )

    assert out == expected_out, f"Expected:\n{repr(expected_out)}\nGot:\n{repr(out)}"

def test_template_parity_no_thinking(tokenizer):
    """Test rendering when thinking is disabled."""

    msgs = [
        {"role": "user", "content": "What is 2+2?"}
    ]

    out = tokenizer.apply_chat_template(
        msgs,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False
    )

    expected_out = (
        "<|im_start|>system\n"
        "<|im_end|>\n"
        "<|im_start|>user\n"
        "What is 2+2?<|im_end|>\n"
        "<|im_start|>assistant\n"
        "<think></think>"
    )

    assert out == expected_out, f"Expected:\n{repr(expected_out)}\nGot:\n{repr(out)}"



def test_template_parity_multiple_turns(tokenizer):
    """Test rendering with multiple conversation turns."""

    msgs = [
        {"role": "system", "content": "reasoning_on"},
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "4", "reasoning_content": "2 plus 2 is 4"},
        {"role": "user", "content": "And 4+4?"}
    ]

    out = tokenizer.apply_chat_template(
        msgs,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True
    )

    expected_out = (
        "<|im_start|>system\n"
        "reasoning_on<|im_end|>\n"
        "<|im_start|>user\n"
        "What is 2+2?<|im_end|>\n"
        "<|im_start|>assistant\n"
        "<think></think>\n"
        "4<|im_end|>\n"
        "<|im_start|>user\n"
        "And 4+4?<|im_end|>\n"
        "<|im_start|>assistant\n"
        "<think>\n"
    )

    assert out == expected_out, f"Expected:\n{repr(expected_out)}\nGot:\n{repr(out)}"
