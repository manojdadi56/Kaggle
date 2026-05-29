"""Autonomous Kaggle-competition orchestrator.

Actors: a local tick loop (this package) triggers Jules (worker) and Claude
Code headless (operator), drives a pluggable GPU-executor registry, keeps
event-sourced state in git, and submits within a budget.

All external integrations use dependency-injected transports so the whole
system is testable offline with zero network calls.
"""

__version__ = "0.1.0"
