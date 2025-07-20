import subprocess
import sys


def run_command(command: list[str], description: str):
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully.\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed.\n{e.stdout}\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print(
            f"❌ Error: {command[0]} not found. Please ensure it is installed and in your PATH."
        )
        sys.exit(1)


def main():
    print("Starting linting and formatting process...")

    # Run Black
    run_command(["poetry", "run", "black", "."], "Running Black (code formatter)")

    # Run Isort
    run_command(["poetry", "run", "isort", "."], "Running Isort (import sorter)")

    # Run Flake8
    run_command(["poetry", "run", "flake8", "."], "Running Flake8 (linter)")

    print("\n✨ Linting and formatting process finished.")


if __name__ == "__main__":
    main()
