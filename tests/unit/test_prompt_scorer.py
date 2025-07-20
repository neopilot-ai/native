import pytest

from core.meta_prompting.prompt_scorer import PromptScore, PromptScorer, PromptType


def test_prompt_scorer_initialization():
    """Test prompt scorer initialization."""
    scorer = PromptScorer()
    assert scorer is not None
    assert hasattr(scorer, "scoring_history")
    assert hasattr(scorer, "type_weights")


def test_score_prompt_basic():
    """Test basic prompt scoring."""
    scorer = PromptScorer()
    prompt = "Write a function to calculate fibonacci numbers."

    result = scorer.score_prompt(prompt, prompt_id="test_1")

    assert isinstance(result, PromptScore)
    assert result.prompt_id == "test_1"
    assert 0.0 <= result.overall_score <= 1.0
    assert result.prompt_type in PromptType


def test_score_prompt_instruction_type():
    """Test scoring of instruction-type prompts."""
    scorer = PromptScorer()
    prompt = "Please implement a binary search algorithm in Python."

    result = scorer.score_prompt(prompt, prompt_id="test_instruction")

    assert result.prompt_type == PromptType.INSTRUCTION
    assert result.clarity_score > 0.0
    assert result.usefulness_score > 0.0


def test_score_prompt_question_type():
    """Test scoring of question-type prompts."""
    scorer = PromptScorer()
    prompt = "What are the advantages of using machine learning in healthcare?"

    result = scorer.score_prompt(prompt, prompt_id="test_question")

    assert result.prompt_type == PromptType.QUESTION
    assert result.clarity_score > 0.0


def test_score_prompt_creative_type():
    """Test scoring of creative-type prompts."""
    scorer = PromptScorer()
    prompt = "Create a story about a robot learning to paint."

    result = scorer.score_prompt(prompt, prompt_id="test_creative")

    assert result.prompt_type == PromptType.CREATIVE
    assert result.completeness_score > 0.0


def test_score_prompt_analytical_type():
    """Test scoring of analytical-type prompts."""
    scorer = PromptScorer()
    prompt = "Analyze the performance implications of using recursion vs iteration for sorting algorithms."

    result = scorer.score_prompt(prompt, prompt_id="test_analytical")

    assert result.prompt_type == PromptType.ANALYTICAL
    assert result.logical_consistency_score > 0.0


def test_score_prompt_system_type():
    """Test scoring of system-type prompts."""
    scorer = PromptScorer()
    prompt = "You are an expert software engineer. Always provide code examples and explain your reasoning."

    result = scorer.score_prompt(prompt, prompt_id="test_system")

    assert result.prompt_type == PromptType.SYSTEM
    assert result.clarity_score > 0.0


def test_score_prompt_meta_type():
    """Test scoring of meta-type prompts."""
    scorer = PromptScorer()
    prompt = "Reflect on the effectiveness of your previous responses and suggest improvements."

    result = scorer.score_prompt(prompt, prompt_id="test_meta")

    assert result.prompt_type == PromptType.META
    assert result.usefulness_score > 0.0


def test_batch_score_prompts():
    """Test batch scoring of multiple prompts."""
    scorer = PromptScorer()
    prompts = [
        "Write a function to sort a list.",
        "What is machine learning?",
        "Create a poem about technology.",
    ]

    results = scorer.batch_score_prompts(
        prompts, prompt_ids=["batch_1", "batch_2", "batch_3"]
    )

    assert len(results) == 3
    assert all(isinstance(r, PromptScore) for r in results)
    assert all(0.0 <= r.overall_score <= 1.0 for r in results)


def test_get_scoring_summary():
    """Test getting scoring summary."""
    scorer = PromptScorer()

    # Score some prompts first
    scorer.score_prompt("Test prompt 1", prompt_id="summary_1")
    scorer.score_prompt("Test prompt 2", prompt_id="summary_2")

    summary = scorer.get_scoring_summary()

    assert "total_prompts" in summary
    assert "average_score" in summary
    assert "score_distribution" in summary
    assert summary["total_prompts"] == 2


def test_export_scores():
    """Test exporting scores to file."""
    import json
    import os
    import tempfile

    scorer = PromptScorer()
    scorer.score_prompt("Test export prompt", prompt_id="export_test")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_file = f.name

    try:
        scorer.export_scores(temp_file)

        # Check if file was created and contains valid JSON
        assert os.path.exists(temp_file)
        with open(temp_file, "r") as f:
            data = json.load(f)
            assert "scores" in data
            assert "summary" in data

    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__])
