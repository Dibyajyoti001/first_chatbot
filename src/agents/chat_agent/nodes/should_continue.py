# src/agents/chat_agent/nodes/should_continue.py
from langgraph.graph import END
from src.agents.chat_agent.states.chat_agent_state import ChatAgentState

def should_continue(state: ChatAgentState) -> str:
    """
    Decide whether to go to the tool executor or end the turn.
    Return the name of the next node (string) or the special END token.
    """
    messages = state.get("messages", [])
    if not messages:
        return END

    last_message = messages[-1]

    # If the model produced a tool call, continue to the tool executor node.
    if getattr(last_message, "tool_calls", None):
        return "tool_executer_node"

    # Otherwise, signal the graph to stop this turn.
    return END
