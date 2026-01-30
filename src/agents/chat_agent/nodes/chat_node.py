# src/agents/chat_agent/nodes/chat_node.py

from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

from langchain_core.messages import BaseMessage, SystemMessage
from src.agents.chat_agent.states.chat_agent_state import ChatAgentState
from src.agents.chat_agent.tools.date_time import get_current_date_and_time
from src.agents.chat_agent.tools.web_search import search_the_web

from src.rag import retrieve 

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def chat(state: ChatAgentState) -> ChatAgentState:
    """
    Main chat node for the graph.

    - Uses messages restored by LangGraph checkpointer
    - Injects RAG context if available
    - Keeps tool calling intact
    """

    # Build model
    model = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=GROQ_API_KEY
    )

    # Bind tools
    model = model.bind_tools([
        get_current_date_and_time,
        search_the_web
    ])

    # Messages restored by LangGraph
    messages: list[BaseMessage] = state["messages"]

    # ---------------- RAG INJECTION ----------------
    # Take latest user message
    last_msg = messages[-1]
    user_query = last_msg.content

    # Retrieve relevant chunks
    docs = retrieve(
        query_text=user_query,
        collection_name="default",
        k=4
    )

    if docs:
        context = "\n\n".join(d["content"] for d in docs)

        rag_message = SystemMessage(
            content=(
                "You are a helpful assistant.\n"
                "Use the following retrieved context to answer the user's question.\n"
                "If the context does not help, answer normally.\n\n"
                f"{context}"
            )
        )

        messages = [rag_message] + messages
    # ------------------------------------------------

    # Invoke model
    answer = model.invoke(messages)

    # Return response (LangGraph handles persistence)
    return {
        "messages": [answer]
    }
