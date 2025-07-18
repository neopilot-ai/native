import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def log_conversation_md(convo_id, agent_name, prompt, response):
    log_file = LOG_DIR / f"{convo_id}.md"
    with open(log_file, "a") as f:
        f.write(f"### 🧠 {agent_name}\n")
        f.write(f"**Prompt:**\n```\n{prompt}\n```\n")
        f.write(f"**Response:**\n```\n{response}\n```\n\n")


def log_conversation_jsonl(convo_id, agent_name, prompt, response):
    log_file = LOG_DIR / f"{convo_id}.jsonl"
    with open(log_file, "a") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "prompt": prompt,
            "response": response
        }, f)
        f.write("\n")
