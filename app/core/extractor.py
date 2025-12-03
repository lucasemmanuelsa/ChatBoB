from app.graph.builder import build_graph
from app.core.schema import Schema

class ExtractorAgent:
    def __init__(self, schema: Schema):
        self.schema = schema
        self.graph = build_graph()
        print(self.graph)

    def feed_message(self, message: str, state: dict):
        state["last_user_message"] = message
        state["schema"] = self.schema
        return self.graph.invoke(state)