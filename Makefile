# Makefile for ai_native_systems

.PHONY: build test run clean zip setup update-todo install-hooks ci-update-todo

help:
	@echo "Available targets:"
	@echo "  install   Install Python and Rust dependencies"
	@echo "  test      Run all tests"
	@echo "  build     Build Rust components"
	@echo "  clean     Remove build artifacts"

install:
	poetry install
	cd rust/memory_fs && cargo build

build:
	bazel build //...

test:
	bazel test //...

run:
	bazel run //apps/cli:main

clean:
	bazel clean

zip:
	zip -r release.zip .

setup:
	pip3 install -r requirements/dev.txt

update-todo:
	python devops/update_todo.py

install-hooks:
	pre-commit install

ci-update-todo:
	python devops/update_todo.py