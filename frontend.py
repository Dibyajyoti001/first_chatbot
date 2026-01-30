# frontend.py
import streamlit as st
import requests
import uuid

# Configuration
API_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")

# Initialize Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: File Upload for RAG ---
with st.sidebar:
    st.header("📂 Knowledge Base")
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt", "md"])
    
    if st.button("Upload File"):
        if uploaded_file:
            with st.spinner("Uploading and indexing..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{API_URL}/rag/upload", files=files)
                    
                    if response.status_code == 200:
                        st.success(f"File '{uploaded_file.name}' processed!")
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
        else:
            st.warning("Please select a file first.")

    st.divider()
    st.caption(f"Session ID: {st.session_state.session_id}")

# --- MAIN CHAT INTERFACE ---
st.title("🤖 Chat Agent")

# 1. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Chat Input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Call Backend API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Note: Your backend expects 'message' as a query parameter
                response = requests.post(
                    f"{API_URL}/chat/{st.session_state.session_id}",
                    params={"message": prompt} 
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # The backend returns a list of messages. We want the last one (the answer).
                    # But your handler returns ALL messages. Let's filter for the AI's latest response.
                    backend_messages = data.get("messages", [])
                    
                    if backend_messages:
                        # Get the last message which should be the AI response
                        last_msg = backend_messages[-1]
                        ai_content = last_msg.get("content", "No response content.")
                        
                        st.markdown(ai_content)
                        st.session_state.messages.append({"role": "assistant", "content": ai_content})
                    else:
                        st.error("Backend returned empty message list.")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"Could not connect to backend: {e}")