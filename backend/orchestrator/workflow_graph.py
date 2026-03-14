import operator
import sqlite3
import os
import uuid
import asyncio
import json
from typing import TypedDict, Any, List, Annotated, Literal, Dict
from dataclasses import dataclass

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.memory import InMemoryStore
from langgraph.runtime import Runtime
from langgraph.types import Send, Command, interrupt
from langchain_openai import ChatOpenAI

from config import get_resilient_llm, USE_CRITIC_AGENT

# ==========================================
# 1. ADVANCED MEMORY SCHEMAS & REDUCERS
# ==========================================
@dataclass
class Context:
    user_id: str

def merge_work(existing: list[dict], new_work: list[dict]) -> list[dict]:
    """Smart Reducer: Overwrites old tasks with newer versions based on domain+task signature."""
    work_dict = {f"{w.get('domain')}_{w.get('task')}": w for w in existing}
    for w in new_work:
        work_dict[f"{w.get('domain')}_{w.get('task')}"] = w
    return list(work_dict.values())

class GraphState(TypedDict):
    event_data: dict
    plan: dict
    schedule: Any
    audit_log: Annotated[List[str], operator.add] 
    completed_work: Annotated[list[dict], merge_work] 
    agent_outputs: dict 
    user_feedback: str
    knowledge_base: Annotated[List[str], operator.add] 

class SubgraphState(TypedDict):
    event_data: dict
    schedule: list
    tasks: list[dict]
    completed_work: Annotated[list[dict], merge_work]
    knowledge_base: Annotated[list[str], operator.add]

class WorkerState(TypedDict):
    task: dict
    event_data: dict
    schedule: list

# ==========================================
# 2. TEAM 1: MARKETING SUPERVISOR
# ==========================================
def build_marketing_subgraph(marketing, comms_agent, design_agent):
    graph = StateGraph(SubgraphState)
    critic_llm = get_resilient_llm(temperature=0.1)

    async def marketing_supervisor(state: SubgraphState):
        tasks_to_dispatch = []
        completed_work = state.get("completed_work", [])
        failed_tasks = [w for w in completed_work if w.get("needs_revision", False)]
        
        if failed_tasks:
            for w in failed_tasks:
                tasks_to_dispatch.append({"domain": w["domain"], "specifics": w["task"]})
        else:
            requested = state["event_data"].get("requested_agents", ["marketing", "comms", "design"])
            if "marketing" in requested: tasks_to_dispatch.extend([{"domain": "marketing", "specifics": "Twitter Thread"}, {"domain": "marketing", "specifics": "LinkedIn Post"}])
            if "comms" in requested: tasks_to_dispatch.append({"domain": "comms", "specifics": "Draft Initial Welcome Invite (Email & WhatsApp)"})
            if "design" in requested: tasks_to_dispatch.append({"domain": "design", "specifics": "Create 3 visual social media promo cards"})
            
        return {"tasks": tasks_to_dispatch}

    def assign_marketing_workers(state: SubgraphState):
        return [Send("creative_worker", {"task": t, "event_data": state["event_data"], "schedule": state.get("schedule", [])}) for t in state["tasks"]]

    async def creative_worker(state: WorkerState):
        domain, specifics = state["task"]["domain"], state["task"]["specifics"]
        
        async def run_agent():
            if domain == "marketing": return await marketing.generate_campaign(state["event_data"], specifics)
            elif domain == "comms": return await comms_agent.draft_communications(state["event_data"], state["schedule"], specifics)
            elif domain == "design": return await design_agent.generate_cards(state["event_data"],state.get("schedule", []), specifics)

        try:
            result = await asyncio.wait_for(run_agent(), timeout=45.0)
            return {"completed_work": [{"domain": domain, "task": specifics, "output": result, "needs_revision": True}]}
        except Exception as e:
            return {"completed_work": [{"domain": domain, "task": specifics, "output": {"status": "ERROR", "error": str(e)}, "needs_revision": False}]}

    async def quality_control_critic(state: SubgraphState):
        if not USE_CRITIC_AGENT:
            reviewed_work = state.get("completed_work", [])
            for work in reviewed_work:
                work["needs_revision"] = False
            return {"completed_work": reviewed_work}
        
        reviewed_work = []
        for work in state.get("completed_work", []):
            if not work.get("needs_revision", False) or "ERROR" in str(work["output"]):
                reviewed_work.append(work)
                continue
                
            critique = await critic_llm.ainvoke(f"Review this {work['domain']} output for quality. Output ONLY 'PASS' or 'FAIL'. Output: {work['output']}")
            if "FAIL" in critique.content:
                print(f"[🔥 CRITIC] Rejecting {work['domain']} draft. Sending back for rewrite.")
                work["task"] = f"REWRITE: {work['task']} (Make it more engaging)"
                work["needs_revision"] = True 
            else:
                work["needs_revision"] = False
                
            reviewed_work.append(work)
            
        return {"completed_work": reviewed_work}
    
    def route_critic(state: SubgraphState):
        if any(w.get("needs_revision", False) for w in state.get("completed_work", [])):
            return "marketing_supervisor"
        return END

    graph.add_node("marketing_supervisor", marketing_supervisor)
    graph.add_node("creative_worker", creative_worker)
    graph.add_node("quality_control_critic", quality_control_critic)
    
    graph.add_edge(START, "marketing_supervisor")
    graph.add_conditional_edges("marketing_supervisor", assign_marketing_workers, ["creative_worker"])
    graph.add_edge("creative_worker", "quality_control_critic")
    graph.add_conditional_edges("quality_control_critic", route_critic, ["marketing_supervisor", END])
    
    return graph.compile()

