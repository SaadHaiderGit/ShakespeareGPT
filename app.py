# Streamlit chat frontend — imports setup_model from main.py, keeps CLI loop intact
import streamlit as st
from main import setup_model
from agent_core import MAX_HISTORY, STYLE_INSTRUCTIONS

st.set_page_config(page_title="ShakespeareGPT", page_icon="📜")
st.title("📜 ShakespeareGPT")
st.caption("Ask anything about Shakespeare's plays and sonnets.")

# Initialise router and message history once per session
if "router" not in st.session_state:
    with st.spinner("Loading model..."):
        st.session_state.router = setup_model()
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: context window fill indicator ---
with st.sidebar:
    st.header("Context Window")
    agent = st.session_state.router.agents.get("info")
    turn_count = len(agent.history) if agent else 0
    fill = turn_count / MAX_HISTORY

    if fill >= 1.0:
        label = f"Full — {turn_count}/{MAX_HISTORY} turns"
    elif fill >= 0.7:
        label = f"Nearly full — {turn_count}/{MAX_HISTORY} turns"
    else:
        label = f"{turn_count}/{MAX_HISTORY} turns"

    st.progress(fill, text=label)

    if fill >= 0.7:
        st.warning("Approaching context limit. Compact to continue cleanly.")

    # Compact: LLM summarises history into a single entry, freeing context
    if st.button("Compact History", disabled=(turn_count == 0)):
        agent.compact()
        st.session_state.messages.append({
            "role": "assistant",
            "content": "_— History compacted. Earlier context has been summarised. —_"
        })
        st.rerun()

    st.caption(f"Max turns: {MAX_HISTORY}. Compact summarises prior turns into one entry.")

    st.divider()

    # Response style toggle — updates agent prompt instruction live
    st.header("Response Style")
    style_options = list(STYLE_INSTRUCTIONS.keys())
    selected = st.radio("", style_options, index=0, format_func=str.capitalize, label_visibility="collapsed")
    if agent:
        agent.response_style = selected
    st.caption(STYLE_INSTRUCTIONS[selected])

# --- Main chat area ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new user input
if prompt := st.chat_input("Ask about Shakespeare..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = st.session_state.router.run(prompt)
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()  # Refresh sidebar turn counter after each message
