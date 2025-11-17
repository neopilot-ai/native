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
	@if command -v poetry >/dev/null 2>&1; then \
		poetry install; \
	else \
		echo "Poetry not found. Installing with pip instead..."; \
		pip3 install -r requirements.txt; \
	fi

install-dev:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry install --with dev; \
	else \
		echo "Poetry not found. Installing with pip instead..."; \
		pip3 install -r requirements.txt; \
		pip3 install pytest pytest-cov black flake8 mypy; \
	fi

build:
	cd rust/memory_fs && cargo build

test:
	@if command -v poetry >/dev/null 2>&1; then \
		PYTHONPATH=. poetry run pytest tests/ -v; \
	else \
		PYTHONPATH=. python3 -m pytest tests/ -v; \
	fi

run:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 apps/cli/main.py; \
	else \
		PYTHONPATH=. python3 apps/cli/main.py; \
	fi

commit:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 apps/cli/commit_agent.py; \
	else \
		PYTHONPATH=. python3 apps/cli/commit_agent.py; \
	fi

lint:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/lint_and_format.py; \
	else \
		PYTHONPATH=. python3 devops/lint_and_format.py; \
	fi

pr-title:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/generate_git_summaries.py --pr-title; \
	else \
		PYTHONPATH=. python3 devops/generate_git_summaries.py --pr-title; \
	fi

release-notes:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/generate_git_summaries.py --release-notes; \
	else \
		PYTHONPATH=. python3 devops/generate_git_summaries.py --release-notes; \
	fi

ci-cd:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/generate_ci_cd.py; \
	else \
		PYTHONPATH=. python3 devops/generate_ci_cd.py; \
	fi

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
	@if command -v poetry >/dev/null 2>&1; then \
		poetry install && poetry run pre-commit install; \
	else \
		pip3 install -r requirements.txt && pip3 install pytest pytest-cov black flake8 mypy pre-commit; \
	fi

update-todo:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/update_todo.py; \
	else \
		PYTHONPATH=. python3 devops/update_todo.py; \
	fi

install-hooks:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run pre-commit install; \
	else \
		pre-commit install; \
	fi

ci-update-todo:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/update_todo.py; \
	else \
		PYTHONPATH=. python3 devops/update_todo.py; \
	fi

bazel-remote:
    @if command -v poetry >/dev/null 2>&1; then \
        poetry run python3 devops/remote_exec.py bazel build //... --config=remote; \
    else \
        PYTHONPATH=. python3 devops/remote_exec.py bazel build //... --config=remote; \
    fi

buck2-remote:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/remote_exec.py buck2 build //... --remote; \
	else \
		PYTHONPATH=. python3 devops/remote_exec.py buck2 build //... --remote; \
	fi

goma-remote:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/remote_exec.py goma build //... --remote; \
	else \
		PYTHONPATH=. python3 devops/remote_exec.py goma build //... --remote; \
	fi

reclient-remote:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/remote_exec.py reclient build //... --remote; \
	else \
		PYTHONPATH=. python3 devops/remote_exec.py reclient build //... --remote; \
	fi

demo-ci-output:
	@echo "Demonstrating CI Dashboard Output functionality..."
	python3 demo_ci_output.py

test-ci-output:
	@echo "Running CI output tests..."
	PYTHONPATH=. python3 -m pytest tests/unit/test_ci_output.py -v

# CI Dashboard targets with output generation
bazel-ci:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/remote_exec.py bazel build //... --junit-output=test-results/bazel-build.xml --json-output=test-results/bazel-build.json; \
	else \
		PYTHONPATH=. python3 devops/remote_exec.py bazel build //... --junit-output=test-results/bazel-build.xml --json-output=test-results/bazel-build.json; \
	fi

buck2-ci:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/remote_exec.py buck2 build //... --junit-output=test-results/buck2-build.xml --json-output=test-results/buck2-build.json; \
	else \
		PYTHONPATH=. python3 devops/remote_exec.py buck2 build //... --junit-output=test-results/buck2-build.xml --json-output=test-results/buck2-build.json; \
	fi

goma-ci:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/remote_exec.py goma build //... --junit-output=test-results/goma-build.xml --json-output=test-results/goma-build.json; \
	else \
		PYTHONPATH=. python3 devops/remote_exec.py goma build //... --junit-output=test-results/goma-build.xml --json-output=test-results/goma-build.json; \
	fi

reclient-ci:
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run python3 devops/remote_exec.py reclient build //... --junit-output=test-results/reclient-build.xml --json-output=test-results/reclient-build.json; \
	else \
		PYTHONPATH=. python3 devops/remote_exec.py reclient build //... --junit-output=test-results/reclient-build.xml --json-output=test-results/reclient-build.json; \
	fi