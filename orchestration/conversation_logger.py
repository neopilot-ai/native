"""
Conversation Logger for AI-native systems.

Logs agent conversations and interactions as markdown files for analysis
and debugging purposes.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def log_conversation_md(
    conversation_id: str,
    agent_role: str,
    input_text: str,
    output_text: str,
    metadata: Optional[Dict[str, Any]] = None,
    logs_dir: str = "logs",
) -> str:
    """
    Log a conversation turn as markdown.

    Args:
        conversation_id: Unique identifier for the conversation
        agent_role: Role/name of the agent (e.g., 'user', 'code_generator', 'reviewer')
        input_text: Input text/prompt
        output_text: Output/response text
        metadata: Optional metadata about the interaction
        logs_dir: Directory to store log files

    Returns:
        Path to the created log file
    """
    # Create logs directory if it doesn't exist
    logs_path = Path(logs_dir)
    logs_path.mkdir(exist_ok=True)

    # Create conversation-specific directory
    conv_dir = logs_path / conversation_id
    conv_dir.mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{agent_role}_{timestamp}.md"
    filepath = conv_dir / filename

    # Create markdown content
    content = f"""# Conversation Turn: {agent_role}

**Conversation ID:** {conversation_id}  
**Timestamp:** {datetime.now().isoformat()}  
**Agent Role:** {agent_role}

## Input

```
{input_text}
```

## Output

```
{output_text}
```

"""

    # Add metadata if provided
    if metadata:
        content += "## Metadata\n\n"
        for key, value in metadata.items():
            content += f"**{key}:** {value}\n"
        content += "\n"

    # Add conversation summary
    content += f"""## Summary

- **Input Length:** {len(input_text)} characters
- **Output Length:** {len(output_text)} characters
- **Turn Type:** {agent_role}

---
*Logged by AI-Native Systems Conversation Logger*
"""

    # Write to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return str(filepath)


def log_conversation_json(
    conversation_id: str,
    agent_role: str,
    input_text: str,
    output_text: str,
    metadata: Optional[Dict[str, Any]] = None,
    logs_dir: str = "logs",
) -> str:
    """
    Log a conversation turn as JSON.

    Args:
        conversation_id: Unique identifier for the conversation
        agent_role: Role/name of the agent
        input_text: Input text/prompt
        output_text: Output/response text
        metadata: Optional metadata about the interaction
        logs_dir: Directory to store log files

    Returns:
        Path to the created log file
    """
    import json

    # Create logs directory if it doesn't exist
    logs_path = Path(logs_dir)
    logs_path.mkdir(exist_ok=True)

    # Create conversation-specific directory
    conv_dir = logs_path / conversation_id
    conv_dir.mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{agent_role}_{timestamp}.json"
    filepath = conv_dir / filename

    # Create JSON content
    log_entry = {
        "conversation_id": conversation_id,
        "agent_role": agent_role,
        "timestamp": datetime.now().isoformat(),
        "input": input_text,
        "output": output_text,
        "metadata": metadata or {},
        "stats": {
            "input_length": len(input_text),
            "output_length": len(output_text),
            "input_words": len(input_text.split()),
            "output_words": len(output_text.split()),
        },
    }

    # Write to file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)

    return str(filepath)


def create_conversation_summary(conversation_id: str, logs_dir: str = "logs") -> str:
    """
    Create a summary of all turns in a conversation.

    Args:
        conversation_id: Unique identifier for the conversation
        logs_dir: Directory containing log files

    Returns:
        Path to the created summary file
    """
    logs_path = Path(logs_dir)
    conv_dir = logs_path / conversation_id

    if not conv_dir.exists():
        raise FileNotFoundError(f"Conversation directory not found: {conv_dir}")

    # Find all markdown files in the conversation directory
    md_files = list(conv_dir.glob("*.md"))
    md_files.sort(key=lambda x: x.name)  # Sort by filename (which includes timestamp)

    if not md_files:
        raise FileNotFoundError(
            f"No markdown files found in conversation directory: {conv_dir}"
        )

    # Create summary content
    summary_content = f"""# Conversation Summary

**Conversation ID:** {conversation_id}  
**Total Turns:** {len(md_files)}  
**Created:** {datetime.now().isoformat()}

## Turn Overview

"""

    # Add each turn to the summary
    for i, md_file in enumerate(md_files, 1):
        # Extract agent role from filename
        agent_role = md_file.stem.split("_")[0]

        summary_content += f"### Turn {i}: {agent_role}\n"
        summary_content += f"**File:** [{md_file.name}]({md_file.name})\n\n"

    summary_content += f"""## Quick Stats

- **Total Files:** {len(md_files)}
- **Agents Involved:** {len(set(f.stem.split('_')[0] for f in md_files))}
- **Time Span:** TODO: Calculate time span

---
*Generated by AI-Native Systems Conversation Logger*
"""

    # Write summary file
    summary_file = conv_dir / "summary.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_content)

    return str(summary_file)


def list_conversations(logs_dir: str = "logs") -> list:
    """
    List all conversations in the logs directory.

    Args:
        logs_dir: Directory containing log files

    Returns:
        List of conversation IDs
    """
    logs_path = Path(logs_dir)
    if not logs_path.exists():
        return []

    # Find all conversation directories
    conv_dirs = [
        d for d in logs_path.iterdir() if d.is_dir() and not d.name.startswith(".")
    ]
    return [d.name for d in conv_dirs]


def get_conversation_stats(
    conversation_id: str, logs_dir: str = "logs"
) -> Dict[str, Any]:
    """
    Get statistics for a specific conversation.

    Args:
        conversation_id: Unique identifier for the conversation
        logs_dir: Directory containing log files

    Returns:
        Dictionary with conversation statistics
    """
    logs_path = Path(logs_dir)
    conv_dir = logs_path / conversation_id

    if not conv_dir.exists():
        raise FileNotFoundError(f"Conversation directory not found: {conv_dir}")

    # Count files by type
    md_files = list(conv_dir.glob("*.md"))
    json_files = list(conv_dir.glob("*.json"))

    # Get agent roles
    agent_roles = set()
    for file in md_files + json_files:
        agent_role = file.stem.split("_")[0]
        agent_roles.add(agent_role)

    return {
        "conversation_id": conversation_id,
        "total_files": len(md_files) + len(json_files),
        "markdown_files": len(md_files),
        "json_files": len(json_files),
        "agent_roles": list(agent_roles),
        "unique_agents": len(agent_roles),
    }


if __name__ == "__main__":
    # Demo usage
    conv_id = "demo_conversation"

    # Log some conversation turns
    log_conversation_md(
        conv_id, "user", "What is machine learning?", "Machine learning is..."
    )
    log_conversation_md(
        conv_id, "code_generator", "Generate a function", "def example():..."
    )
    log_conversation_md(
        conv_id, "reviewer", "Review the code", "The code looks good..."
    )

    # Create summary
    summary_file = create_conversation_summary(conv_id)
    print(f"Created conversation summary: {summary_file}")

    # Get stats
    stats = get_conversation_stats(conv_id)
    print(f"Conversation stats: {stats}")
