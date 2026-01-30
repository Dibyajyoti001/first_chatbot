# src/agents/chat_agent/nodes/tool_executer_node.py
from src.agents.chat_agent.states.chat_agent_state import ChatAgentState

def tool_extractor(state: ChatAgentState) -> ChatAgentState:
    """
    Minimal/no-op tool executor. If your LLM emits tool calls, expand this function
    to locate the tool, execute it, and inject a ToolMessage back into messages.
    For now this returns the same messages (avoids crash).
    """
    # No-op for now – prevents graph from crashing if should_continue returns tool_executer_node
    return {"messages": state["messages"]}
