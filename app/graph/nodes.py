from langchain.prompts import ChatPromptTemplate
from langgraph.graph import END
import json
from app.core.llm import get_llm
from app.core.prompts import (
    IDENTIFY_MISSING_FIELDS_PROMPT,
    STARTER_PROMPT,
    EXTRACT_FROM_MESSAGE_PROMPT,
    GENERATE_QUESTION_PROMPT,
    FINAL_JSON_PROMPT
)

llm = get_llm()

def starter_node(state):
    template = ChatPromptTemplate.from_template(STARTER_PROMPT)
    chain = template | llm

    state["logs"].append("STARTER: Iniciando classificação de intenção...")

    intent = chain.invoke({
            "context_messages" : state.get("context_messages"),
            "last_asked_question": state.get("last_asked_question"),
            "last_user_message": state.get("last_user_message")
    }
    ).content.strip().upper()

    state["logs"].append(f"STARTER: Intenção classificada como {intent}")


    if 'EXTRACT' in intent:
        return {"next": "extractor", "logs": state["logs"]}
    return {"next": "ask", "logs": state["logs"]}

def extractor_node(state):

    state['logs'].append("EXTRACTOR: extraindo informações...")
    template = ChatPromptTemplate.from_template(EXTRACT_FROM_MESSAGE_PROMPT)

    chain = template | llm

    resp = chain.invoke({
        "schema": state["schema"].fields,
        "last_user_message": state["last_user_message"],
        "last_asked_question": state["last_asked_question"],
        "extracted": state["extracted"]
        }
    ).content.strip()

    try:
        partial = json.loads(resp)
    except Exception:
        partial = {}
    
    extracted = state["extracted"]
    extracted.update(partial)

    state['logs'].append(f"EXTRACTOR: extraído {partial}")
    return {"extracted": extracted, "next": "missing", "logs": state["logs"]}

def missing_node(state):
    state["logs"].append("MISSING: verificando campos faltantes via LLM...")
    
    template = ChatPromptTemplate.from_template(IDENTIFY_MISSING_FIELDS_PROMPT)
    chain = template | llm

    resp = chain.invoke({
        "schema": state["schema"].fields,
        "extracted": state["extracted"]
    }).content.strip()


    try:
        parsed = json.loads(resp)
        missing = parsed.get("missing", [])
    except Exception:
        schema_fields = state["schema"].fields
        extracted = state.get("extracted", {})
        missing = [field for field in schema_fields if field not in extracted or not extracted[field]]

    state["logs"].append(f"MISSING: campos faltantes identificados: {missing}")

    out = {"missing_fields": missing, "logs": state["logs"]}
    out["next"] = "ask" if missing else "output"
    return out

def ask_node(state):

    state["logs"].append("ASK: gerando pergunta para campo faltante...")
    missing = state.get("missing_fields", [])

    if not missing:
        state["logs"].append("ASK: campo vazio")

    template = ChatPromptTemplate.from_template(GENERATE_QUESTION_PROMPT)
    chain = template | llm

    raw = chain.invoke({
        "context_messages": state["context_messages"],
        "extracted": state["extracted"],
        "missing_fields": missing,
        "schema": state["schema"].fields,
        "last_asked_question": state["last_asked_question"],
        "last_user_message": state["last_user_message"]
    }).content.strip()

    state["context_messages"].append({
        "role": "assistant",
        "content": raw
    })

    state["logs"].append(f"ASK: pergunta gerada: {raw}")

    return {
        "question_to_ask": raw,
        "last_asked_question": raw,
        "context_messages": state["context_messages"],
        "next": None,
        "logs": state["logs"]
        }

def output_node(state):
    template = ChatPromptTemplate.from_template(FINAL_JSON_PROMPT)
    chain = template | llm
    state["logs"].append("OUTPUT: gerando JSON final...")
    resp = chain.invoke({
        "schema": state["schema"].fields,
        "extracted": state["extracted"],
        "missing": state["missing_fields"]
    }).content.strip()

    state["logs"].append(f"OUTPUT: JSON final gerado: {resp}")

    try:
        resp = json.loads(resp)
    except Exception:
        resp = {}

    return {"final_json": resp, "status_finished": True, "logs": state["logs"], "next": END}