# ==========================================
# 3. TEAM 2: OPERATIONS SUPERVISOR
# ==========================================
def build_operations_subgraph(budget_agent, volunteer_agent, sponsor_agent, resource_agent):
    graph = StateGraph(SubgraphState)

    async def ops_supervisor(state: SubgraphState):
        requested = state["event_data"].get("requested_agents", ["budget", "volunteer", "sponsor", "resource"])
        tasks = []
        if "budget" in requested: tasks.append({"domain": "budget", "specifics": "Calculate Venue Estimates"})
        if "volunteer" in requested: tasks.append({"domain": "volunteer", "specifics": "Assign Desk Shifts"})
        if "sponsor" in requested: tasks.append({"domain": "sponsor", "specifics": "Draft Sponsors Pitch"})
        if "resource" in requested: tasks.append({"domain": "resource", "specifics": "Allocate physical rooms"})
        return {"tasks": tasks}

    def assign_ops_workers(state: SubgraphState):
        return [Send("logistics_worker", {"task": t, "event_data": state["event_data"], "schedule": state.get("schedule", [])}) for t in state["tasks"]]

    async def logistics_worker(state: WorkerState):
        domain, specifics = state["task"]["domain"], state["task"]["specifics"]
        
        async def run_agent():
            if domain == "budget": return await budget_agent.calculate(state["event_data"],state["schedule"], specifics)
            elif domain == "resource": return await resource_agent.allocate(state["event_data"], state["schedule"], specifics)
            elif domain == "volunteer": return await volunteer_agent.assign_shifts(state["event_data"], state["schedule"], specifics)
            elif domain == "sponsor": return await sponsor_agent.draft_sponsorships(state["event_data"], specifics)

        try:
            result = await asyncio.wait_for(run_agent(), timeout=45.0)
            return {"completed_work": [{"domain": domain, "task": specifics, "output": result}]}
        except Exception as e:
            return {"completed_work": [{"domain": domain, "task": specifics, "output": {"status": "ERROR", "error": str(e)}}]}

    graph.add_node("ops_supervisor", ops_supervisor)
    graph.add_node("logistics_worker", logistics_worker)
    graph.add_edge(START, "ops_supervisor")
    graph.add_conditional_edges("ops_supervisor", assign_ops_workers, ["logistics_worker"])
    graph.add_edge("logistics_worker", END)
    return graph.compile()

