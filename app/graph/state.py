from typing import Dict, Any, TypedDict
from app.core.schema import Schema

class AgentState(TypedDict):
    last_user_message: str
    last_asked_question: str
    schema: Schema
    extracted: Dict[str, Any]
    missing_fields: list
    question_to_ask: str
    final_json: Dict[str, Any]
    context_messages: list
    status_finished: bool
    next: str
    logs: list