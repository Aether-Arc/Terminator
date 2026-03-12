from langgraph.graph import StateGraph, END

from langgraph.checkpoint.sqlite import SqliteSaver # 🚀 UPGRADED CHECKPOINTER

from typing import TypedDict, Any, List, Annotated

import operator

import sqlite3

import os
from memory.vector_store import search_memory
from learning.policy_memory import RLPolicyMemory

# Import our new modular components
from orchestrator.agent_router import AgentRouter
from orchestrator.task_manager import TaskManager
from orchestrator.reflection_loop import ReflectionLoop

class GraphState(TypedDict):
    event_data: dict
    candidates: List[dict]
    plan: dict
    score: float
    iterations: int
    schedule: Any
    requires_approval: bool
        
    # 🚀 NEW: THE IMMUTABLE SCRATCHPAD
    # Using Annotated with operator.add means agents CANNOT overwrite this list.
    # Every time an agent returns {"audit_log": ["Did X"]}, it appends to the history.
    audit_log: Annotated[List[str], operator.add] 
    
    # 🚀 NEW: GLOBAL DIRECTIVES
    # This string is passed to every single agent so they never "forget" the core rules
    # no matter how long the conversation gets.
    global_constraints: str 
    

    past_context: str 
    critic_feedback: str 
    simulation_metrics: Any 
    marketing_copy: str     
    email_logs: list        
    active_agents: List[str]       
    pending_agents: List[str]      
    agent_outputs: dict            

def build_graph(planner, critic, scheduler, marketing, email, world_model, budget_agent, volunteer_agent, attendance_predictor, sponsor_agent):
    workflow = StateGraph(GraphState)
    rl_memory = RLPolicyMemory()
    reflection_engine = ReflectionLoop(critic, rl_memory)

    async def run_planner(state):
        event_data = state["event_data"]
        
        crowd_size = event_data.get("expected_crowd", 500)
        
        search_query = f"Event Name: {event_data.get('name', 'Event')}. Theme: {event_data.get('marketing_prompt', '')}"
        past_events = search_memory(search_query)
        
        event_data["learned_strategy"] = rl_memory.get_best_action(state=str(crowd_size))
        event_data["historical_context"] = str(past_events)
        if state.get("critic_feedback"):
            event_data["critic_feedback"] = state["critic_feedback"]
            
        plan_list = await planner.generate_multiple_plans(event_data, count=3)
        return {"candidates": plan_list, "iterations": state.get("iterations", 0) + 1,"audit_log": [f"Planner generated {len(plan_list)} candidate schedules."], "past_context": str(past_events)}

    async def run_world_model(state):
        sim_metrics = [world_model.simulate_crowd_flow(state["event_data"], p) for p in state.get("candidates", [])]
        return {"simulation_metrics": sim_metrics}

    def route_critic(state):
        return "scheduler" if state["score"] > 80 or state["iterations"] >= 2 else "planner"

    def run_scheduler(state):
        schedule = scheduler.create_schedule(state["plan"])
        return {"schedule": schedule, "requires_approval": True}

    # Modular Execution Wrappers
    async def run_marketing(state):
        state["event_data"]["schedule"] = state["schedule"] 
        return {"marketing_copy": await marketing.generate_campaign(state["event_data"])}

    def run_email(state):
        return {"email_logs": email.send_invites(state["event_data"].get("csv_content", ""), "Your optimal schedule is locked!")}

    async def run_budget(state):
        outputs = state.get("agent_outputs", {})
        outputs["budget"] = await budget_agent.calculate(state["event_data"])
        return {"agent_outputs": outputs}

    async def run_volunteer(state):
        outputs = state.get("agent_outputs", {})
        outputs["volunteer"] = await volunteer_agent.assign_shifts(state["event_data"], state["schedule"])
        return {"agent_outputs": outputs}
        
    def run_attendance_ml(state):
        outputs = state.get("agent_outputs", {})
        outputs["attendance_forecast"] = attendance_predictor.predict_attendance(state["event_data"].get("expected_crowd", 500))
        return {"agent_outputs": outputs}
        
    async def run_sponsor(state):
        outputs = state.get("agent_outputs", {})
        outputs["sponsor"] = await sponsor_agent.draft_sponsorships(state["event_data"])
        return {"agent_outputs": outputs}

    # Register Nodes
    workflow.add_node("planner", run_planner)
    workflow.add_node("world_model", run_world_model)
    workflow.add_node("critic", reflection_engine.evaluate_candidates)
    workflow.add_node("scheduler", run_scheduler)
    workflow.add_node("supervisor", TaskManager.run_supervisor)
    workflow.add_node("queue_manager", AgentRouter.pop_queue)
    workflow.add_node("marketing", run_marketing)
    workflow.add_node("email", run_email)
    workflow.add_node("budget", run_budget)
    workflow.add_node("volunteer", run_volunteer)
    workflow.add_node("attendance_ml", run_attendance_ml)
    workflow.add_node("sponsor", run_sponsor)

    # Draw Edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "world_model")
    workflow.add_edge("world_model", "critic")
    workflow.add_conditional_edges("critic", route_critic, {"scheduler": "scheduler", "planner": "planner"})
    
    workflow.add_edge("scheduler", "supervisor")
    workflow.add_edge("supervisor", "queue_manager")
    
    workflow.add_conditional_edges("queue_manager", AgentRouter.dynamic_router, {
        "marketing": "marketing", "email": "email", "budget": "budget",
        "volunteer": "volunteer", "attendance_ml": "attendance_ml", "sponsor": "sponsor", END: END
    })
    
    for agent in ["marketing", "email", "budget", "volunteer", "attendance_ml", "sponsor"]:
        workflow.add_edge(agent, "queue_manager")

    # 🚀 THE HACKATHON CHEAT CODE: Async-to-Sync Checkpointer Bridge
    # This bypasses the need for `aiosqlite` and complex context managers
    from langgraph.checkpoint.sqlite import SqliteSaver
    
    class AsyncSqliteSaverBridge(SqliteSaver):
        async def aget_tuple(self, config):
            return self.get_tuple(config)
            
        async def aput(self, config, checkpoint, metadata, new_versions):
            return self.put(config, checkpoint, metadata, new_versions)
            
        async def aput_writes(self, config, writes, task_id):
            return self.put_writes(config, writes, task_id)

    # Create the persistent SQLite database
    os.makedirs(os.path.join(os.getcwd(), "memory"), exist_ok=True)
    db_path = os.path.join(os.getcwd(), "memory", "swarm_threads.sqlite")
    
    # check_same_thread=False allows our async FastAPI routes to access it safely
    conn = sqlite3.connect(db_path, check_same_thread=False)
    
    # Attach our custom bridge class!
    memory = AsyncSqliteSaverBridge(conn)
    
    return workflow.compile(checkpointer=memory, interrupt_before=["supervisor"])