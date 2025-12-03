from app.core.llm import get_llm
from app.core.prompts import (
    EXTRACT_FROM_MESSAGE_PROMPT,
    GENERATE_QUESTION_PROMPT,
    FINAL_JSON_PROMPT
)

llm = get_llm()

def extract_from_message(state):
    user_message = state["last_user_message"]
    schema = state["schema"]
    collected = state.get("collected", {})

    resp = llm.invoke(
        EXTRACT_FROM_MESSAGE_PROMPT,
        input_variables={
            "schema": schema.fields,
            "message": user_message,
            "collected": collected
        }
    )

    return {"extracted": resp, "next": "missing"}

def identify_missing_fields(state):
    schema_fields = state["schema"].fields
    collected = state.get("collected", {})

    missing = [f for f in schema_fields if f not in collected]

    out = {"missing_fields": missing}
    if missing:
        out["next"] = "ask"
    else:
        out["next"] = "final"
    return out

def generate_question(state):
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

def generate_final_json(state):
    resp = llm.invoke(
        FINAL_JSON_PROMPT,
        input_variables={
            "schema": state["schema"].fields,
            "collected": state.get("collected", {}),
            "missing": state.get("missing_fields", [])
        }
    )
    return {"final_json": resp}
