from langchain.prompts import ChatPromptTemplate

from app.core.llm import get_llm
from app.core.prompts import (
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
            "context_messages" : state.get("context_messages", ""),
            "last_asked_question": state.get("last_asked_question", ""),
            "last_user_message": state.get("last_user_message", "")
    }
    ).strip().lower()

    if 'EXTRACT' in intent:
        return {"next": "extractor", "logs": state["logs"]}
    return {"next": "ask", "logs": state["logs"]}

def extractor_node(state):

    user_message = state["last_user_message"]
    schema = state["schema"]
    collected = state.get("collected", {})
    state['logs'].append("EXTRACTOR: extraindo informações...")
    template = ChatPromptTemplate.from_template(EXTRACT_FROM_MESSAGE_PROMPT)
    chain = template | llm
    resp = chain.invoke({
        "schema": schema.fields,
        "message": user_message,
        "collected": collected
        }
    )

    return {"extracted": resp, "next": "missing"}

def missing_node(state):
    schema_fields = state["schema"].fields
    collected = state.get("collected", {})

    missing = [f for f in schema_fields if f not in collected]

    out = {"missing_fields": missing}
    if missing:
        out["next"] = "ask"
    else:
        out["next"] = "final"
    return out

def ask_node(state):
    missing = state["missing_fields"]
    if not missing:
        return {}

    field = missing[0]
    description = state["schema"].fields[field]["description"]

    response = llm.invoke(
        GENERATE_QUESTION_PROMPT,
        input_variables={
            "field": field,
            "description": description,
            "collected": state.get("collected", {})
        }
    )

    return {"question_to_ask": response}

def output_node(state):
    resp = llm.invoke(
        FINAL_JSON_PROMPT,
        input_variables={
            "schema": state["schema"].fields,
            "collected": state.get("collected", {}),
            "missing": state.get("missing_fields", [])
        }
    )
    return {"final_json": resp}
