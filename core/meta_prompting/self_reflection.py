from typing import Any, Dict

RUBRIC = {
    "usefulness": "Does the response provide actionable, relevant, and helpful information?",
    "tone": "Is the response professional, clear, and appropriate in tone?",
    "logical_consistency": "Is the reasoning sound and free of contradictions?",
}


def self_reflect(response: str) -> Dict[str, Any]:
    """
    Perform self-reflection on a response using the internal rubric.
    Returns a dict with scores and comments for each criterion.
    """
    # Placeholder: In a real system, this would use an LLM or advanced heuristics.
    # Here, we simulate with simple heuristics for demonstration.
    scores = {}
    comments = {}
    # Usefulness: length and presence of actionable words
    scores["usefulness"] = (
        2
        if any(
            w in response.lower()
            for w in ["should", "recommend", "suggest", "implement"]
        )
        else 1
    )
    comments["usefulness"] = (
        "Actionable advice detected."
        if scores["usefulness"] == 2
        else "Could be more actionable."
    )
    # Tone: check for professionalism
    scores["tone"] = (
        2 if all(w not in response.lower() for w in ["dumb", "stupid", "idiot"]) else 1
    )
    comments["tone"] = (
        "Professional tone."
        if scores["tone"] == 2
        else "Unprofessional language detected."
    )
    # Logical consistency: check for contradiction keywords
    scores["logical_consistency"] = 2 if "however" not in response.lower() else 1
    comments["logical_consistency"] = (
        "No obvious contradictions."
        if scores["logical_consistency"] == 2
        else "Possible contradiction detected."
    )
    return {"scores": scores, "comments": comments, "rubric": RUBRIC}


if __name__ == "__main__":
    sample = "You should implement unit tests. This will improve code quality."
    result = self_reflect(sample)
    print(result)
