from orchestration.agent_roles import AGENTS, AgentRole
from orchestration.conversation_logger import log_conversation_md

def run_agent_chain(prompt: str, convo_id: str):
    intermediate = prompt
    for role in [
        AgentRole.CODE_GENERATOR,
        AgentRole.REVIEWER,
        AgentRole.SYNTHESIZER,
        AgentRole.SUPERVISOR
    ]:
        agent = AGENTS[role]
        response = agent.execute(intermediate)
        log_conversation_md(convo_id, role.value, intermediate, response)
        intermediate = response  # Pass output to next agent

    return intermediate


if __name__ == "__main__":
    user_prompt = input("🧠 Enter your feature prompt: ")
    convo_id = input("📁 Enter a conversation ID: ")
    final_output = run_agent_chain(user_prompt, convo_id)
    print(f"\n🧩 Final Output:\n{final_output}")
