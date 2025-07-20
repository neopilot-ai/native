# Makefile for ai_native_systems

.PHONY: build test run clean zip setup update-todo install-hooks ci-update-todo help install-dev bazel-remote buck2-remote goma-remote reclient-remote demo-ci-output test-ci-output

help:
	@echo "Available targets:"
	@echo "  install     Install Python dependencies with poetry"
	@echo "  install-dev Install development dependencies"
	@echo "  test        Run all tests with pytest"
	@echo "  run         Run the CLI interface"
	@echo "  build       Build Rust components"
	@echo "  clean       Remove build artifacts"
	@echo "  zip         Create release zip"
	@echo "  setup       Setup development environment"
	@echo "  update-todo Update TODO.md based on implementation status"
	@echo "  demo-ci-output  Demonstrate JUnit/JSON output functionality"
	@echo "  test-ci-output   Run CI output tests"

install:
	poetry install

install-dev:
	poetry install --with dev

build:
	cd rust/memory_fs && cargo build

test:
	PYTHONPATH=. poetry run pytest tests/ -v

run:
	poetry run python apps/cli/main.py

commit:
	poetry run python apps/cli/commit_agent.py

lint:
	poetry run python devops/lint_and_format.py

pr-title:
	poetry run python devops/generate_git_summaries.py --pr-title

release-notes:
	poetry run python devops/generate_git_summaries.py --release-notes

ci-cd:
	poetry run python devops/generate_ci_cd.py

clean:
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf */*/__pycache__/
	cd rust/memory_fs && cargo clean

zip:
	@echo "Creating release zip..."
	@rm -f ai_native_systems.zip
	@zip -r ai_native_systems.zip . -x "*.git*" "venv/*" "*.pyc" "__pycache__/*" ".pytest_cache/*" "*.zip"

setup:
	poetry install
	poetry run pre-commit install

update-todo:
	poetry run python devops/update_todo.py

install-hooks:
	poetry run pre-commit install

ci-update-todo:
	poetry run python devops/update_todo.py

bazel-remote:
	poetry run python devops/remote_exec.py bazel build //... --remote

buck2-remote:
	poetry run python devops/remote_exec.py buck2 build //... --remote

goma-remote:
	poetry run python devops/remote_exec.py goma build //...

reclient-remote:
	poetry run python devops/remote_exec.py reclient build //...

demo-ci-output:
	@echo "Demonstrating CI Dashboard Output functionality..."
	python3 demo_ci_output.py

test-ci-output:
	@echo "Running CI output tests..."
	PYTHONPATH=. python3 -m pytest tests/unit/test_ci_output.py -v

# CI Dashboard targets with output generation
bazel-ci:
	poetry run python devops/remote_exec.py bazel build //... --junit-output=test-results/bazel-build.xml --json-output=test-results/bazel-build.json

buck2-ci:
	poetry run python devops/remote_exec.py buck2 build //... --junit-output=test-results/buck2-build.xml --json-output=test-results/buck2-build.json

goma-ci:
	poetry run python devops/remote_exec.py goma build //... --junit-output=test-results/goma-build.xml --json-output=test-results/goma-build.json

reclient-ci:
	poetry run python devops/remote_exec.py reclient build //... --junit-output=test-results/reclient-build.xml --json-output=test-results/reclient-build.json