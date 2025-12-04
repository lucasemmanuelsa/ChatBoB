from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes import (
    starter_node,
    extractor_node,
    missing_node,
    ask_node,
    output_node
)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("starter", starter_node)
    graph.add_node("extractor", extractor_node)
    graph.add_node("missing", missing_node)
    graph.add_node("ask", ask_node)
    graph.add_node("output", output_node)

    graph.set_entry_point("extractor")
    graph.add_edge("extractor", "missing")
    graph.add_edge("missing", "ask")
    graph.add_edge("missing", "output")

    graph.add_edge("output", END)
    return graph.compile()
