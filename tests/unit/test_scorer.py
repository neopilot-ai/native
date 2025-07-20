"""
Unit tests for the evaluation scorer module.
"""

import os
import tempfile

import pytest

from core.eval_core.scorer import EvaluationScore, OutputScorer, quick_score


class TestOutputScorer:
    """Test cases for OutputScorer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = OutputScorer()

    def test_scorer_initialization(self):
        """Test scorer initializes correctly."""
        assert self.scorer is not None
        # Model may or may not be available depending on dependencies

    def test_score_output_basic(self):
        """Test basic output scoring functionality."""
        prompt = "Explain the concept of recursion in programming."
        output = "Recursion is a programming technique where a function calls itself to solve problems."

        score = self.scorer.score_output(output, prompt)

        assert isinstance(score, EvaluationScore)
        assert 0.0 <= score.overall_score <= 1.0
        assert 0.0 <= score.relevance_score <= 1.0
        assert 0.0 <= score.coherence_score <= 1.0
        assert 0.0 <= score.completeness_score <= 1.0
        assert score.timestamp is not None

    def test_score_relevance(self):
        """Test relevance scoring."""
        prompt = "What is machine learning?"

        # High relevance output
        relevant_output = "Machine learning is a subset of artificial intelligence that enables systems to learn from data."
        score_relevant = self.scorer._score_relevance(relevant_output, prompt)

        # Low relevance output
        irrelevant_output = "The weather is nice today and I like pizza."
        score_irrelevant = self.scorer._score_relevance(irrelevant_output, prompt)

        assert score_relevant > score_irrelevant
        assert 0.0 <= score_relevant <= 1.0
        assert 0.0 <= score_irrelevant <= 1.0

    def test_score_coherence(self):
        """Test coherence scoring."""
        # Coherent text
        coherent_text = "First, we analyze the problem. Then, we develop a solution. Finally, we implement it."
        coherence_high = self.scorer._score_coherence(coherent_text)

        # Incoherent text
        incoherent_text = "Random words. No connection. Completely scattered thoughts."
        coherence_low = self.scorer._score_coherence(incoherent_text)

        assert coherence_high > coherence_low
        assert 0.0 <= coherence_high <= 1.0
        assert 0.0 <= coherence_low <= 1.0

    def test_score_completeness(self):
        """Test completeness scoring."""
        prompt = "Describe the process of photosynthesis in plants."

        # Complete answer
        complete_output = "Photosynthesis is the process by which plants convert sunlight, carbon dioxide, and water into glucose and oxygen. This occurs in chloroplasts using chlorophyll."
        completeness_high = self.scorer._score_completeness(complete_output, prompt)

        # Incomplete answer
        incomplete_output = "Plants use sunlight."
        completeness_low = self.scorer._score_completeness(incomplete_output, prompt)

        assert completeness_high > completeness_low

    def test_redundancy_penalty(self):
        """Test redundancy penalty calculation."""
        output = "Machine learning is a type of AI technology."
        previous_outputs = [
            "Machine learning is a type of AI technology.",  # Duplicate
            "Deep learning is a subset of machine learning.",  # Related but different
        ]

        penalty = self.scorer._calculate_redundancy_penalty(output, previous_outputs)
        assert penalty > 0.0  # Should have penalty for duplicate
        assert penalty <= 1.0

    def test_batch_scoring(self):
        """Test batch scoring functionality."""
        outputs_and_prompts = [
            ("Python is a programming language.", "What is Python?"),
            ("Machine learning uses algorithms.", "Explain machine learning."),
            ("Recursion calls itself.", "What is recursion?"),
        ]

        scores = self.scorer.batch_score(outputs_and_prompts)

        assert len(scores) == 3
        assert all(isinstance(score, EvaluationScore) for score in scores)
        assert all(0.0 <= score.overall_score <= 1.0 for score in scores)

    def test_export_scores(self):
        """Test score export functionality."""
        # Generate some scores
        prompt = "What is AI?"
        output = "AI is artificial intelligence."
        score = self.scorer.score_output(output, prompt)

        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            self.scorer.export_scores([score], temp_path)
            assert os.path.exists(temp_path)

            # Check file is not empty
            with open(temp_path, "r") as f:
                content = f.read()
                assert len(content) > 0
                assert "scores" in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        score = self.scorer.score_output("", "")
        assert score.overall_score == 0.0

        score = self.scorer.score_output("Valid output", "")
        assert score.relevance_score == 0.0

    def test_score_with_ideal_answer(self):
        """Test scoring with ideal answer comparison."""
        prompt = "What is 2+2?"
        output = "2+2 equals 4"
        ideal = "The answer is 4"

        score = self.scorer.score_output(output, prompt, ideal_answer=ideal)
        assert isinstance(score, EvaluationScore)
        # embedding_similarity might be None if model not available

    def test_metadata_inclusion(self):
        """Test that metadata is properly included in scores."""
        prompt = "Test prompt"
        output = "Test output"

        score = self.scorer.score_output(output, prompt)

        assert "prompt_length" in score.metadata
        assert "output_length" in score.metadata
        assert score.metadata["prompt_length"] == len(prompt.split())
        assert score.metadata["output_length"] == len(output.split())


class TestQuickScore:
    """Test cases for quick_score function."""

    def test_quick_score_returns_float(self):
        """Test that quick_score returns a float."""
        result = quick_score("Test output", "Test prompt")
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_quick_score_consistency(self):
        """Test that quick_score is consistent with full scoring."""
        output = "Machine learning is AI"
        prompt = "What is machine learning?"

        quick_result = quick_score(output, prompt)

        scorer = OutputScorer()
        full_result = scorer.score_output(output, prompt)

        assert quick_result == full_result.overall_score


@pytest.fixture
def sample_scores():
    """Fixture providing sample evaluation scores for testing."""
    scorer = OutputScorer()

    test_cases = [
        ("Python is a programming language", "What is Python?"),
        ("Machine learning uses data to learn", "Explain machine learning"),
        ("The sky is blue", "What color is the sky?"),
    ]

    scores = []
    for output, prompt in test_cases:
        score = scorer.score_output(output, prompt)
        scores.append(score)

    return scores


def test_evaluation_score_dataclass(sample_scores):
    """Test EvaluationScore dataclass properties."""
    score = sample_scores[0]

    assert hasattr(score, "overall_score")
    assert hasattr(score, "relevance_score")
    assert hasattr(score, "coherence_score")
    assert hasattr(score, "completeness_score")
    assert hasattr(score, "timestamp")
    assert hasattr(score, "metadata")

    # Test timestamp is set
    assert score.timestamp is not None
    assert len(score.timestamp) > 0


if __name__ == "__main__":
    pytest.main([__file__])
