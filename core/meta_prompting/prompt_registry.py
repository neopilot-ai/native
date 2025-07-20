"""
This module implements a Prompt Registry for managing and retrieving various prompts,
and a basic Prompt Evaluation System.
"""

from typing import Any, Dict, Optional


class PromptRegistry:
    """
    Manages a collection of prompts, allowing for registration, retrieval, and categorization.
    """

    def __init__(self):
        self._prompts: Dict[str, Dict[str, Any]] = {}

    def register_prompt(
        self,
        name: str,
        content: str,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Registers a new prompt with a given name, content, category, and optional metadata.
        """
        if name in self._prompts:
            raise ValueError(f"Prompt with name '{name}' already exists.")

        prompt_data = {
            "content": content,
            "category": category,
            "metadata": metadata if metadata is not None else {},
        }
        self._prompts[name] = prompt_data

    def get_prompt(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a prompt by its registered name.
        """
        return self._prompts.get(name)

    def list_prompts(self, category: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Lists all registered prompts, optionally filtered by category.
        """
        if category:
            return {
                name: data
                for name, data in self._prompts.items()
                if data["category"] == category
            }
        return self._prompts


class PromptEvaluationSystem:
    """
    A basic system for evaluating prompts based on predefined criteria.
    This is a placeholder and would be expanded with more sophisticated metrics.
    """

    def evaluate_prompt(
        self, prompt_content: str, criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluates a prompt against given criteria.
        For now, it's a mock evaluation.
        """
        score = 0
        feedback = []

        if "length_limit" in criteria:
            if len(prompt_content) <= criteria["length_limit"]:
                score += 1
            else:
                score -= 1
                feedback.append("Prompt exceeds length limit.")

        if "keywords" in criteria:
            found_keywords = [kw for kw in criteria["keywords"] if kw in prompt_content]
            if len(found_keywords) == len(criteria["keywords"]):
                score += 2
                feedback.append("All keywords found.")
            elif found_keywords:
                score += 1
                feedback.append(f"Some keywords found: {', '.join(found_keywords)}.")
            else:
                feedback.append("No keywords found.")

        # Placeholder for more complex evaluation logic (e.g., semantic analysis, coherence)
        if "clarity_check" in criteria and criteria["clarity_check"]:
            # In a real system, this would involve NLP techniques
            score += 1
            feedback.append("Clarity check applied (mock).")

        return {"score": score, "feedback": feedback}


# Example Usage (for demonstration purposes)
if __name__ == "__main__":
    registry = PromptRegistry()
    evaluator = PromptEvaluationSystem()

    # Registering prompts
    registry.register_prompt(
        "greeting_prompt",
        "Hello, how can I assist you today?",
        category="conversational",
        metadata={"version": "1.0"},
    )
    registry.register_prompt(
        "data_analysis_prompt",
        "Analyze the provided dataset and identify key trends and anomalies.",
        category="analytical",
        metadata={"source": "internal_docs"},
    )

    print("\n--- Registered Prompts ---")
    print(registry.list_prompts())

    # Get a specific prompt
    print("\n--- Get 'greeting_prompt' ---")
    print(registry.get_prompt("greeting_prompt"))

    # Evaluate a prompt
    print("\n--- Evaluate 'data_analysis_prompt' ---")
    data_analysis_content = registry.get_prompt("data_analysis_prompt")["content"]
    evaluation_criteria = {
        "length_limit": 100,
        "keywords": ["dataset", "trends", "anomalies"],
        "clarity_check": True,
    }
    evaluation_results = evaluator.evaluate_prompt(
        data_analysis_content, evaluation_criteria
    )
    print(evaluation_results)

    # Attempt to register a duplicate prompt (should raise ValueError)
    try:
        registry.register_prompt("greeting_prompt", "Another greeting.")
    except ValueError as e:
        print(f"\nError: {e}")
