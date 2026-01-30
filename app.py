# app.py
from dotenv import load_dotenv  # Import the loader
load_dotenv()                   # Run the loader FIRST
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from src.routes.rag_route import router as rag_router

from src.routes.chat_route import router
from src.agents.chat_agent.graph import create_chat_agent_graph
import src.server_state as server_state

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - create graph and keep checkpointer context alive
    compiled_graph, checkpointer_ctx = create_chat_agent_graph()
    server_state.GRAPH = compiled_graph
    server_state.CHECKPOINTER_CTX = checkpointer_ctx

    print("Graph compiled and checkpointer context entered. Backend ready.")
    try:
        yield
    finally:
        # Shutdown - exit checkpointer context and clear state
        ctx = server_state.CHECKPOINTER_CTX
        if ctx is not None:
            try:
                ctx.__exit__(None, None, None)
                print("Checkpointer context exited cleanly.")
            except Exception as e:
                print("Error while exiting checkpointer context:", e)
        server_state.GRAPH = None
        server_state.CHECKPOINTER_CTX = None
        print("Server state cleared. Backend shutdown complete.")

app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.include_router(rag_router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
