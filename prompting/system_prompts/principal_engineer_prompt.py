import json
from pathlib import Path


def load_system_prompt(path=None):
    """Load the system prompt from a JSON file."""
    if path is None:
        path = Path(__file__).parent / "principal_engineer_prompt.json"
    else:
        path = Path(path)
    with open(path, "r") as f:
        return json.load(f)


def build_combined_prompt(user_prompt, system_prompt_path=None):
    """Combine the system prompt with the user's prompt into a single string."""
    system_prompt = load_system_prompt(system_prompt_path)
    persona = system_prompt["persona"]
    principles = "\n".join(system_prompt["principles"])
    review_standards = "\n".join(system_prompt["review_standards"])
    workflow = "\n".join(system_prompt["workflow"])
    tech_stack = ", ".join(system_prompt["tech_stack"])
    system_message = (
        f"You are a {persona} specializing in {tech_stack}.\n"
        f"Principles:\n{principles}\n"
        f"Review Standards:\n{review_standards}\n"
        f"Workflow:\n{workflow}\n"
        f"Respond with actionable, production-grade advice and code."
    )
    combined_prompt = f"{system_message}\n\nUser Task: {user_prompt}"
    return combined_prompt
