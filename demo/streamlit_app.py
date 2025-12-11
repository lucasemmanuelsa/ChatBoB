import streamlit as st
import os
import sys
from typing import Dict, Any

# Garantir import local do pacote `app`
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.append(repo_root)

from app.core.schema import Schema
from app.core.extractor import ExtractorAgent

st.set_page_config(page_title="Extractor Agent", layout="wide")

# Inicialização do agente e do estado
schema_path = os.path.join(repo_root, "examples", "schema_example.json")
schema = Schema.load_from_file(schema_path)
agent = ExtractorAgent(schema)

DEFAULT_STATE: Dict[str, Any] = {
    "last_user_message": "",
    "last_asked_question": "",
    "schema": schema,
    "extracted": {},
    "missing_fields": [],
    "question_to_ask": None,
    "final_json": None,
    "context_messages": [],
    "status_finished": False,
    "next": None,
    "logs": [],
}

if "state" not in st.session_state:
    st.session_state.state = DEFAULT_STATE.copy()

agent = agent


def run_graph_with_input(user_message: str):
    """Atualiza o state com a mensagem do usuário e invoca o agente.

    Mescla apenas as chaves retornadas pelo agente no state existente.
    """
    state = st.session_state.state
    state["last_user_message"] = user_message
    state.setdefault("context_messages", []).append({"role": "user", "content": user_message})

    # feed_message do seu agent espera o state e retorna updates
    updates = agent.feed_message(user_message, state)

    if isinstance(updates, dict):
        state.update(updates)

    st.session_state.state = state


st.title("🧠 Agente Extrator — Chat")

state = st.session_state.state

# Se o agente deixou uma pergunta, mostrar e esperar resposta
if state.get("question_to_ask"):
    st.subheader("❓ O agente precisa de mais informações:")
    st.info(state["question_to_ask"])
    answer = st.text_input("Sua resposta:", key="agent_answer")
    if st.button("Enviar resposta", key="btn_answer"):
        # limpar indicador de pergunta e enviar resposta ao agente
        state["question_to_ask"] = None
        run_graph_with_input(answer)

else:
    user_text = st.text_input("Mensagem:", key="user_message")
    if st.button("Enviar", key="btn_main"):
        run_graph_with_input(user_text)

st.divider()
st.subheader("📌 Estado Atual do Agente")

st.json({
    "extracted": state.get("extracted"),
    "missing_fields": state.get("missing_fields"),
    "next": state.get("next"),
})

if state.get("last_asked_question"):
    st.write("**Última pergunta gerada:**", state["last_asked_question"])

st.divider()
st.subheader("📜 Logs")
for log in state.get("logs", []):
    st.write("•", log)
