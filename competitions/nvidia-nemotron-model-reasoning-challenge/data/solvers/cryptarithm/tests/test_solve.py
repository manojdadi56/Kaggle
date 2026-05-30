from solve import solve

def test_concat_fwd():
    prompt = r"""In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
`!*[{ = `"[`
'*'> = ![@
'-!` = \\
`!*\& = '@'{
Now, determine the result for: [[-!'"""
    assert solve(prompt) == "[[!'"

def test_concat_rev():
    prompt = r"""In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
}`]?( = ())
}#<)\ = #?
?(!&& = #@@#
(?!@` = )#))
Now, determine the result for: ))!\)"""
    assert solve(prompt) == r"))\)"

def test_z3_classic():
    prompt = "What is the answer to SEND + MORE = MONEY?"
    assert solve(prompt) == "10652"

if __name__ == "__main__":
    test_concat_fwd()
    test_concat_rev()
    test_z3_classic()
    print("All tests passed.")
