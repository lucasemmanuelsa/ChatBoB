import os
import json
from datetime import datetime
from typing import Dict, Any


def save_session_data(state: Dict[str, Any], base_dir: str = "conversation_logs"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    session_dir = os.path.join(base_dir, f"session_{timestamp}")

    os.makedirs(session_dir, exist_ok=True)

    # -------------------------
    # 1. Conversa (contexto do agente)
    # -------------------------
    with open(os.path.join(session_dir, "conversation.json"), "w", encoding="utf-8") as f:
        json.dump(
            state.get("context_messages", []),
            f,
            indent=2,
            ensure_ascii=False
        )

    # -------------------------
    # 2. JSON final extraído
    # -------------------------
    with open(os.path.join(session_dir, "finaljson.json"), "w", encoding="utf-8") as f:
        json.dump(
            state.get("final_json"),
            f,
            indent=2,
            ensure_ascii=False
        )

    # -------------------------
    # 3. Logs internos do agente
    # -------------------------
    with open(os.path.join(session_dir, "agent_logs.json"), "w", encoding="utf-8") as f:
        json.dump(
            state.get("logs", []),
            f,
            indent=2,
            ensure_ascii=False
        )

    return session_dir
