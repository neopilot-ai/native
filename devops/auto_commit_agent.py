# Automatically generate commits and PRs using an LLM agent

import argparse
import subprocess
import tempfile

from orchestration.agent_roles import AGENTS, AgentContext, AgentRole


def get_git_diff():
    return subprocess.check_output(["git", "diff", "--cached"]).decode()


def generate_commit_message(diff: str):
    agent = AGENTS[AgentRole.CODE_GENERATOR]
    # Create a minimal context for the auto-commit agent
    context = AgentContext(
        session_id="auto-commit", original_prompt="Generate Git commit message"
    )
    execution_record = agent.execute(
        f"Generate a Git commit message for this diff:\n{diff}", context
    )
    return execution_record["output"]  # Extract the message from the execution record


def commit(staged: bool = True):
    if not staged:
        subprocess.run(["git", "add", "."])
    diff = get_git_diff()
    message = generate_commit_message(diff)

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write(message)
        temp_file_path = f.name

    try:
        subprocess.run(["git", "commit", "-F", temp_file_path], check=True)
        print(f"✅ Committed with message:\n\n{message}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git commit failed: {e}")
        print(f"Stderr: {e.stderr.decode() if e.stderr else ''}")
    finally:
        import os

        os.remove(temp_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-powered git commit tool")
    parser.add_argument(
        "--all", action="store_true", help="Add all changes before commit"
    )
    args = parser.parse_args()

    print("🧠 Generating commit message using LLM agent...")
    commit(staged=not args.all)
