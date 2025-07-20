"""
Core evaluation scoring module for AI-native systems.

This module provides comprehensive scoring mechanisms for evaluating
AI outputs including embedding similarity, relevance, and redundancy detection.
"""

import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer

    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False


@dataclass
class EvaluationScore:
    """Structured evaluation score with multiple dimensions."""

    overall_score: float
    relevance_score: float
    coherence_score: float
    completeness_score: float
    embedding_similarity: Optional[float] = None
    redundancy_penalty: float = 0.0
    metadata: Dict[str, Any] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


class OutputScorer:
    """
    Advanced output scorer with multiple evaluation strategies.

    Supports:
    - Basic heuristic scoring
    - Embedding-based similarity scoring
    - Relevance and alignment scoring
    - Redundancy detection
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the scorer.

        Args:
            model_name: Name of the sentence transformer model for embeddings
        """
        self.model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                print(f"✅ Loaded embedding model: {model_name}")
            except Exception as e:
                print(f"⚠️  Failed to load embedding model: {e}")
                self.model = None
        else:
            print(
                "⚠️  sentence-transformers not available. Embedding features disabled."
            )

    def score_output(
        self,
        output: str,
        prompt: str,
        ideal_answer: Optional[str] = None,
        previous_outputs: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> EvaluationScore:
        """
        Comprehensive scoring of AI output.

        Args:
            output: The AI-generated output to score
            prompt: The original prompt/query
            ideal_answer: Optional ideal answer for similarity comparison
            previous_outputs: List of previous outputs for redundancy detection
            context: Additional context for scoring

        Returns:
            EvaluationScore: Comprehensive score object
        """

        # Basic heuristic scores
        relevance = self._score_relevance(output, prompt)
        coherence = self._score_coherence(output)
        completeness = self._score_completeness(output, prompt)

        # Embedding similarity (if available)
        embedding_sim = None
        if ideal_answer and self.model:
            embedding_sim = self._score_embedding_similarity(output, ideal_answer)

        # Redundancy penalty
        redundancy_penalty = 0.0
        if previous_outputs:
            redundancy_penalty = self._calculate_redundancy_penalty(
                output, previous_outputs
            )

        # Calculate overall score
        overall = self._calculate_overall_score(
            relevance, coherence, completeness, embedding_sim, redundancy_penalty
        )

        return EvaluationScore(
            overall_score=overall,
            relevance_score=relevance,
            coherence_score=coherence,
            completeness_score=completeness,
            embedding_similarity=embedding_sim,
            redundancy_penalty=redundancy_penalty,
            metadata={
                "prompt_length": len(prompt.split()),
                "output_length": len(output.split()),
                "has_ideal_answer": ideal_answer is not None,
                "context_provided": context is not None,
            },
        )

    def _score_relevance(self, output: str, prompt: str) -> float:
        """
        Score relevance between output and prompt.
        Uses keyword overlap and structural analysis.
        """
        if not output or not prompt:
            return 0.0

        # Simple keyword overlap method
        prompt_words = set(prompt.lower().split())
        output_words = set(output.lower().split())

        # Remove common stopwords
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "could",
        }

        prompt_content = prompt_words - stopwords
        output_content = output_words - stopwords

        if not prompt_content:
            return 0.5  # Neutral score if no content words

        overlap = len(prompt_content.intersection(output_content))
        relevance = overlap / len(prompt_content)

        # Boost score if output directly addresses prompt structure
        if any(
            word in output.lower() for word in ["therefore", "because", "thus", "so"]
        ):
            relevance += 0.1

        return min(1.0, relevance)

    def _score_coherence(self, output: str) -> float:
        """
        Score coherence and logical flow of the output.
        """
        if not output:
            return 0.0

        sentences = output.split(".")
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.7  # Single sentence gets moderate coherence

        score = 0.8  # Base coherence score

        # Check for transition words
        transitions = [
            "however",
            "therefore",
            "furthermore",
            "moreover",
            "additionally",
            "consequently",
            "meanwhile",
            "nonetheless",
            "thus",
            "hence",
        ]

        transition_count = sum(1 for word in transitions if word in output.lower())
        if transition_count > 0:
            score += 0.1 * min(transition_count, 2)

        # Penalize very short or very long sentences
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if 5 <= avg_sentence_length <= 25:
            score += 0.1

        return min(1.0, score)

    def _score_completeness(self, output: str, prompt: str) -> float:
        """
        Score how completely the output addresses the prompt.
        """
        if not output:
            return 0.0

        # Check if output has reasonable length relative to prompt complexity
        prompt_complexity = len(prompt.split())
        output_length = len(output.split())

        # Expected output length based on prompt
        expected_min = max(10, prompt_complexity * 0.5)
        expected_max = prompt_complexity * 5

        if output_length < expected_min:
            return 0.3  # Too short
        elif output_length > expected_max * 3:
            return 0.7  # Potentially too verbose
        else:
            return 0.9  # Good length

    def _score_embedding_similarity(self, output: str, ideal_answer: str) -> float:
        """
        Score similarity using sentence embeddings.
        """
        if not self.model or not output or not ideal_answer:
            return None

        try:
            output_embedding = self.model.encode([output])
            ideal_embedding = self.model.encode([ideal_answer])

            # Cosine similarity
            similarity = np.dot(output_embedding[0], ideal_embedding[0]) / (
                np.linalg.norm(output_embedding[0]) * np.linalg.norm(ideal_embedding[0])
            )

            # Normalize to 0-1 range
            return max(0.0, min(1.0, (similarity + 1) / 2))

        except Exception as e:
            print(f"Error calculating embedding similarity: {e}")
            return None

    def _calculate_redundancy_penalty(
        self, output: str, previous_outputs: List[str]
    ) -> float:
        """
        Calculate penalty for redundant content.
        """
        if not previous_outputs or not output:
            return 0.0

        output_words = set(output.lower().split())
        max_overlap = 0.0

        for prev_output in previous_outputs:
            if not prev_output:
                continue

            prev_words = set(prev_output.lower().split())
            if not prev_words:
                continue

            overlap = len(output_words.intersection(prev_words))
            overlap_ratio = overlap / min(len(output_words), len(prev_words))
            max_overlap = max(max_overlap, overlap_ratio)

        # Penalty increases with similarity
        if max_overlap > 0.8:
            return 0.5  # High penalty for near-duplicates
        elif max_overlap > 0.6:
            return 0.3  # Medium penalty
        elif max_overlap > 0.4:
            return 0.1  # Small penalty
        else:
            return 0.0  # No penalty

    def _calculate_overall_score(
        self,
        relevance: float,
        coherence: float,
        completeness: float,
        embedding_similarity: Optional[float],
        redundancy_penalty: float,
    ) -> float:
        """
        Calculate weighted overall score.
        """
        # Base weights
        weights = {
            "relevance": 0.4,
            "coherence": 0.2,
            "completeness": 0.2,
            "embedding": 0.2,
        }

        # Calculate base score
        base_score = (
            weights["relevance"] * relevance
            + weights["coherence"] * coherence
            + weights["completeness"] * completeness
        )

        # Add embedding similarity if available
        if embedding_similarity is not None:
            base_score += weights["embedding"] * embedding_similarity
        else:
            # Redistribute embedding weight to other components
            base_score *= 1.0 + weights["embedding"]

        # Apply redundancy penalty
        final_score = base_score * (1.0 - redundancy_penalty)

        return max(0.0, min(1.0, final_score))

    def batch_score(
        self,
        outputs_and_prompts: List[Tuple[str, str]],
        ideal_answers: Optional[List[str]] = None,
    ) -> List[EvaluationScore]:
        """
        Score multiple outputs in batch.

        Args:
            outputs_and_prompts: List of (output, prompt) tuples
            ideal_answers: Optional list of ideal answers

        Returns:
            List of EvaluationScore objects
        """
        scores = []
        previous_outputs = []

        for i, (output, prompt) in enumerate(outputs_and_prompts):
            ideal = (
                ideal_answers[i] if ideal_answers and i < len(ideal_answers) else None
            )

            score = self.score_output(
                output=output,
                prompt=prompt,
                ideal_answer=ideal,
                previous_outputs=previous_outputs.copy(),
            )

            scores.append(score)
            previous_outputs.append(output)

        return scores

    def export_scores(self, scores: List[EvaluationScore], filepath: str) -> None:
        """
        Export scores to JSON file.
        """
        scores_data = [asdict(score) for score in scores]

        with open(filepath, "w") as f:
            json.dump(
                {
                    "scores": scores_data,
                    "summary": {
                        "total_scores": len(scores),
                        "avg_overall": (
                            sum(s.overall_score for s in scores) / len(scores)
                            if scores
                            else 0
                        ),
                        "avg_relevance": (
                            sum(s.relevance_score for s in scores) / len(scores)
                            if scores
                            else 0
                        ),
                        "timestamp": datetime.now().isoformat(),
                    },
                },
                f,
                indent=2,
            )

        print(f"✅ Exported {len(scores)} scores to {filepath}")


def quick_score(output: str, prompt: str, **kwargs) -> float:
    """
    Quick scoring function for simple use cases.

    Returns just the overall score as a float.
    """
    scorer = OutputScorer()
    score = scorer.score_output(output, prompt, **kwargs)
    return score.overall_score


if __name__ == "__main__":
    # Demo usage
    scorer = OutputScorer()

    test_prompt = "Explain the concept of recursion in programming."
    test_output = "Recursion is a programming technique where a function calls itself to solve a problem by breaking it down into smaller, similar subproblems."

    score = scorer.score_output(test_output, test_prompt)

    print(f"Overall Score: {score.overall_score:.3f}")
    print(f"Relevance: {score.relevance_score:.3f}")
    print(f"Coherence: {score.coherence_score:.3f}")
    print(f"Completeness: {score.completeness_score:.3f}")
