# Defines multi-agent orchestration roles and responsibilities

from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any


class AgentRole(str, Enum):
    CODE_GENERATOR = "LLM-A"
    REVIEWER = "LLM-B"
    SYNTHESIZER = "LLM-C"
    SUPERVISOR = "LLM-D"


@dataclass
class Agent:
    name: str
    role: AgentRole
    strategy: Callable[[str], Any]

    def execute(self, prompt: str):
        print(f"[{self.role}] executing task: {prompt}")
        return self.strategy(prompt)


# Example strategy stub (replace with real LLM call)
def code_generator_strategy(prompt):
    return f"# Generated code for: {prompt}"

def reviewer_strategy(prompt):
    return f"# Reviewed: {prompt}"

def synthesizer_strategy(prompt):
    return f"# Synthesis result for: {prompt}"

def supervisor_strategy(prompt):
    return f"# Meta-evaluation: {prompt}"


# Agent instances
AGENTS = {
    AgentRole.CODE_GENERATOR: Agent("Gen", AgentRole.CODE_GENERATOR, code_generator_strategy),
    AgentRole.REVIEWER: Agent("Rev", AgentRole.REVIEWER, reviewer_strategy),
    AgentRole.SYNTHESIZER: Agent("Synth", AgentRole.SYNTHESIZER, synthesizer_strategy),
    AgentRole.SUPERVISOR: Agent("Super", AgentRole.SUPERVISOR, supervisor_strategy),
}