# ==========================================
# 4. CHIEF ORCHESTRATOR (MAIN GRAPH)
# ==========================================
def build_graph(planner, scheduler, marketing, comms_agent, budget_agent, volunteer_agent, sponsor_agent, updater_agent, resource_agent, design_agent):
    workflow = StateGraph(GraphState, context_schema=Context)

    async def run_planner(state: GraphState, runtime: Runtime[Context]) -> Command[Literal["scheduler"]]:
        event_data = state["event_data"]
        
        namespace = (runtime.context.user_id, "past_events")
        memories = await runtime.store.asearch(namespace, query=event_data.get('name', ''), limit=3)
        historical_context = "\n".join([m.value.get("event_summary", "") for m in memories]) if memories else ""
        
        hive_mind = "\n".join(state.get("knowledge_base", []))
        event_data["historical_context"] = f"Past History: {historical_context}\n\nRecent Insights: {hive_mind}"
            
        plan_list = await planner.generate_multiple_plans(event_data, count=1)
        await runtime.store.aput(namespace, str(uuid.uuid4()), {"event_summary": f"Planned {event_data.get('name')} with parameters: {event_data.get('user_constraints')}"})

        return Command(update={"plan": plan_list[0], "audit_log": ["Zero-shot plan generated."]}, goto="scheduler")

    async def run_scheduler(state: GraphState):
        schedule = await scheduler.create_schedule(state["plan"])
        return {"schedule": schedule}

    # 🚀 Parallel Branching
    def chief_orchestrator(state: GraphState):
        return [
            Send("marketing_team", {"event_data": state["event_data"], "schedule": state["schedule"]}),
            Send("operations_team", {"event_data": state["event_data"], "schedule": state["schedule"]})
        ]

    async def finalize_results(state: GraphState) -> Command[Literal["human_review"]]:
        latest_work = state.get("completed_work", [])
        
        outputs = {
            "marketing": [w for w in latest_work if w["domain"] == "marketing"],
            "comms": [w for w in latest_work if w["domain"] == "comms"],
            "design": [w for w in latest_work if w["domain"] == "design"],
            "operations": [w for w in latest_work if w["domain"] not in ["marketing", "comms", "design"]]
        }
        return Command(update={"agent_outputs": outputs}, goto="human_review")

    def human_review(state: GraphState) -> Command[Literal["__end__", "updater_node", "planner", "human_review"]]:
        feedback = interrupt("Review everything. Edit directly, chat to modify, or approve.")
        action = feedback.get("action", "prompt")
        
        if action == "approve": return Command(update={"audit_log": ["Approved all assets."]}, goto=END)
        elif action == "direct_edit": 
            return Command(update={"schedule": feedback.get("schedule", state["schedule"]), "agent_outputs": feedback.get("agent_outputs", state["agent_outputs"])}, goto="human_review")
        elif action == "prompt": return Command(update={"user_feedback": feedback.get("message", "")}, goto="updater_node")
        else: return Command(update={"event_data": {"user_constraints": feedback.get("message", "")}, "completed_work": []}, goto="planner")

    async def updater_node(state: GraphState) -> Command[Literal["human_review"]]:
        new_schedule, new_outputs = await updater_agent.process_update(instructions=state["user_feedback"], schedule=state.get("schedule"), outputs=state.get("agent_outputs"))
        return Command(update={"schedule": new_schedule, "agent_outputs": new_outputs}, goto="human_review")
    
    # ==========================================
    # 🚀 STATE ISOLATION WRAPPERS
    # ==========================================
    marketing_compiled = build_marketing_subgraph(marketing, comms_agent, design_agent)
    operations_compiled = build_operations_subgraph(budget_agent, volunteer_agent, sponsor_agent, resource_agent)

    async def marketing_team_node(state: dict):
        # Runs the subgraph but ONLY returns the deduplicated completed_work
        result = await marketing_compiled.ainvoke(state)
        return {"completed_work": result.get("completed_work", [])}

    async def operations_team_node(state: dict):
        result = await operations_compiled.ainvoke(state)
        return {"completed_work": result.get("completed_work", [])}

    # ==========================================
    # GRAPH ASSEMBLY
    # ==========================================
    workflow.add_node("planner", run_planner)
    workflow.add_node("scheduler", run_scheduler)
    
    # 🚀 ADD THE WRAPPER NODES INSTEAD OF THE RAW SUBGRAPHS
    workflow.add_node("marketing_team", marketing_team_node)
    workflow.add_node("operations_team", operations_team_node)
    
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "scheduler")
    
    # Router spawns the wrappers concurrently
    workflow.add_conditional_edges("scheduler", chief_orchestrator, ["marketing_team", "operations_team"])
    
    workflow.add_node("finalize", finalize_results)
    workflow.add_edge("marketing_team", "finalize")
    workflow.add_edge("operations_team", "finalize")
    
    workflow.add_node("human_review", human_review)
    workflow.add_node("updater_node", updater_node)

    class AsyncSqliteSaverBridge(SqliteSaver):
        async def aget_tuple(self, config): return self.get_tuple(config)
        async def aput(self, config, checkpoint, metadata, new_versions): return self.put(config, checkpoint, metadata, new_versions)
        async def aput_writes(self, config, writes, task_id): return self.put_writes(config, writes, task_id)

    os.makedirs(os.path.join(os.getcwd(), "memory"), exist_ok=True)
    conn = sqlite3.connect(os.path.join(os.getcwd(), "memory", "swarm_threads.sqlite"), check_same_thread=False)
    
    return workflow.compile(checkpointer=AsyncSqliteSaverBridge(conn), store=InMemoryStore())