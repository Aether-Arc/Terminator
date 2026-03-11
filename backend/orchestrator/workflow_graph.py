from langgraph.graph import StateGraph, END
from typing import TypedDict, Any
from memory.vector_store import search_memory, store_memory
from learning.policy_memory import RLPolicyMemory

class GraphState(TypedDict):
    event_data: dict
    plan: dict
    score: float
    iterations: int
    schedule: Any
    marketing_copy: str
    requires_approval: bool
    past_context: str 
    critic_feedback: str 
    simulation_metrics: dict # 🧠 NEW: Holds physics simulation data

def build_graph(planner, critic, scheduler, marketing, world_model):
    workflow = StateGraph(GraphState)
    rl_memory = RLPolicyMemory()

    async def run_planner(state):
        event_data = state["event_data"]
        crowd_size = event_data.get("expected_crowd", 500)
        event_name = event_data.get("name", "Unknown Event")
        theme = event_data.get("marketing_prompt", "")
        
        # VectorDB & RL Context
        search_query = f"Event Name: {event_name}. Theme: {theme}. Crowd size: {crowd_size}"
        past_events = search_memory(search_query)
        best_strategy = rl_memory.get_best_action(state=str(crowd_size))
        
        event_data["learned_strategy"] = best_strategy
        event_data["historical_context"] = str(past_events)
        
        if state.get("critic_feedback"):
            event_data["critic_feedback"] = state["critic_feedback"]
            
        plan_list = await planner.generate_multiple_plans(event_data, count=1)
        return {"plan": plan_list[0], "iterations": state.get("iterations", 0) + 1, "past_context": str(past_events)}

    async def run_world_model(state):
        # 🧠 COGNITIVE LOOP PILLAR 2: Simulate physical constraints & delays
        sim_results = world_model.simulate_crowd_flow(state["event_data"], state["plan"])
        return {"simulation_metrics": sim_results}

    async def run_critic(state):
        # 🧠 COGNITIVE LOOP PILLAR 3: Critic evaluates Plan + Physics Simulation
        plan_str = str(state.get("plan", ""))
        sim_str = str(state.get("simulation_metrics", {}))
        
        combined_context = f"PROPOSED PLAN:\n{plan_str}\n\nWORLD MODEL PHYSICS SIMULATION:\n{sim_str}"
        review = await critic.review(combined_context)
        
        score = review.get("score", 50)
        
        crowd_size = state["event_data"].get("expected_crowd", 500)
        rl_memory.update_policy(state=str(crowd_size), action="selected_plan", reward=score, next_state="execution")
        
        return {"score": score, "critic_feedback": review.get("feedback", "")}

    def route_critic(state):
        if state["score"] > 80 or state["iterations"] >= 3:
            return "scheduler"
        return "planner"

    def run_scheduler(state):
        schedule = scheduler.create_schedule(state["plan"])
        return {"schedule": schedule, "requires_approval": True}

    workflow.add_node("planner", run_planner)
    workflow.add_node("world_model", run_world_model)
    workflow.add_node("critic", run_critic)
    workflow.add_node("scheduler", run_scheduler)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "world_model")
    workflow.add_edge("world_model", "critic")
    workflow.add_conditional_edges("critic", route_critic, {"scheduler": "scheduler", "planner": "planner"})
    workflow.add_edge("scheduler", END) 

    return workflow.compile()