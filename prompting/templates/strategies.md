# 🧠 Prompt Strategies for AI-Native Agents

## 🎯 Minimalist Prompting
- One task per prompt
- Avoid verbosity
- Provide relevant context only

## 🧱 Modular Execution
- Decompose feature into atomic sub-tasks
- Apply recursive prompting
- Validate through agent feedback

## 🧪 Multi-Shot Prompting
**Goal:** Provide examples to guide output style.

```txt
Generate a validation function like:

Example 1:
def validate_email(email): ...

Example 2:
def validate_url(url): ...

🧠 Chain-of-Thought Reasoning

Encourage sequential thinking:
Let's solve [PROBLEM]:
1. Understand input/output
2. Consider edge cases
3. Write test cases

🗨️ Socratic Prompt Schema
You are a FAANG-level prompt engineer.
Task: Refactor login handler
Weak Point: Security flaws
Why is this wrong?
What’s a better approach?