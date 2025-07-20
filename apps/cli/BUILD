load("@pip_deps//:requirements.bzl", "requirement")

py_library(
    name = "cli_lib",
    srcs = [
        "memory_viewer.py",
        "orchestrator.py",
        "prompt_runner.py",
    ],
    deps = [
        requirement("spacy"),
        requirement("typer"),
        requirement("faiss-cpu"),
        requirement("sentence-transformers"),
    ],
    visibility = ["//visibility:public"],
)

py_binary(
    name = "cli",
    srcs = ["main.py"],
    main = "main.py",
    deps = [
        ":cli_lib",
        requirement("typer"),
    ],
)
