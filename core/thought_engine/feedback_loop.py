from typing import Dict, List


def critic(thinklet: str, system_prompt: str = "") -> str:
    """Critic agent: identifies issues or weaknesses."""
    # Placeholder: In real use, this could use an LLM or rules.
    prompt = f"{system_prompt}\n\nCriticize this thinklet: {thinklet}"
    return f"[Critic] Potential issue: consider edge cases in '{thinklet}'"


def optimizer(thinklet: str, system_prompt: str = "") -> str:
    """Optimizer agent: suggests improvements."""
    prompt = f"{system_prompt}\n\nOptimize this thinklet: {thinklet}"
    return f"[Optimizer] Suggestion: refactor for clarity in '{thinklet}'"


def verifier(thinklet: str, system_prompt: str = "") -> str:
    """Verifier agent: checks for correctness or completeness."""
    prompt = f"{system_prompt}\n\nVerify this thinklet: {thinklet}"
    return f"[Verifier] Verified: logic appears sound in '{thinklet}'"


def multi_agent_feedback(
    thinklets: List[str], system_prompt: str = ""
) -> List[Dict[str, str]]:
    """
    Process each thinklet through critic, optimizer, and verifier agents.
    Returns a list of dicts with each agent's feedback per thinklet.
    """
    results = []
    for t in thinklets:
        feedback = {
            "original": t,
            "critic": critic(t, system_prompt),
            "optimizer": optimizer(t, system_prompt),
            "verifier": verifier(t, system_prompt),
        }
        results.append(feedback)
    return results


# For backward compatibility
recursive_feedback = multi_agent_feedback

if __name__ == "__main__":
    sample_thinklets = ["Add input validation.", "Optimize the loop."]
    feedback = multi_agent_feedback(sample_thinklets)
    for f in feedback:
        print(f)
