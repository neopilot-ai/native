"""
Meta-prompting scoring system for AI-native systems.

Provides chain-of-thought grading and evaluation of meta prompts
based on usefulness, tone, logical consistency, and effectiveness.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class PromptType(Enum):
    """Types of prompts for specialized scoring."""

    INSTRUCTION = "instruction"
    QUESTION = "question"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    SYSTEM = "system"
    META = "meta"


@dataclass
class PromptScore:
    """Comprehensive prompt scoring results."""

    prompt_id: str
    prompt_text: str
    prompt_type: PromptType

    # Core dimensions
    clarity_score: float  # How clear and unambiguous the prompt is
    usefulness_score: float  # How useful the prompt is for its purpose
    logical_consistency: float  # Internal logical consistency
    tone_appropriateness: float  # Appropriate tone for the context
    completeness_score: float  # How complete/comprehensive the prompt is

    # Meta-analysis
    effectiveness_score: float  # Predicted effectiveness
    overall_score: float  # Weighted overall score

    # Chain of thought reasoning
    reasoning: Dict[str, str]  # Explanations for each score
    recommendations: List[str]  # Improvement suggestions

    # Metadata
    timestamp: str
    metadata: Dict[str, Any]

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class PromptScorer:
    """
    Meta-prompting scorer with chain-of-thought evaluation.

    Evaluates prompts across multiple dimensions using structured reasoning
    and provides actionable feedback for improvement.
    """

    def __init__(self):
        """Initialize the prompt scorer."""
        self.scoring_history = []

        # Scoring weights for different prompt types
        self.type_weights = {
            PromptType.INSTRUCTION: {
                "clarity": 0.25,
                "usefulness": 0.20,
                "logical_consistency": 0.20,
                "tone_appropriateness": 0.15,
                "completeness": 0.20,
            },
            PromptType.QUESTION: {
                "clarity": 0.30,
                "usefulness": 0.25,
                "logical_consistency": 0.15,
                "tone_appropriateness": 0.10,
                "completeness": 0.20,
            },
            PromptType.CREATIVE: {
                "clarity": 0.15,
                "usefulness": 0.20,
                "logical_consistency": 0.10,
                "tone_appropriateness": 0.25,
                "completeness": 0.30,
            },
            PromptType.ANALYTICAL: {
                "clarity": 0.20,
                "usefulness": 0.25,
                "logical_consistency": 0.30,
                "tone_appropriateness": 0.10,
                "completeness": 0.15,
            },
            PromptType.SYSTEM: {
                "clarity": 0.30,
                "usefulness": 0.25,
                "logical_consistency": 0.25,
                "tone_appropriateness": 0.05,
                "completeness": 0.15,
            },
            PromptType.META: {
                "clarity": 0.20,
                "usefulness": 0.30,
                "logical_consistency": 0.25,
                "tone_appropriateness": 0.05,
                "completeness": 0.20,
            },
        }

    def classify_prompt_type(self, prompt: str) -> PromptType:
        """
        Classify the type of prompt based on content analysis.

        Args:
            prompt: The prompt text to classify

        Returns:
            PromptType: The classified prompt type
        """
        prompt_lower = prompt.lower()

        # System prompt indicators
        if any(
            word in prompt_lower
            for word in ["you are", "act as", "role:", "system:", "behave like"]
        ):
            return PromptType.SYSTEM

        # Meta prompt indicators
        if any(
            word in prompt_lower
            for word in ["evaluate", "analyze this prompt", "improve this", "meta"]
        ):
            return PromptType.META

        # Creative prompt indicators
        if any(
            word in prompt_lower
            for word in ["create", "write a story", "imagine", "design", "creative"]
        ):
            return PromptType.CREATIVE

        # Analytical prompt indicators
        if any(
            word in prompt_lower
            for word in ["analyze", "compare", "evaluate", "assess", "examine"]
        ):
            return PromptType.ANALYTICAL

        # Question indicators
        if any(prompt.strip().endswith(char) for char in ["?"]):
            return PromptType.QUESTION

        # Question words at start
        if any(
            prompt_lower.startswith(word)
            for word in ["what", "how", "why", "when", "where", "who", "which"]
        ):
            return PromptType.QUESTION

        # Default to instruction
        return PromptType.INSTRUCTION

    def score_clarity(self, prompt: str, prompt_type: PromptType) -> Tuple[float, str]:
        """
        Score prompt clarity using chain-of-thought reasoning.

        Returns:
            Tuple of (score, reasoning)
        """
        score = 0.5  # Base score
        reasons = []

        # Length analysis
        word_count = len(prompt.split())
        if word_count < 5:
            score -= 0.2
            reasons.append("Very short prompt may lack clarity")
        elif word_count > 100:
            score -= 0.1
            reasons.append("Very long prompt may be unclear")
        elif 10 <= word_count <= 30:
            score += 0.1
            reasons.append("Good length for clarity")

        # Ambiguity indicators
        ambiguous_words = ["something", "anything", "maybe", "perhaps", "possibly"]
        if any(word in prompt.lower() for word in ambiguous_words):
            score -= 0.15
            reasons.append("Contains ambiguous language")

        # Clear structure indicators
        if any(marker in prompt for marker in ["1.", "2.", "-", "*", ":"]):
            score += 0.1
            reasons.append("Has structured formatting")

        # Question marks for non-questions
        if prompt_type != PromptType.QUESTION and "?" in prompt:
            score -= 0.05
            reasons.append("Mixed question/instruction format may confuse")

        # Specific terms
        specific_indicators = ["specific", "exactly", "precisely", "detailed"]
        if any(word in prompt.lower() for word in specific_indicators):
            score += 0.1
            reasons.append("Uses specific language")

        # Normalize score
        score = max(0.0, min(1.0, score))

        reasoning = "; ".join(reasons) if reasons else "Standard clarity assessment"
        return score, reasoning

    def score_usefulness(
        self, prompt: str, prompt_type: PromptType
    ) -> Tuple[float, str]:
        """Score prompt usefulness for its intended purpose."""
        score = 0.6  # Base score
        reasons = []

        # Context provision
        if any(
            word in prompt.lower() for word in ["context:", "background:", "given that"]
        ):
            score += 0.15
            reasons.append("Provides helpful context")

        # Clear objective
        action_words = [
            "create",
            "analyze",
            "explain",
            "describe",
            "compare",
            "evaluate",
        ]
        if any(word in prompt.lower() for word in action_words):
            score += 0.1
            reasons.append("Has clear action objective")

        # Constraints and requirements
        if any(
            phrase in prompt.lower()
            for phrase in ["must include", "should contain", "requirements"]
        ):
            score += 0.1
            reasons.append("Specifies requirements")

        # Output format specification
        format_words = ["format:", "list", "table", "json", "steps", "bullet points"]
        if any(word in prompt.lower() for word in format_words):
            score += 0.1
            reasons.append("Specifies output format")

        # Vague requests
        vague_phrases = ["do something about", "help with", "tell me about"]
        if any(phrase in prompt.lower() for phrase in vague_phrases):
            score -= 0.2
            reasons.append("Contains vague requests")

        score = max(0.0, min(1.0, score))
        reasoning = "; ".join(reasons) if reasons else "Standard usefulness assessment"
        return score, reasoning

    def score_logical_consistency(
        self, prompt: str, prompt_type: PromptType
    ) -> Tuple[float, str]:
        """Score logical consistency and coherence."""
        score = 0.7  # Base score
        reasons = []

        # Contradictory instructions
        contradictions = [
            ("short", "detailed"),
            ("brief", "comprehensive"),
            ("simple", "complex"),
            ("quick", "thorough"),
        ]

        prompt_lower = prompt.lower()
        for word1, word2 in contradictions:
            if word1 in prompt_lower and word2 in prompt_lower:
                score -= 0.2
                reasons.append(
                    f"Contains potentially contradictory terms: {word1}/{word2}"
                )

        # Logical flow indicators
        flow_words = ["first", "then", "next", "finally", "because", "therefore"]
        if any(word in prompt_lower for word in flow_words):
            score += 0.1
            reasons.append("Shows logical flow")

        # Multiple conflicting tasks
        task_count = sum(
            1
            for word in ["create", "analyze", "explain", "write"]
            if word in prompt_lower
        )
        if task_count > 2:
            score -= 0.1
            reasons.append("Multiple tasks may lack focus")

        score = max(0.0, min(1.0, score))
        reasoning = "; ".join(reasons) if reasons else "Standard consistency assessment"
        return score, reasoning

    def score_tone_appropriateness(
        self, prompt: str, prompt_type: PromptType
    ) -> Tuple[float, str]:
        """Score appropriateness of tone."""
        score = 0.7  # Base score
        reasons = []

        # Politeness indicators
        polite_words = ["please", "kindly", "would you", "could you"]
        if any(word in prompt.lower() for word in polite_words):
            score += 0.1
            reasons.append("Uses polite language")

        # Aggressive or demanding tone
        demanding_words = ["must", "immediately", "urgent", "demand"]
        if any(word in prompt.lower() for word in demanding_words):
            score -= 0.15
            reasons.append("May have overly demanding tone")

        # Professional tone
        if prompt_type in [PromptType.SYSTEM, PromptType.ANALYTICAL]:
            professional_indicators = ["analyze", "evaluate", "assess", "provide"]
            if any(word in prompt.lower() for word in professional_indicators):
                score += 0.1
                reasons.append("Maintains professional tone")

        # Casual tone for creative prompts
        if prompt_type == PromptType.CREATIVE:
            casual_indicators = ["fun", "creative", "imagine", "let's"]
            if any(word in prompt.lower() for word in casual_indicators):
                score += 0.1
                reasons.append("Appropriate casual tone for creative task")

        score = max(0.0, min(1.0, score))
        reasoning = "; ".join(reasons) if reasons else "Standard tone assessment"
        return score, reasoning

    def score_completeness(
        self, prompt: str, prompt_type: PromptType
    ) -> Tuple[float, str]:
        """Score completeness of the prompt."""
        score = 0.5  # Base score
        reasons = []

        # Essential components for different types
        if prompt_type == PromptType.INSTRUCTION:
            required = ["what to do", "how to do it"]  # Simplified check
            if "what" in prompt.lower() or "how" in prompt.lower():
                score += 0.2
                reasons.append("Contains action specification")

        if prompt_type == PromptType.QUESTION:
            if any(
                word in prompt.lower()
                for word in ["what", "how", "why", "when", "where"]
            ):
                score += 0.2
                reasons.append("Has clear interrogative")

        # Context completeness
        if len(prompt.split()) > 20:  # Longer prompts likely more complete
            score += 0.1
            reasons.append("Substantial content suggests completeness")

        # Examples or constraints
        if any(
            word in prompt.lower()
            for word in ["example", "instance", "such as", "like"]
        ):
            score += 0.15
            reasons.append("Provides examples for clarity")

        # Missing critical elements
        if prompt_type == PromptType.CREATIVE and "create" not in prompt.lower():
            score -= 0.1
            reasons.append("Creative prompt lacks creation directive")

        score = max(0.0, min(1.0, score))
        reasoning = (
            "; ".join(reasons) if reasons else "Standard completeness assessment"
        )
        return score, reasoning

    def calculate_effectiveness(
        self, scores: Dict[str, float], prompt_type: PromptType
    ) -> float:
        """Calculate predicted effectiveness based on component scores."""
        weights = self.type_weights[prompt_type]

        effectiveness = (
            weights["clarity"] * scores["clarity"]
            + weights["usefulness"] * scores["usefulness"]
            + weights["logical_consistency"] * scores["logical_consistency"]
            + weights["tone_appropriateness"] * scores["tone_appropriateness"]
            + weights["completeness"] * scores["completeness"]
        )

        return effectiveness

    def generate_recommendations(
        self, scores: Dict[str, float], reasoning: Dict[str, str]
    ) -> List[str]:
        """Generate improvement recommendations based on scores."""
        recommendations = []

        if scores["clarity"] < 0.6:
            recommendations.append(
                "Improve clarity: Use more specific language and reduce ambiguity"
            )

        if scores["usefulness"] < 0.6:
            recommendations.append(
                "Enhance usefulness: Add context and specify desired outcomes"
            )

        if scores["logical_consistency"] < 0.6:
            recommendations.append(
                "Improve consistency: Remove contradictory requirements"
            )

        if scores["tone_appropriateness"] < 0.6:
            recommendations.append("Adjust tone: Match formality to the task type")

        if scores["completeness"] < 0.6:
            recommendations.append(
                "Increase completeness: Add missing requirements or context"
            )

        # General recommendations based on low overall score
        overall = sum(scores.values()) / len(scores)
        if overall < 0.5:
            recommendations.append(
                "Consider restructuring the prompt with clearer objectives"
            )

        return recommendations

    def score_prompt(
        self,
        prompt: str,
        prompt_id: Optional[str] = None,
        prompt_type: Optional[PromptType] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PromptScore:
        """
        Comprehensive prompt scoring with chain-of-thought reasoning.

        Args:
            prompt: The prompt text to score
            prompt_id: Optional identifier for the prompt
            prompt_type: Optional manual classification (auto-detected if None)
            metadata: Optional additional metadata

        Returns:
            PromptScore: Comprehensive scoring results
        """
        if prompt_id is None:
            prompt_id = f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if prompt_type is None:
            prompt_type = self.classify_prompt_type(prompt)

        # Score individual dimensions
        clarity_score, clarity_reason = self.score_clarity(prompt, prompt_type)
        usefulness_score, usefulness_reason = self.score_usefulness(prompt, prompt_type)
        consistency_score, consistency_reason = self.score_logical_consistency(
            prompt, prompt_type
        )
        tone_score, tone_reason = self.score_tone_appropriateness(prompt, prompt_type)
        completeness_score, completeness_reason = self.score_completeness(
            prompt, prompt_type
        )

        # Compile scores
        scores = {
            "clarity": clarity_score,
            "usefulness": usefulness_score,
            "logical_consistency": consistency_score,
            "tone_appropriateness": tone_score,
            "completeness": completeness_score,
        }

        reasoning = {
            "clarity": clarity_reason,
            "usefulness": usefulness_reason,
            "logical_consistency": consistency_reason,
            "tone_appropriateness": tone_reason,
            "completeness": completeness_reason,
        }

        # Calculate derived scores
        effectiveness_score = self.calculate_effectiveness(scores, prompt_type)
        overall_score = (sum(scores.values()) + effectiveness_score) / (len(scores) + 1)

        # Generate recommendations
        recommendations = self.generate_recommendations(scores, reasoning)

        # Create result
        result = PromptScore(
            prompt_id=prompt_id,
            prompt_text=prompt,
            prompt_type=prompt_type,
            clarity_score=clarity_score,
            usefulness_score=usefulness_score,
            logical_consistency=consistency_score,
            tone_appropriateness=tone_score,
            completeness_score=completeness_score,
            effectiveness_score=effectiveness_score,
            overall_score=overall_score,
            reasoning=reasoning,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {},
        )

        # Store in history
        self.scoring_history.append(result)

        return result

    def batch_score(self, prompts: List[str]) -> List[PromptScore]:
        """Score multiple prompts in batch."""
        results = []
        for i, prompt in enumerate(prompts):
            result = self.score_prompt(prompt, prompt_id=f"batch_{i}")
            results.append(result)
        return results

    def get_scoring_summary(self) -> Dict[str, Any]:
        """Get summary statistics from scoring history."""
        if not self.scoring_history:
            return {"message": "No scoring history available"}

        scores = [s.overall_score for s in self.scoring_history]

        return {
            "total_prompts_scored": len(self.scoring_history),
            "average_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "score_distribution": {
                "excellent (>0.8)": len([s for s in scores if s > 0.8]),
                "good (0.6-0.8)": len([s for s in scores if 0.6 <= s <= 0.8]),
                "needs_improvement (<0.6)": len([s for s in scores if s < 0.6]),
            },
            "common_recommendations": self._get_common_recommendations(),
        }

    def _get_common_recommendations(self) -> List[str]:
        """Get most common recommendations from history."""
        all_recommendations = []
        for result in self.scoring_history:
            all_recommendations.extend(result.recommendations)

        # Count frequency
        rec_count = {}
        for rec in all_recommendations:
            rec_count[rec] = rec_count.get(rec, 0) + 1

        # Sort by frequency and return top 5
        sorted_recs = sorted(rec_count.items(), key=lambda x: x[1], reverse=True)
        return [rec for rec, count in sorted_recs[:5]]

    def export_scores(self, filepath: str) -> None:
        """Export scoring history to JSON file."""
        export_data = {
            "scoring_history": [asdict(score) for score in self.scoring_history],
            "summary": self.get_scoring_summary(),
            "export_timestamp": datetime.now().isoformat(),
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"✅ Exported {len(self.scoring_history)} prompt scores to {filepath}")


def quick_score_prompt(prompt: str) -> float:
    """Quick scoring function that returns just the overall score."""
    scorer = PromptScorer()
    result = scorer.score_prompt(prompt)
    return result.overall_score


if __name__ == "__main__":
    # Demo usage
    scorer = PromptScorer()

    test_prompts = [
        "Write a story about a robot.",
        "Please analyze the economic impacts of renewable energy adoption, considering both short-term costs and long-term benefits, and provide a structured report with specific examples.",
        "Do something with data analysis maybe?",
        "What are the key differences between machine learning and artificial intelligence?",
    ]

    print("🧠 Meta-Prompt Scoring Demo")
    print("=" * 40)

    for i, prompt in enumerate(test_prompts, 1):
        result = scorer.score_prompt(prompt, prompt_id=f"demo_{i}")

        print(f'\n{i}. Prompt: "{prompt}"')
        print(f"   Type: {result.prompt_type.value}")
        print(f"   Overall Score: {result.overall_score:.3f}")
        print(f"   Clarity: {result.clarity_score:.3f}")
        print(f"   Usefulness: {result.usefulness_score:.3f}")
        print(f"   Effectiveness: {result.effectiveness_score:.3f}")

        if result.recommendations:
            print("   Recommendations:")
            for rec in result.recommendations[:2]:  # Show first 2
                print(f"   • {rec}")

    print(f"\n📊 Summary:")
    summary = scorer.get_scoring_summary()
    print(f"   Average Score: {summary['average_score']:.3f}")
    print(
        f"   Prompts Needing Improvement: {summary['score_distribution']['needs_improvement (<0.6)']}"
    )
