import json
from pathlib import Path


def load_system_prompt(path=None):
    """Load the system prompt from a JSON file."""
    if path is None:
        path = Path(__file__).parent / "faang_engineer_prompt.json"
    else:
        path = Path(path)
    with open(path, "r") as f:
        return json.load(f)


def build_combined_prompt(user_prompt, system_prompt_path=None):
    """Combine the system prompt with the user's prompt into a single string."""
    system_prompt = load_system_prompt(system_prompt_path)
    persona = system_prompt["persona"]
    rules = "\n".join(f"- {rule}" for rule in system_prompt["rules"])
    devops_actions = "\n".join(
        f"- {action}" for action in system_prompt["devops"]["actions"]
    )

    system_message = (
        f"{persona}\n\n"
        f"**Core Directives & Rules:**\n{rules}\n\n"
        f"**DevOps & CI/CD Environment:**\n"
        f"- Environment: {system_prompt['devops']['environment']}\n"
        f"{devops_actions}"
    )

    combined_prompt = f"{system_message}\n\n**User Task:**\n{user_prompt}"
    return combined_prompt
