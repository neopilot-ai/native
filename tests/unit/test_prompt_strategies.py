import pytest

from core.meta_prompting.prompt_strategies import (
    MinimalistPrompting,
    ModularDecompositionPrompts,
    MultiShotChainOfThoughtGuidance,
)


def test_minimalist_prompting():
    strategy = MinimalistPrompting()
    prompt = "Test prompt."
    expected_output = "Minimalist approach: Test prompt."
    assert strategy.apply(prompt) == expected_output


def test_modular_decomposition_prompts():
    strategy = ModularDecompositionPrompts()
    prompt = "Test prompt."
    expected_output = "Decompose and conquer: Test prompt. Break this down into smaller, actionable steps."
    assert strategy.apply(prompt) == expected_output


def test_multi_shot_chain_of_thought_guidance():
    strategy = MultiShotChainOfThoughtGuidance()
    prompt = "Test prompt."
    expected_output = "Multi-shot and Chain-of-Thought: Test prompt. Think step-by-step and explain your reasoning."
    assert strategy.apply(prompt) == expected_output
