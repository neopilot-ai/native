"""
This module defines various prompting strategies to guide the AI's behavior and output.
These strategies can be combined or used individually based on the task requirements.
"""


class PromptStrategy:
    """Base class for all prompting strategies."""

    def apply(self, prompt: str) -> str:
        raise NotImplementedError


class MinimalistPrompting(PromptStrategy):
    """
    A strategy that focuses on providing only the essential information to the AI,
    avoiding verbosity and unnecessary context.
    """

    def apply(self, prompt: str) -> str:
        return f"[Minimalist Prompting] Clear and concise: {prompt}. Define exactly one task. Avoid verbosity."


class ModularDecompositionPrompts(PromptStrategy):
    """
    A strategy that breaks down complex tasks into smaller, manageable sub-prompts.
    This encourages the AI to process information step-by-step.
    """

    def apply(self, prompt: str) -> str:
        return f"[Modular Decomposition] Decompose features into atomic components: {prompt}. Apply step-by-step, recursive implementation. Validate iteratively."


class MultiShotChainOfThoughtGuidance(PromptStrategy):
    """
    A strategy that provides multiple examples (multi-shot) and encourages the AI
    to explain its reasoning process (chain-of-thought).
    """

    def apply(self, prompt: str) -> str:
        return f"[Multi-Shot CoT] Use example-driven prompts to guide style/format. Encourage logical progression in solving complex tasks: {prompt}. Think step-by-step and explain your reasoning."


class SocraticPrompting(PromptStrategy):
    """
    A strategy that uses a Socratic method to guide the AI's reasoning and problem-solving.
    """

    def apply(self, prompt: str) -> str:
        return f"[Socratic Prompting] Task: {prompt}. Weak Point: [PROBLEM]. How would you optimize this? Why did you choose that? Alternative solutions?"


# Example Usage (for demonstration purposes, not part of the core logic)
if __name__ == "__main__":
    initial_prompt = (
        "Develop a Python script to parse a CSV file and extract specific columns."
    )

    minimalist = MinimalistPrompting()
    print(f"Minimalist: {minimalist.apply(initial_prompt)}")

    modular = ModularDecompositionPrompts()
    print(f"Modular: {modular.apply(initial_prompt)}")

    multi_shot_cot = MultiShotChainOfThoughtGuidance()
    print(f"Multi-Shot CoT: {multi_shot_cot.apply(initial_prompt)}")

    socratic = SocraticPrompting()
    print(f"Socratic: {socratic.apply(initial_prompt)}")
