import streamlit as st
from langgraph_tool_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid
from datetime import datetime

# =========================== Utilities ===========================
def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []
    st.rerun()

def add_thread(thread_id):
    existing_thread_ids = [chat["id"] for chat in st.session_state["chat_threads"]]
    if thread_id not in existing_thread_ids:
        st.session_state["chat_threads"].append({"id": thread_id, "name": "New Chat"})

def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])

def get_or_create_chat_threads():
    threads_from_backend = retrieve_all_threads()
    if "chat_threads" not in st.session_state:
        st.session_state["chat_threads"] = []
    existing_thread_ids = {chat["id"] for chat in st.session_state["chat_threads"]}
    for thread_id in threads_from_backend:
        if thread_id not in existing_thread_ids:
            st.session_state["chat_threads"].append({"id": thread_id, "name": f"Conversation {thread_id[:4]}..."})

# ======================= Session Initialization ===================
if "thread_id" not in st.session_state:
    all_threads = retrieve_all_threads()
    if all_threads:
        st.session_state["thread_id"] = all_threads[0]
        messages = load_conversation(st.session_state["thread_id"])
        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            temp_messages.append({"role": role, "content": msg.content})
        st.session_state["message_history"] = temp_messages
    else:
        st.session_state["thread_id"] = generate_thread_id()
        st.session_state["message_history"] = []

get_or_create_chat_threads()
add_thread(st.session_state["thread_id"])

# ============================ Sidebar ============================
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")
for chat_entry in st.session_state["chat_threads"][::-1]:
    thread_id = chat_entry["id"]
    chat_name = chat_entry["name"]
    if st.sidebar.button(chat_name, key=f"sidebar_btn_{thread_id}"):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)
        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            temp_messages.append({"role": role, "content": msg.content})
        st.session_state["message_history"] = temp_messages
        st.rerun()

# ============================ Main UI ============================
if not st.session_state["message_history"] or (
    len(st.session_state["message_history"]) == 1 and 
    st.session_state["message_history"][0]["role"] == "assistant" and 
    st.session_state["message_history"][0]["content"] == "Hello! I'm a helpful assistant. How can I assist you today?"
):
    st.session_state["message_history"] = [
        {"role": "assistant", "content": "Hello! I'm a helpful assistant. How can I assist you today?"}
    ]

for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type here")

def ai_only_stream(user_input, CONFIG):
    full_response = ""
    placeholder = st.empty()
    for message_chunk, metadata in chatbot.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=CONFIG,
        stream_mode="messages",
    ):
        if isinstance(message_chunk, ToolMessage):
            tool_name = getattr(message_chunk, "name", "tool")
            st.status(f"🔧 Running `{tool_name}`...", state="running")
        elif isinstance(message_chunk, AIMessage):
            content = message_chunk.content
            if content:
                full_response += content
                placeholder.markdown(full_response)
    return full_response

if user_input:
    if len(st.session_state["message_history"]) == 1:
        current_thread_id = st.session_state["thread_id"]
        for chat_entry in st.session_state["chat_threads"]:
            if chat_entry["id"] == current_thread_id:
                chat_entry["name"] = user_input[:50] + "..." if len(user_input) > 50 else user_input
                break
    
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"], "created_at": datetime.now().isoformat()},
        "run_name": "chat_turn",
    }

    with st.chat_message("assistant"):
        final_response = ai_only_stream(user_input, CONFIG)

    st.session_state["message_history"].append({"role": "assistant", "content": final_response})
    st.rerun()
