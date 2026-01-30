import os
from langchain_community.chat_message_histories import SQLChatMessageHistory

DATABASE_URL = os.getenv("DATABASE_URL")

def get_chat_history(session_id: str):
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string=DATABASE_URL
    )
