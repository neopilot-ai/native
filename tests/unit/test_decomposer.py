import pytest

from core.token_forge.decomposer import decompose_prompt


def test_decompose_prompt_basic():
    """Test basic prompt decomposition."""
    prompt = "This is a simple prompt. It has two sentences."
    thinklets = decompose_prompt(prompt)
    assert len(thinklets) > 0
    assert all(isinstance(t, str) for t in thinklets)


def test_decompose_prompt_multiple_paragraphs():
    """Test decomposition of multi-paragraph prompts."""
    prompt = """First paragraph with multiple sentences. This is the second sentence.

Second paragraph here. Another sentence in this paragraph."""
    thinklets = decompose_prompt(prompt)
    assert len(thinklets) >= 2  # Should have at least 2 thinklets for 2 paragraphs


def test_decompose_prompt_empty():
    """Test decomposition of empty prompt."""
    thinklets = decompose_prompt("")
    assert thinklets == []


def test_decompose_prompt_single_sentence():
    """Test decomposition of single sentence prompt."""
    prompt = "Single sentence prompt."
    thinklets = decompose_prompt(prompt)
    assert len(thinklets) == 1
    assert thinklets[0] == prompt


def test_decompose_prompt_similarity_threshold():
    """Test decomposition with different similarity thresholds."""
    prompt = "First sentence. Second sentence. Third sentence."

    # High threshold should result in more thinklets
    high_threshold_thinklets = decompose_prompt(prompt, similarity_threshold=0.9)

    # Low threshold should result in fewer thinklets
    low_threshold_thinklets = decompose_prompt(prompt, similarity_threshold=0.5)

    # High threshold should generally produce more thinklets
    assert len(high_threshold_thinklets) >= len(low_threshold_thinklets)


if __name__ == "__main__":
    pytest.main([__file__])
