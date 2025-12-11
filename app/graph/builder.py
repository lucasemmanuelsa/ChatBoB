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

    # Entrypoint: iniciar no nó "starter" para que o fluxo seja decidido pelo starter
    graph.set_entry_point("starter")

    graph.add_conditional_edges(
        "starter",
        lambda state: state["next"],
        {
            "extractor": "extractor",
            "ask": "ask",
        }
    )

    graph.add_edge("extractor", "missing")
    
    graph.add_conditional_edges(
        "missing",
        lambda state: state["next"],
        {
            "ask": "ask",
            "output": "output"
        }
    )


    graph.add_edge("output", END)
    return graph.compile()
