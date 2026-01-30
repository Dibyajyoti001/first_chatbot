# src/agents/chat_agent/graph.py
import os
from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.postgres import PostgresSaver

from src.agents.chat_agent.states.chat_agent_state import ChatAgentState
from src.agents.chat_agent.nodes.chat_node import chat
from src.agents.chat_agent.nodes.should_continue import should_continue
from src.agents.chat_agent.nodes.tool_executer_node import tool_extractor

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

def create_chat_agent_graph() -> CompiledStateGraph:
    """
    Build and compile the StateGraph with a Postgres checkpointer.
    This function returns a compiled graph. The caller should keep the PostgresSaver
    context alive for the app lifetime (we will do that in app.py).
    """
    builder = StateGraph(ChatAgentState)

    # register nodes
    builder.add_node("chat_node", chat)
    builder.add_node("tool_executer_node", tool_extractor)

    # edges
    builder.add_edge(START, "chat_node")
    builder.add_conditional_edges("chat_node", should_continue)
    builder.add_edge("tool_executer_node", "chat_node")

    # create checkpointer (context manager)
    checkpointer_ctx = PostgresSaver.from_conn_string(DATABASE_URL)
    checkpointer = checkpointer_ctx.__enter__()  # enter and keep alive
    checkpointer.setup()  # create tables if not present

    compiled = builder.compile(checkpointer=checkpointer)

    # return compiled graph and the context so caller can close at shutdown if desired
    return compiled, checkpointer_ctx
