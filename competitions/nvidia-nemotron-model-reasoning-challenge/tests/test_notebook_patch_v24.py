import pytest
import os
import sys

# Add the patches directory to the path so we can import the module
patches_dir = os.path.join(os.path.dirname(__file__), '../experiments/notebook_patches')
sys.path.append(patches_dir)

from v24_target_masking import patch_notebook

class DummyTokenizer:
    def __init__(self):
        self.eos_token = "<eos>"
        self.eos_token_id = 99

    def __call__(self, text, add_special_tokens=False):
        # Dummy tokenization: just split by spaces and give each a length of 1 token for simplicity
        # To make it slightly realistic, we'll assign unique integer IDs
        tokens = text.split()
        return {"input_ids": [hash(t) % 1000 for t in tokens]}

    def apply_chat_template(self, conversation, tokenize=False, add_generation_prompt=False):
        # A simple dummy chat template renderer
        res = ""
        for turn in conversation:
            res += f"<{turn['role']}>\n{turn['content']}\n"
        if add_generation_prompt:
            res += "<assistant>\n"
        return res

def test_patch_notebook():
    stub_notebook = """
def build_datum(prompt_text: str, answer_text: str, tokenizer, max_length: int = 8192):
    prompt_tokens = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    answer_tokens = tokenizer(answer_text, add_special_tokens=False)["input_ids"]
    answer_tokens = answer_tokens + [tokenizer.eos_token_id]
    tokens = prompt_tokens + answer_tokens
    mask = [0]*len(prompt_tokens) + [1]*len(answer_tokens)
    return tokens, mask

def train():
    for epoch in range(total_epochs):
        for step, batch in enumerate(batches):
            lr = lr_initial + (lr_final - lr_initial) * (epoch / total_epochs)
            optimizer.step()
"""

    patched = patch_notebook(stub_notebook)

    # 1. Assert LR was changed correctly
    assert "lr = lr_initial + (lr_final - lr_initial) * (step / total_steps)" in patched, "LR schedule was not updated per step correctly."
    assert "epoch / total_epochs" not in patched, "Epoch-based LR decay should be removed."

    # 2. Extract and run the patched datum function
    # We will execute the patched string in a local dictionary to get the function
    local_env = {}
    exec(patched, globals(), local_env)

    assert "build_datum" in local_env, "build_datum function not found after patch."
    build_datum = local_env["build_datum"]

    tokenizer = DummyTokenizer()
    prompt = "What is 2+2?"
    answer = "The answer is 4."

    tokens, mask = build_datum(prompt, answer, tokenizer)

    # Let's verify mask
    prompt_formatted = tokenizer.apply_chat_template([{"role": "user", "content": prompt}], add_generation_prompt=True)
    prompt_tokens_len = len(tokenizer(prompt_formatted)["input_ids"])

    assert sum(mask[:prompt_tokens_len]) == 0, "Prompt tokens should have mask 0."
    assert all(m == 1 for m in mask[prompt_tokens_len:]), "Completion tokens should have mask 1."
    assert len(mask) == len(tokens), "Mask length should match tokens length."

def test_patch_notebook_datum():
    # Remove indentation for exec to work cleanly at module level
    stub_notebook = """
def datum(prompt_text: str, answer_text: str, tokenizer, max_length: int = 8192):
    prompt_tokens = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    answer_tokens = tokenizer(answer_text, add_special_tokens=False)["input_ids"]
    answer_tokens = answer_tokens + [tokenizer.eos_token_id]
    tokens = prompt_tokens + answer_tokens
    mask = [0]*len(prompt_tokens) + [1]*len(answer_tokens)
    return tokens, mask
"""

    patched = patch_notebook(stub_notebook)

    local_env = {}
    exec(patched, globals(), local_env)

    assert "datum" in local_env, "Function not found after patch."
