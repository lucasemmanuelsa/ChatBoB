import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.schema import Schema
from app.core.extractor import ExtractorAgent
from app.graph.state import AgentState

schema = Schema.load_from_file("/home/lucas/tcc/chat-data-extractor/examples/schema_example.json")
agent = ExtractorAgent(schema)

if "state" not in st.session_state:
    st.session_state.state = AgentState()

st.title("🤖 ChatBob")

msg = st.chat_input("Digite algo...")

if msg:
    state = st.session_state.state
    new_state = agent.feed_message(msg, state)
    st.session_state.state = AgentState(**new_state)

    st.write("### Estado Atual")
    st.json(st.session_state.state.dict())
