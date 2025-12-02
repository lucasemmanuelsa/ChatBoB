from langgraph.graph import StateGraph
from app.graph.state import AgentState
from app.graph.nodes import (
    extract_from_message,
    identify_missing_fields,
    generate_question,
    generate_final_json
)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("extract", extract_from_message)
    graph.add_node("missing", identify_missing_fields)
    graph.add_node("ask", generate_question)
    graph.add_node("final", generate_final_json)

    graph.set_entry_point("extract")
    graph.add_edge("extract", "missing")
    graph.add_edge("missing", "ask")
    graph.add_edge("missing", "final")  # finaliza se não houver missing

    return graph.compile()
