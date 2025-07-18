import os
import re

TODO_FILE = "TODO.md"
CHECKS = [
    # (pattern in TODO.md, file or directory to check)
    (r"Implement `core/token_forge/decomposer.py`", "core/token_forge/decomposer.py"),
    (r"Add `core/context_kernel/memory_store.py`", "core/context_kernel/memory_store.py"),
    (r"Create `tool_chain/executor.py`", "core/tool_chain/executor.py"),
    (r"Add `meta_prompting/self_reflection.py`", "core/meta_prompting/self_reflection.py"),
    (r"Simple tool calls via shell or REST API", "core/tool_chain/executor.py"),
    (r"Tool registry and permission checks", "core/tool_chain/executor.py"),
    (r"Support for chained execution", "core/tool_chain/executor.py"),
    (r"Reflect on usefulness, tone, logical consistency", "core/meta_prompting/self_reflection.py"),
]

def update_todo():
    with open(TODO_FILE, "r") as f:
        lines = f.readlines()

    for pattern, path in CHECKS:
        exists = os.path.exists(path)
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                if exists and not line.strip().startswith("- [x]"):
                    lines[i] = line.replace("- [ ]", "- [x]")
                elif not exists and not line.strip().startswith("- [ ]"):
                    lines[i] = line.replace("- [x]", "- [ ]")

    with open(TODO_FILE, "w") as f:
        f.writelines(lines)

if __name__ == "__main__":
    update_todo()
    print("TODO.md auto-updated based on codebase status.") 