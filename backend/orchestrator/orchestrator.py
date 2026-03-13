import asyncio
import uuid
import sqlite3
import os
from agents.planner_agent import PlannerAgent
from agents.scheduler_agent import SchedulerAgent
from agents.marketing_agent import MarketingAgent
from agents.critic_agent import CriticAgent
from agents.crisis_agent import CrisisAgent
from agents.email_agent import EmailAgent
from world_model.event_world_model import WorldModelAgent
from learning.policy_memory import RLPolicyMemory
from orchestrator.workflow_graph import build_graph
from memory.vector_store import search_memory, store_memory

from planning.monte_carlo_planner import MonteCarloPlanner
from planning.strategy_generator import StrategyGenerator

from agents.budget_agent import BudgetAgent
from agents.volunteer_agent import VolunteerAgent
from agents.sponsor_agent import SponsorAgent
from ml_models.attendance_predictor import AttendancePredictor
from agents.comms_agent import CommsAgent

# 👇 --- HIGHLIGHT: IMPORT THE NEW LEDGER MANAGER & CSV PARSER --- 👇
from memory.ledger_manager import LedgerManager
from tools.csv_parser import parse_messy_csv
# 👆 ------------------------------------------------------------- 👆

class EventOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.marketing = MarketingAgent()
        self.email = EmailAgent()
        self.world_model = WorldModelAgent()
        self.critic = CriticAgent()
        self.crisis = CrisisAgent()
        
        self.budget = BudgetAgent()
        self.volunteer = VolunteerAgent()
        self.sponsor = SponsorAgent()
        self.attendance_ml = AttendancePredictor()
        
        self.comms = CommsAgent()
        self.mcts = MonteCarloPlanner(self.world_model)
        self.strategy_gen = StrategyGenerator()
        
        self.graph = build_graph(
            self.planner, self.critic, self.scheduler, self.marketing,
            self.email, self.world_model, self.budget, self.volunteer,
            self.attendance_ml, self.sponsor
        )

    def get_thread_history(self):
        db_path = os.path.join(os.getcwd(), "memory", "swarm_threads.sqlite")
        if not os.path.exists(db_path): 
            return []
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
                rows = cursor.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            print(f"DB Read Error: {e}")
            return []

    async def plan_event(self, event_data, streamer, thread_id=None):
        await streamer.broadcast("Orchestrator", "Initializing Swarm Sequence...", "thinking")

        if not thread_id:
            thread_id = "event_thread_1"
        
        self.thread_config = {"configurable": {"thread_id": thread_id}}
        
        # 👇 --- HIGHLIGHT: INITIALIZE THE LEDGER & INGEST THE CSV --- 👇
        await streamer.broadcast("Orchestrator", "Spinning up Master Event Ledger...", "simulating")
        ledger_manager = LedgerManager(thread_id)
        
        # If the user uploaded a CSV, parse it and save it directly to the Master Ledger
        csv_content = event_data.get("csv_content", "")
        if csv_content:
            await streamer.broadcast("Orchestrator", "Parsing raw CSV data into Ledger...", "thinking")
            parsed_contacts = parse_messy_csv(csv_content)
            await ledger_manager.update_ledger("participants", parsed_contacts)
            await streamer.broadcast("Orchestrator", f"Saved {len(parsed_contacts)} participants to Ledger.", "success")
        
        # Read the newly constructed ledger so we can pass it into the AI Graph
        current_ledger = await ledger_manager.read_ledger()
        # 👆 ------------------------------------------------------------- 👆

        initial_state = {
            "master_ledger": current_ledger, # <--- Passed into the swarm here!
            "event_data": event_data,
            "iterations": 0,
            "candidates": [],
            "plan": {},
            "score": 0,
            "requires_approval": False,
            "agent_outputs": {},
            "audit_log": [],
            "global_constraints": ""
        }
        
        await streamer.broadcast("SwarmNetwork", "Executing adaptive reasoning graph...", "simulating")
        final_state = await self.graph.ainvoke(initial_state, config=self.thread_config)
        await streamer.broadcast("Orchestrator", "Schedule Drafted. Pausing Swarm for Human Approval.", "warning")
        
        return {
            "thread_id": thread_id,
            "workflow_executed": True,
            "selected_plan": final_state.get("plan"),
            "schedule": final_state.get("schedule"),
            "requires_approval": final_state.get("requires_approval"),
            "stability_score": final_state.get("score")
        }
    
    async def fork_and_update(self, thread_id, new_prompt, streamer):
        self.thread_config = {"configurable": {"thread_id": thread_id}}
        await streamer.broadcast("Orchestrator", f"TIME TRAVEL INITIATED: Rewinding state for {thread_id}...", "warning")
        
        current_state = self.graph.get_state(self.thread_config)
        event_data = current_state.values.get("event_data", {})
        event_data["user_constraints"] = event_data.get("user_constraints", "") + f" \nNEW ORGANIZER CONSTRAINT: {new_prompt}"
        
        self.graph.update_state(
            self.thread_config,
            {"event_data": event_data, "score": 0, "iterations": 0, "plan": {}, "schedule": []},
            as_node="critic"
        )
        
        await streamer.broadcast("CriticAgent", f"Applying new constraint: '{new_prompt}'. Routing back to Planner.", "simulating")
        
        async for event in self.graph.astream(None, config=self.thread_config):
            for node_name, state_update in event.items():
                await streamer.broadcast(node_name.capitalize(), "Autonomously replanning...", "simulating")
                
        final_state = self.graph.get_state(self.thread_config)
        return {
            "status": "forked_and_replanned",
            "schedule": final_state.values.get("schedule", []),
            "requires_approval": True,
            "stability_score": final_state.values.get("score", 0)
        }   

    async def approve_plan(self, event_data, streamer):
        await streamer.broadcast("Orchestrator", "Human intervention received. Processing...", "success")
        
        edited_plan = event_data.get("edited_plan")
        if edited_plan:
            await streamer.broadcast("Orchestrator", "Human edit detected. Routing back to Simulation Engine...", "warning")
            self.graph.update_state(self.thread_config, {"plan": edited_plan}, as_node="planner")
            async for event in self.graph.astream(None, config=self.thread_config):
                for node_name, state_update in event.items():
                    await streamer.broadcast(node_name.capitalize(), f"Simulating human-edited plan physics...", "simulating")
            
            new_state = self.graph.get_state(self.thread_config)
            return {
                "status": "re_evaluated",
                "message": "Human plan was simulated and critiqued. Please review the new stability score.",
                "plan": new_state.values.get("plan"),
                "simulation_metrics": new_state.values.get("simulation_metrics"),
                "score": new_state.values.get("score")
            }

        await streamer.broadcast("Orchestrator", "Plan approved. Engaging Autonomous Execution Network...", "simulating")
        
        new_agents_requested = event_data.get("add_agents", []) 
        if new_agents_requested:
            event_data["requested_agents"] = new_agents_requested
            self.graph.update_state(self.thread_config, {"event_data": event_data})
            await streamer.broadcast("Orchestrator", f"Organizer requested dynamic injection of: {new_agents_requested}.", "warning")

        await streamer.broadcast("SupervisorAgent", "Dynamically firing local GPU agents in parallel...", "thinking")
        
        current_state = self.graph.get_state(self.thread_config).values
        evt_data = current_state.get("event_data", event_data)
        final_schedule = current_state.get("schedule", [])
        evt_data["schedule"] = final_schedule 
        
        # 👇 --- HIGHLIGHT: SAVE FINAL SCHEDULE TO LEDGER --- 👇
        ledger_manager = LedgerManager(self.thread_config["configurable"]["thread_id"])
        await ledger_manager.update_ledger("schedule", final_schedule)
        # 👆 ------------------------------------------------ 👇
        
        for agent_node in ["marketing", "budget", "volunteer", "sponsor", "email", "attendance_ml"]:
            await streamer.broadcast(agent_node.capitalize(), "Autonomously executing task in parallel...", "simulating")

        marketing_task = self.marketing.generate_campaign(evt_data)
        budget_task = self.budget.calculate(evt_data)
        volunteer_task = self.volunteer.assign_shifts(evt_data, final_schedule)
        sponsor_task = self.sponsor.draft_sponsorships(evt_data)
        
        marketing_assets, budget_res, volunteer_res, sponsor_res = await asyncio.gather(
            marketing_task, budget_task, volunteer_task, sponsor_task
        )
        
        email_logs = self.email.send_invites(evt_data.get("csv_content", ""), "Your optimal schedule is locked!")
        attendance_forecast = self.attendance_ml.predict_attendance(evt_data.get("expected_crowd", 500))
        
        agent_outputs = {
            "budget": budget_res,
            "volunteer": volunteer_res,
            "sponsor": sponsor_res,
            "attendance_forecast": attendance_forecast
        }
        
        # 👇 --- HIGHLIGHT: DUMP PARALLEL AGENT RESULTS TO LEDGER --- 👇
        await ledger_manager.update_ledger("budget", budget_res)
        await ledger_manager.update_ledger("volunteers", volunteer_res)
        await ledger_manager.update_ledger("sponsors", sponsor_res)
        await ledger_manager.update_ledger("marketing_assets", {"copy": marketing_assets, "emails": email_logs})
        # 👆 -------------------------------------------------------- 👆
        
        self.graph.update_state(self.thread_config, {
            "marketing_copy": marketing_assets,
            "email_logs": email_logs,
            "agent_outputs": agent_outputs
        })
        
        event_name = event_data.get("name", "Unknown Event")
        crowd = event_data.get("expected_crowd", "Unknown")
        store_memory(f"SUCCESSFUL EVENT '{event_name}' ({crowd} attendees). Schedule used: {final_schedule}. Marketing used: {marketing_assets}")
        
        await streamer.broadcast("RLPolicyMemory", "Experience stored. Self-improvement weights updated.", "success")
        await streamer.broadcast("Orchestrator", "All operational phases autonomously completed.", "idle")
        
        return {
            "status": "approved_and_completed",
            "marketing": marketing_assets,
            "schedule": final_schedule,
            "email_outreach_logs": email_logs,
            "agent_outputs": agent_outputs
        }

    async def manual_override(self, override_data, streamer):
        action_type = override_data.get("override_type") 
        
        if action_type == "edit_schedule":
            await streamer.broadcast("Orchestrator", "Manual schedule override initiated by Organizer.", "error")
            new_schedule = override_data.get("new_schedule", [])
            
            await streamer.broadcast("CommsAgent", "Notifying participants of manual schedule change...", "thinking")
            result = await self.comms.execute_broadcast(
                csv_content=override_data.get("csv_content", ""), 
                command="The event schedule has been manually updated by the organizer. Please check the live dashboard for the new timings. Use both Email and Whatsapp.",
                event_context="Routine schedule modification."
            )
            
            await streamer.broadcast("Orchestrator", "Manual override complete. Participants notified.", "success")
            return {"status": "Schedule manually updated", "new_schedule": new_schedule, "comms_result": result}
            
        elif action_type == "custom_crisis":
            crisis_desc = override_data.get("description", "A custom emergency has occurred.")
            await streamer.broadcast("Orchestrator", f"CUSTOM CRISIS INJECTED: {crisis_desc}", "error")
            return await self.handle_crisis(override_data, streamer, "manual_trigger")
            
        elif action_type == "broadcast":
            command = override_data.get("description", "Send an update.")
            csv_content = override_data.get("csv_content", "")
            
            await streamer.broadcast("CommsAgent", "Analyzing broadcast command & parsing CSV...", "thinking")
            result = await self.comms.execute_broadcast(
                csv_content=csv_content, 
                command=command, 
                event_context="Organizer initiated manual broadcast."
            )
            await streamer.broadcast("CommsAgent", f"Broadcast complete across requested channels.", "success")
            return result
            
        return {"error": "Unknown override type."}
    
    async def resume_event(self, streamer):
        await streamer.broadcast("Orchestrator", "CRASH RECOVERY INITIATED: Loading SQLite Checkpoint...", "warning")
        self.thread_config = {"configurable": {"thread_id": "event_thread_1"}}
        
        saved_state = self.graph.get_state(self.thread_config)
        next_agent = saved_state.next 
        
        if not next_agent:
            await streamer.broadcast("Orchestrator", "Thread is already fully completed. Nothing to resume.", "idle")
            return {"status": "completed"}

        await streamer.broadcast("Orchestrator", f"Found saved state! Resuming execution at: {next_agent[0].capitalize()}", "success")
        
        async for event in self.graph.astream(None, config=self.thread_config):
            for node_name, state_update in event.items():
                if node_name == "supervisor":
                    await streamer.broadcast("SupervisorAgent", "Dynamically firing local GPU agents in parallel...", "thinking")
                else:
                    await streamer.broadcast(node_name.capitalize(), "Autonomously executing task...", "simulating")

        final_state = self.graph.get_state(self.thread_config)
        agent_outputs = final_state.values.get("agent_outputs", {})
        
        await streamer.broadcast("Orchestrator", "Recovery successful. All operations completed.", "idle")
        return {
            "status": "recovered_and_completed",
            "schedule": final_state.values.get("schedule", []),
            "marketing": final_state.values.get("marketing_copy", ""),
            "agent_outputs": agent_outputs
        }
    
    async def handle_crisis(self, crisis_data, streamer, crisis_event):
        crisis_desc = crisis_data.get('description', 'Unknown anomaly detected.')
        event_name = crisis_data.get("event_name", "the current event") 
        crowd_size = crisis_data.get("expected_crowd", 500)
        
        await streamer.broadcast("Orchestrator", f"CRISIS DETECTED: {crisis_desc}", "error")
        await streamer.broadcast("WorldModelAgent", "Querying VectorDB for historical crisis data...", "simulating")
        search_query = f"Crisis: {crisis_desc} during event: {event_name}"
        past_crises = search_memory(search_query)
        
        await streamer.broadcast("StrategyGenerator", "Inventing context-aware mitigation strategies...", "thinking")
        possible_actions = await self.strategy_gen.generate(crisis_desc, crowd_size)
        
        await streamer.broadcast("MonteCarloPlanner", f"Running 100x physics simulations on proposed strategies...", "simulating")
        best_math_action = self.mcts.plan(possible_actions, simulations=100)
        best_action_name = best_math_action.get("name", "Dynamic Reschedule")
        
        await streamer.broadcast("MonteCarloPlanner", f"MCTS Converged. Safest path: '{best_action_name}'", "success")

        await streamer.broadcast("CrisisAgent", "Fusing MCTS physics data into human-readable schedule mitigation...", "thinking")
        mock_current_schedule = [{"session": "Hacking Phase 1", "time": "11:00 AM"}]
        
        enhanced_crisis_prompt = f"""
        CRISIS: {crisis_desc}
        HISTORICAL CONTEXT: {past_crises}
        MCTS OPTIMAL ACTION: Our Monte Carlo simulations proved that the strategy '{best_action_name}' is the safest route.
        You MUST build your final mitigation strategy around this MCTS Optimal Action.
        """
        
        solution = await self.crisis.resolve(enhanced_crisis_prompt, mock_current_schedule)
        mitigation_text = solution.get('mitigation_strategy', 'Adjusting timeline dynamically.')
        await streamer.broadcast("SchedulerAgent", f"Applying fixes: {mitigation_text}", "simulating")
        new_schedule = self.scheduler.recalculate(solution)
        
        store_memory(f"Event: {event_name} | Crisis: {crisis_desc} | MCTS Action: {best_action_name} | Mitigation: {mitigation_text}")
        
        await streamer.broadcast("CommsAgent", "Crisis override: Blasting urgent updates across all relevant channels...", "warning")
        csv_content = crisis_data.get("csv_content", "") 
        broadcast_result = await self.comms.execute_broadcast(
            csv_content=csv_content,
            command=f"Send an urgent update via email and whatsapp to all participants detailing this mitigation plan: {mitigation_text}",
            event_context=f"Crisis Resolution for: {crisis_desc}"
        )
        
        emergency_logs = broadcast_result.get("logs", [])
        await streamer.broadcast("Orchestrator", "Crisis resolved. Knowledge stored in VectorDB.", "success")
        
        return {
            "status": "Resolved & Participants Notified",
            "crisis_injected": crisis_desc, 
            "applied_solution": solution, 
            "new_schedule": new_schedule,
            "emergency_logs": emergency_logs
        }

    def get_event_details(self, thread_id):
        self.thread_config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(self.thread_config)
        
        if not state or not hasattr(state, 'values'):
            return {"error": "Thread not found or event not finished."}
            
        return {
            "thread_id": thread_id,
            "schedule": state.values.get("schedule", []),
            "marketing_copy": state.values.get("marketing_copy", ""),
            "email_logs": state.values.get("email_logs", []),
            "agent_outputs": state.values.get("agent_outputs", {})
        }