import argparse
import subprocess

from orchestration.agent_roles import AGENTS, AgentContext, AgentRole


def generate_ci_cd_pipeline(project_description: str) -> str:
    """Generate CI/CD pipeline suggestions using the SYNTHESIZER agent."""
    agent = AGENTS[AgentRole.SYNTHESIZER]
    context = AgentContext(
        session_id="ci-cd-generation", original_prompt="Generate CI/CD pipeline"
    )
    prompt = f"Generate a GitHub Actions CI/CD pipeline YAML for a project with the following description: {project_description}"
    execution_record = agent.execute(prompt, context)
    return execution_record["output"]


def main():
    parser = argparse.ArgumentParser(description="AI-powered CI/CD pipeline generator")
    parser.add_argument(
        "--description",
        type=str,
        required=True,
        help="A description of the project for which to generate CI/CD pipeline suggestions.",
    )
    args = parser.parse_args()

    print("🧠 Generating CI/CD pipeline suggestions using LLM agent...")
    ci_cd_pipeline = generate_ci_cd_pipeline(args.description)
    print(f"\n✅ Generated CI/CD Pipeline Suggestions:\n\n{ci_cd_pipeline}")


if __name__ == "__main__":
    main()
