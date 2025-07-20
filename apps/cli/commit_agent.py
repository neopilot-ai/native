import typer

from devops.auto_commit_agent import commit

app = typer.Typer()


@app.command()
def main(
    all: bool = typer.Option(False, "--all", "-a", help="Add all changes before commit")
):
    """AI-powered git commit tool"""
    print("🧠 Generating commit message using LLM agent...")
    commit(staged=not all)


if __name__ == "__main__":
    app()
