import argparse
import subprocess

from orchestration.agent_roles import AGENTS, AgentContext, AgentRole


def get_git_diff(commit_range: str = None) -> str:
    """Get the git diff for a given commit range or staged changes."""
    if commit_range:
        return subprocess.check_output(["git", "diff", commit_range]).decode()
    else:
        return subprocess.check_output(["git", "diff", "HEAD"]).decode()


def generate_summary(diff: str, summary_type: str) -> str:
    """Generate a PR title or release notes using the SYNTHESIZER agent."""
    agent = AGENTS[AgentRole.SYNTHESIZER]
    context = AgentContext(
        session_id="git-summary", original_prompt=f"Generate {summary_type}"
    )
    prompt = f"Generate a {summary_type} for the following git diff:\n{diff}"
    execution_record = agent.execute(prompt, context)
    return execution_record["output"]


def main():
    parser = argparse.ArgumentParser(description="AI-powered Git summary generator")
    parser.add_argument(
        "--pr-title", action="store_true", help="Generate a Pull Request title"
    )
    parser.add_argument(
        "--release-notes", action="store_true", help="Generate release notes"
    )
    parser.add_argument(
        "--diff-range",
        type=str,
        help="Git diff range (e.g., HEAD~3..HEAD or commit_hash1..commit_hash2)",
    )
    args = parser.parse_args()

    if not (args.pr_title or args.release_notes):
        parser.error("Please specify either --pr-title or --release-notes")

    diff = get_git_diff(args.diff_range)

    if args.pr_title:
        print("🧠 Generating PR title using LLM agent...")
        pr_title = generate_summary(diff, "Pull Request title")
        print(f"\n✅ Generated PR Title:\n\n{pr_title}")

    if args.release_notes:
        print("🧠 Generating release notes using LLM agent...")
        release_notes = generate_summary(diff, "release notes")
        print(f"\n✅ Generated Release Notes:\n\n{release_notes}")


if __name__ == "__main__":
    main()
