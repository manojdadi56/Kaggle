import re

def patch_notebook(source: str) -> str:
    """
    Patches the notebook source to:
    (1) Update build_datum()/datum() to correctly mask the prompt tokens (0) and completion tokens (1)
        using apply_chat_template to determine proper offsets.
    (2) Update LR schedule to decay per STEP instead of per epoch.
    """

    # 1. Patch datum() function
    new_datum_code = '''def datum(prompt_text: str, answer_text: str, tokenizer, max_length: int = 8192):
    # Format the prompt alone to find its exact token length
    prompt_chat = [{"role": "user", "content": prompt_text}]
    prompt_formatted = tokenizer.apply_chat_template(prompt_chat, tokenize=False, add_generation_prompt=True)
    prompt_tokens = tokenizer(prompt_formatted, add_special_tokens=False)["input_ids"]

    # Format the full chat
    full_chat = [{"role": "user", "content": prompt_text}, {"role": "assistant", "content": answer_text}]
    full_formatted = tokenizer.apply_chat_template(full_chat, tokenize=False)

    # Some tokenizers do not automatically append the EOS token to the assistant response in the template.
    if not full_formatted.endswith(tokenizer.eos_token):
        full_formatted += tokenizer.eos_token

    full_tokens = tokenizer(full_formatted, add_special_tokens=False)["input_ids"]

    # Determine the mask: 0 for prompt, 1 for assistant response
    prompt_len = len(prompt_tokens)

    # In some edge cases prompt_len might exceed full_tokens length if the template behaves weirdly,
    # but normally it should be a prefix.
    mask = [0] * prompt_len + [1] * max(0, len(full_tokens) - prompt_len)

    # Truncate to max_length if necessary
    if len(full_tokens) > max_length:
        full_tokens = full_tokens[:max_length]
        mask = mask[:max_length]

    return full_tokens, mask'''

    def repl_datum_manual(match):
        indent = match.group(1)
        old_name = match.group(2)

        lines = new_datum_code.replace("def datum(", f"def {old_name}(").split('\n')

        # The first line has the original indent
        res = [indent + lines[0]]
        # We need to compute how much indentation the new code had natively (4 spaces here).
        # We replace the original 4 spaces with the proper indent + 4 spaces
        for line in lines[1:]:
            if line.startswith('    '):
                # Line was indented by 4 spaces in our string
                res.append(indent + '    ' + line[4:])
            elif line.startswith('        '):
                res.append(indent + '        ' + line[8:])
            elif not line.strip():
                res.append('')
            else:
                res.append(indent + line)

        return '\n'.join(res)

    pattern_datum = re.compile(
        r'^([ \t]*)def ((?:build_)?datum)\([^)]*\):.*?return.*?mask\s*$',
        re.DOTALL | re.MULTILINE
    )

    if pattern_datum.search(source):
        source = pattern_datum.sub(repl_datum_manual, source)

    # 2. Patch LR Schedule
    # If the LR is assigned using epoch, replace it with step / total_steps

    def repl_generic_lr(match):
        indent = match.group(1)
        return indent + 'lr = lr_initial + (lr_final - lr_initial) * (step / total_steps)'

    pattern_generic_lr = re.compile(
        r'^([ \t]*)(?:lr|learning_rate)\s*=\s*[^\n]*epoch[^\n]*$',
        re.MULTILINE
    )
    source = pattern_generic_lr.sub(repl_generic_lr, source)

    return source
