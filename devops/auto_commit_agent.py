# Automatically generate commits and PRs using an LLM agent

import subprocess
import argparse
from orchestration.agent_roles import AGENTS, AgentRole


def get_git_diff():
    return subprocess.check_output(["git", "diff", "--cached"]).decode()


def generate_commit_message(diff: str):
    agent = AGENTS[AgentRole.CODE_GENERATOR]
    return agent.execute(f"Generate a Git commit message for this diff:\n{diff}")


def commit(staged: bool = True):
    if not staged:
        subprocess.run(["git", "add", "."])
    diff = get_git_diff()
    message = generate_commit_message(diff)
    subprocess.run(["git", "commit", "-m", message])
    print(f"✅ Committed with message:\n\n{message}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-powered git commit tool")
    parser.add_argument("--all", action="store_true", help="Add all changes before commit")
    args = parser.parse_args()

    print("🧠 Generating commit message using LLM agent...")
    commit(staged=not args.all)