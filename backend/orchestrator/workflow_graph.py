from langgraph.graph import StateGraph, END
from typing import TypedDict, Any

class GraphState(TypedDict):
    event_data: dict
    plan: str
    schedule: Any
    marketing_copy: str

def build_graph(planner, scheduler, marketing):
    workflow = StateGraph(GraphState)

    # Wrap agent calls to handle state dictionary properly
    def run_planner(state):
        return {"plan": planner.generate_plan(state["event_data"])}

    def run_scheduler(state):
        # FIXED: Changed from build_schedule to create_schedule
        return {"schedule": scheduler.create_schedule(state.get("plan", {"sessions": []}))}

    def run_marketing(state):
        return {"marketing_copy": marketing.generate_campaign(state["event_data"])}

    workflow.add_node("planner", run_planner)
    workflow.add_node("scheduler", run_scheduler)
    workflow.add_node("marketing", run_marketing)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "scheduler")
    workflow.add_edge("scheduler", "marketing")
    workflow.add_edge("marketing", END)

    return workflow.compile()