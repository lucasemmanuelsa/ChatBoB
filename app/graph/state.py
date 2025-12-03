from typing import Dict, Any, Optional, TypedDict
from pydantic import BaseModel

class AgentState(TypedDict):
    last_user_message: Optional[str] = None
    schema: Optional[Any] = None
    collected: Dict[str, Any] = {}
    extracted: Optional[Dict[str, Any]] = None
    missing_fields: Optional[list] = None
    question_to_ask: Optional[str] = None
    final_json: Optional[Dict[str, Any]] = None
    context_messages: Optional[list] = None
    status_finished: bool = False
    next: str