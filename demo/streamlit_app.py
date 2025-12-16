import streamlit as st
import os
import sys
from typing import Dict, Any

# Caminho para o repo
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.append(repo_root)

from app.core.schema import Schema
from app.core.extractor import ExtractorAgent

st.set_page_config(page_title="ChatBoB", page_icon="🤖")

# Carrega schema e agente
schema_path = os.path.join(repo_root, "examples", "schema_example.json")
schema = Schema.load_from_file(schema_path)
agent = ExtractorAgent(schema)

# Estado inicial padrão
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
    "messages": []  # mensagens exibidas no chat
}

# Inicializa state + mensagem inicial automática
if "state" not in st.session_state:
    st.session_state.state = DEFAULT_STATE.copy()
    st.session_state.state["messages"].append({
        "role": "assistant",
        "content": "Olá! Sou o **ChatBoB**, seu agente extrator inteligente. Para começarmos: **qual é o seu nome?**"
    })


def run_graph_with_input(user_message: str):
    """Envia mensagem para o agente e salva os resultados no state."""
    state = st.session_state.state

    # salva no histórico visual
    state["messages"].append({"role": "user", "content": user_message})

    # salva no contexto interno
    state["last_user_message"] = user_message
    state["context_messages"].append({"role": "user", "content": user_message})

    # o agente gera updates
    updates = agent.feed_message(user_message, state)
    if isinstance(updates, dict):
        state.update(updates)

    # se o agente fez alguma pergunta, ela aparece no chat
    if state.get("question_to_ask"):
        state["messages"].append({
            "role": "assistant",
            "content": state["question_to_ask"]
        })

    st.session_state.state = state


st.title("🤖 ChatBoB – Agente Extrator")

state = st.session_state.state

# -------------------------
#  EXIBE TODAS AS MENSAGENS DO CHAT
# -------------------------
for msg in state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
#  INPUT DO USUÁRIO
# -------------------------
user_message = st.chat_input("Digite sua mensagem...")

if user_message:
    with st.chat_message("user"):
        st.markdown(user_message)

    # indicador visual de processamento
    with st.spinner("ChatBoB está pensando..."):
        run_graph_with_input(user_message)

    # recarrega para exibir mensagem nova
    st.rerun()

# -------------------------
#  BLOCO DEBAIXO DO CHAT — STATE + LOGS
# -------------------------

st.markdown("---")

with st.expander("📌 Estado Atual do Agente"):
    st.json({
        "extracted": state.get("extracted"),
        "missing_fields": state.get("missing_fields"),
        "next": state.get("next"),
        "last_asked_question": state.get("last_asked_question"),
        "status_finished": state.get("status_finished"),
    })

with st.expander("📜 Logs do Agente"):
    for log in state.get("logs", []):
        st.write("•", log)
