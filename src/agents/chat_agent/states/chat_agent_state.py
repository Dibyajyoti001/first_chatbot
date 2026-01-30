# src/agents/chat_agent/states/chat_agent_state.py
from langgraph.graph import MessagesState

# Keep this minimal: inherits MessagesState so LangGraph knows how to persist messages
class ChatAgentState(MessagesState):
    pass
