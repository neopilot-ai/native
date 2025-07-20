# Tool functions available to LLM agents

import os


def list_dir(path="."):
    return os.listdir(path)


def read_file_tool(filepath):
    with open(filepath, "r") as f:
        return f.read()


def edit_file_tool(filepath, new_content):
    with open(filepath, "w") as f:
        f.write(new_content)
    return f"✅ Updated {filepath}"


TOOL_REGISTRY = {
    "list_dir": list_dir,
    "read_file": read_file_tool,
    "edit_file": edit_file_tool,
}
