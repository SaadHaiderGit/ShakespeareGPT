# Streamlit chat frontend — imports setup_model from main.py, keeps CLI loop intact
import streamlit as st
from main import setup_model

st.set_page_config(page_title="ShakespeareGPT", page_icon="📜")
st.title("📜 ShakespeareGPT")
st.caption("Ask anything about Shakespeare's plays and sonnets.")

# Initialise router and message history once per session
if "router" not in st.session_state:
    with st.spinner("Loading model..."):
        st.session_state.router = setup_model()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

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
