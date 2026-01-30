# src/handlers/chat_handler.py
from langchain_core.messages import HumanMessage
from typing import Dict
import src.server_state as server_state

def chat_agent_handler(message: str, session_id: str) -> Dict:
    """
    Build input, invoke the compiled LangGraph (which uses PostgresSaver),
    and return a serializable dictionary.
    """
    if server_state.GRAPH is None:
        return {"error": "graph not ready, server_state.GRAPH is None"}, 503

    # Messages are passed as langchain message objects
    human = HumanMessage(content=message)

    config = {"configurable": {"thread_id": session_id}}

    # Invoke graph (synchronous)
    state = server_state.GRAPH.invoke({"messages": [human]}, config=config)

    # Normalize messages into serializable list of dicts
    out = []
    for m in state["messages"]:
        content = getattr(m, "content", None) or getattr(m, "text", str(m))
        role = getattr(m, "role", None) or getattr(m, "type", "assistant")
        out.append({"role": role, "content": content})

    return {"session_id": session_id, "messages": out}
