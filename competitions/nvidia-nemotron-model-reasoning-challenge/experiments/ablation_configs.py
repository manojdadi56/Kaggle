CONFIGS = {
    'baseline': {
        'lora_rank': 32,
        'alpha': 64,
        'epochs': 1,
        'lr': 2e-4,
        'target_modules': ['mixer.in_proj', 'mixer.out_proj', 'q_proj', 'k_proj', 'v_proj', 'o_proj'],
        'hypothesis': 'Baseline matching the winner configuration with a few adjustments for T4 memory.',
        'source': 'technique-backlog.md:4'
    },
    'rank16': {
        'lora_rank': 16,
        'alpha': 32,
        'epochs': 1,
        'lr': 2e-4,
        'target_modules': ['mixer.in_proj', 'mixer.out_proj', 'q_proj', 'k_proj', 'v_proj', 'o_proj'],
        'hypothesis': 'Reducing rank to 16 allows larger batch size or sequence length with minimal accuracy drop.',
        'source': 'Derived from baseline to test memory limits on T4.'
    },
    '2epoch': {
        'lora_rank': 32,
        'alpha': 64,
        'epochs': 2,
        'lr': 2e-4,
        'target_modules': ['mixer.in_proj', 'mixer.out_proj', 'q_proj', 'k_proj', 'v_proj', 'o_proj'],
        'hypothesis': 'Training for 2 epochs might improve accuracy or lead to overfitting.',
        'source': 'Standard hyperparameter sweep.'
    },
    'curriculum': {
        'lora_rank': 32,
        'alpha': 64,
        'epochs': 1,
        'lr': 2e-4,
        'target_modules': ['mixer.in_proj', 'mixer.out_proj', 'q_proj', 'k_proj', 'v_proj', 'o_proj'],
        'hypothesis': 'Sorting data by difficulty might improve convergence.',
        'source': 'General ML knowledge / curriculum learning.'
    },
    'select2reason': {
        'lora_rank': 32,
        'alpha': 64,
        'epochs': 1,
        'lr': 2e-4,
        'target_modules': ['mixer.in_proj', 'mixer.out_proj', 'q_proj', 'k_proj', 'v_proj', 'o_proj'],
        'hypothesis': 'Select2Reason-style curation keeping only boxed-correct traces improves quality over quantity.',
        'source': 'technique-backlog.md:5'
    },
    'logprob_filter': {
        'lora_rank': 32,
        'alpha': 64,
        'epochs': 1,
        'lr': 2e-4,
        'target_modules': ['mixer.in_proj', 'mixer.out_proj', 'q_proj', 'k_proj', 'v_proj', 'o_proj'],
        'hypothesis': 'Filtering out low logprob generations improves training signal.',
        'source': 'winner-notebook_tinker.py.md (minlogprob references)'
    }
}
