from langgraph.graph import StateGraph


def build_graph(planner, scheduler, marketing):

    graph = StateGraph(dict)

    graph.add_node("planner", planner.generate_plan)
    graph.add_node("scheduler", scheduler.build_schedule)
    graph.add_node("marketing", marketing.generate_campaign)

    graph.add_edge("planner", "scheduler")
    graph.add_edge("scheduler", "marketing")

    graph.set_entry_point("planner")

    return graph.compile()