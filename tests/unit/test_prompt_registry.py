import pytest

from core.meta_prompting.prompt_registry import PromptEvaluationSystem, PromptRegistry


def test_prompt_registry_register_and_get():
    registry = PromptRegistry()
    registry.register_prompt("test_prompt", "This is a test prompt.", category="test")
    retrieved_prompt = registry.get_prompt("test_prompt")
    assert retrieved_prompt is not None
    assert retrieved_prompt["content"] == "This is a test prompt."
    assert retrieved_prompt["category"] == "test"
    assert retrieved_prompt["metadata"] == {}


def test_prompt_registry_duplicate_registration():
    registry = PromptRegistry()
    registry.register_prompt("test_prompt", "Content 1")
    with pytest.raises(
        ValueError, match="Prompt with name 'test_prompt' already exists."
    ):
        registry.register_prompt("test_prompt", "Content 2")


def test_prompt_registry_list_prompts():
    registry = PromptRegistry()
    registry.register_prompt("prompt1", "Content 1", category="cat1")
    registry.register_prompt("prompt2", "Content 2", category="cat2")
    registry.register_prompt("prompt3", "Content 3", category="cat1")

    all_prompts = registry.list_prompts()
    assert len(all_prompts) == 3
    assert "prompt1" in all_prompts
    assert "prompt2" in all_prompts
    assert "prompt3" in all_prompts

    cat1_prompts = registry.list_prompts(category="cat1")
    assert len(cat1_prompts) == 2
    assert "prompt1" in cat1_prompts
    assert "prompt3" in cat1_prompts
    assert "prompt2" not in cat1_prompts


def test_prompt_evaluation_system_length_limit():
    evaluator = PromptEvaluationSystem()
    criteria = {"length_limit": 10}

    # Test within limit
    results = evaluator.evaluate_prompt("short", criteria)
    assert results["score"] == 1
    assert "Prompt exceeds length limit." not in results["feedback"]

    # Test exceeding limit
    results = evaluator.evaluate_prompt("this is a long prompt", criteria)
    assert results["score"] == -1
    assert "Prompt exceeds length limit." in results["feedback"]


def test_prompt_evaluation_system_keywords():
    evaluator = PromptEvaluationSystem()
    criteria = {"keywords": ["apple", "banana"]}

    # All keywords found
    results = evaluator.evaluate_prompt("I like apple and banana.", criteria)
    assert results["score"] == 2
    assert "All keywords found." in results["feedback"]

    # Some keywords found
    results = evaluator.evaluate_prompt("I like apple.", criteria)
    assert results["score"] == 1
    assert "Some keywords found: apple." in results["feedback"]

    # No keywords found
    results = evaluator.evaluate_prompt("I like orange.", criteria)
    assert results["score"] == 0
    assert "No keywords found." in results["feedback"]


def test_prompt_evaluation_system_clarity_check():
    evaluator = PromptEvaluationSystem()
    criteria = {"clarity_check": True}

    results = evaluator.evaluate_prompt("Any prompt content.", criteria)
    assert results["score"] == 1
    assert "Clarity check applied (mock)." in results["feedback"]


def test_prompt_evaluation_system_combined_criteria():
    evaluator = PromptEvaluationSystem()
    criteria = {
        "length_limit": 30,  # Increased length limit
        "keywords": ["test", "system"],
        "clarity_check": True,
    }

    # All criteria met
    results = evaluator.evaluate_prompt("This is a test for the system.", criteria)
    assert results["score"] == 4  # 1 (length) + 2 (keywords) + 1 (clarity)
    assert "Prompt exceeds length limit." not in results["feedback"]
    assert "All keywords found." in results["feedback"]
    assert "Clarity check applied (mock)." in results["feedback"]

    # Some criteria not met
    results = evaluator.evaluate_prompt(
        "This is a very very very long prompt without keywords.", criteria
    )
    assert results["score"] == 0  # -1 (length) + 0 (keywords) + 1 (clarity)
    assert "Prompt exceeds length limit." in results["feedback"]
    assert "No keywords found." in results["feedback"]
    assert "Clarity check applied (mock)." in results["feedback"]
