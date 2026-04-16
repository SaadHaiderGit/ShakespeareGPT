# Streamlit chat frontend — ChatGPT-like layout with custom HTML bubbles
import streamlit as st
from main import setup_model
from agent_core import MAX_HISTORY, STYLE_INSTRUCTIONS

st.set_page_config(page_title="ShakespeareGPT", page_icon="📜", layout="centered")

# --- Global CSS: user bubble (right), assistant full-width, subtle sidebar ---
st.markdown("""
<style>
.user-bubble {
    display: flex;
    justify-content: flex-end;
    margin: 12px 0 4px 0;
}
.user-bubble span {
    background: #0084ff;
    color: white;
    padding: 9px 15px;
    border-radius: 18px 18px 4px 18px;
    max-width: 72%;
    font-size: 0.95rem;
    line-height: 1.5;
    word-wrap: break-word;
    display: inline-block;
}
.llm-label {
    font-size: 0.72rem;
    color: #999;
    margin: 16px 0 2px 0;
}
</style>
""", unsafe_allow_html=True)

# --- Session state init ---
if "router" not in st.session_state:
    with st.spinner("Loading model..."):
        st.session_state.router = setup_model()
if "messages" not in st.session_state:
    st.session_state.messages = []

agent = st.session_state.router.agents.get("info")

# --- Sidebar: subtle context window + style controls ---
with st.sidebar:
    turn_count = len(agent.history) if agent else 0
    fill = turn_count / MAX_HISTORY

    st.markdown(
        f"<p style='font-size:0.78rem;color:#666;margin:0 0 4px 0;'>Context: {turn_count}/{MAX_HISTORY} turns</p>",
        unsafe_allow_html=True
    )
    st.progress(fill)
    if fill >= 0.7:
        st.caption("⚠️ Approaching context limit.")
    if st.button("Compact", disabled=(turn_count == 0), use_container_width=True):
        agent.compact()
        st.session_state.messages.append({"role": "assistant", "content": "*— History compacted —*"})
        st.rerun()

    st.markdown("<hr style='margin:10px 0;opacity:0.25;border:none;border-top:1px solid #ccc;'>", unsafe_allow_html=True)

    # Response style — horizontal radio, small label and hint
    st.markdown("<p style='font-size:0.78rem;color:#666;margin:0 0 4px 0;'>Response style</p>", unsafe_allow_html=True)
    selected = st.radio(
        "", list(STYLE_INSTRUCTIONS.keys()),
        index=0, format_func=str.capitalize,
        label_visibility="collapsed", horizontal=True
    )
    if agent:
        agent.response_style = selected
    st.markdown(
        f"<p style='font-size:0.72rem;color:#aaa;margin-top:3px;'>{STYLE_INSTRUCTIONS[selected]}</p>",
        unsafe_allow_html=True
    )

# --- Chat history ---
st.title("📜 ShakespeareGPT")
st.caption("Ask anything about Shakespeare's plays and sonnets.")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-bubble"><span>{msg["content"]}</span></div>',
            unsafe_allow_html=True
        )
    else:
        # Assistant: small model label + full-width markdown response
        st.markdown('<div class="llm-label">llama3</div>', unsafe_allow_html=True)
        st.markdown(msg["content"])

# --- New input ---
if prompt := st.chat_input("Ask about Shakespeare..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(
        f'<div class="user-bubble"><span>{prompt}</span></div>',
        unsafe_allow_html=True
    )

    # ReAct loop (blocking) then stream Final Answer full-width
    with st.spinner("Reasoning and searching documents..."):
        step2_prompt = agent._prepare_answer_prompt(prompt)

    st.markdown('<div class="llm-label">llama3</div>', unsafe_allow_html=True)
    answer = st.write_stream(agent._stream_answer(step2_prompt))
    agent._record_turn(prompt, answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
