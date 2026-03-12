import asyncio
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

# 🧠 DEEPMIND IMPORTS (Planning & Simulation)
from planning.monte_carlo_planner import MonteCarloPlanner
from planning.strategy_generator import StrategyGenerator

# 🌟 NEW MODULAR AGENT IMPORTS
from agents.budget_agent import BudgetAgent
from agents.volunteer_agent import VolunteerAgent
from agents.sponsor_agent import SponsorAgent
from ml_models.attendance_predictor import AttendancePredictor

class EventOrchestrator:
    def __init__(self):
        # 1. Initialize Core Agents
        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.marketing = MarketingAgent()
        self.email = EmailAgent()
        self.world_model = WorldModelAgent()
        self.critic = CriticAgent()
        self.crisis = CrisisAgent()
        
        # 2. Initialize Advanced/Optional Agents & ML Models
        self.budget = BudgetAgent()
        self.volunteer = VolunteerAgent()
        self.sponsor = SponsorAgent()
        self.attendance_ml = AttendancePredictor()
        
        self.mcts = MonteCarloPlanner(self.world_model)
        self.strategy_gen = StrategyGenerator()
        
        # 3. Pass ALL agents into the dynamic autonomous graph
        self.graph = build_graph(
            self.planner,
            self.critic,
            self.scheduler,
            self.marketing,
            self.email, 
            self.world_model,
            self.budget,
            self.volunteer,
            self.attendance_ml,
            self.sponsor
        )

    async def plan_event(self, event_data, streamer):
        await streamer.broadcast("Orchestrator", "Initializing Swarm Sequence...", "thinking")
        
        # Thread ID tells LangGraph exactly where to store this event's memory
        self.thread_config = {"configurable": {"thread_id": "event_thread_1"}}
        
        initial_state = {
            "event_data": event_data,
            "iterations": 0,
            "candidates": [],
            "plan": {},
            "score": 0,
            "requires_approval": False,
            "agent_outputs": {}
        }
        
        await streamer.broadcast("SwarmNetwork", "Executing adaptive reasoning graph...", "simulating")
        
        # Run graph until it hits the interrupt_before=["supervisor"] breakpoint
        final_state = await self.graph.ainvoke(initial_state, config=self.thread_config)
        
        await streamer.broadcast("Orchestrator", "Schedule Drafted. Pausing Swarm for Human Approval.", "warning")
        
        return {
            "workflow_executed": True,
            "selected_plan": final_state.values.get("plan"),
            "schedule": final_state.values.get("schedule"),
            "requires_approval": final_state.values.get("requires_approval"),
            "stability_score": final_state.values.get("score")
        }

    async def approve_plan(self, event_data, streamer):
        await streamer.broadcast("Orchestrator", "Human intervention received. Processing...", "success")
        
        # 1. TIME TRAVEL / STATE FORCING (If the human edited the plan)
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
        
        # --- NEW: DYNAMIC AGENT INJECTION ---
        new_agents_requested = event_data.get("add_agents", []) 
        if new_agents_requested:
            # Add this to the event_data state so the Supervisor sees it when it wakes up
            event_data["requested_agents"] = new_agents_requested
            self.graph.update_state(self.thread_config, {"event_data": event_data})
            await streamer.broadcast("Orchestrator", f"Organizer requested dynamic injection of: {new_agents_requested}.", "warning")

        # 2. TRUE PARALLEL ASYNC EXECUTION (Hybrid Swarm Speedup)
        # We bypass the sequential LangGraph router here and fire all local agents simultaneously
        await streamer.broadcast("SupervisorAgent", "Dynamically firing local GPU agents in parallel...", "thinking")
        
        # Fetch current state
        current_state = self.graph.get_state(self.thread_config).values
        evt_data = current_state.get("event_data", event_data)
        final_schedule = current_state.get("schedule", [])
        evt_data["schedule"] = final_schedule # Marketing needs this injected
        
        # Broadcast active execution UI
        for agent_node in ["marketing", "budget", "volunteer", "sponsor", "email", "attendance_ml"]:
            await streamer.broadcast(agent_node.capitalize(), "Autonomously executing task in parallel...", "simulating")

        # Fire all local GPU tasks at the exact same time
        marketing_task = self.marketing.generate_campaign(evt_data)
        budget_task = self.budget.calculate(evt_data)
        volunteer_task = self.volunteer.assign_shifts(evt_data, final_schedule)
        sponsor_task = self.sponsor.draft_sponsorships(evt_data)
        
        # Gather async results simultaneously
        marketing_assets, budget_res, volunteer_res, sponsor_res = await asyncio.gather(
            marketing_task, budget_task, volunteer_task, sponsor_task
        )
        
        # Run synchronous models (Email & ML predictors)
        email_logs = self.email.send_invites(evt_data.get("csv_content", ""), "Your optimal schedule is locked!")
        attendance_forecast = self.attendance_ml.predict_attendance(evt_data.get("expected_crowd", 500))
        
        agent_outputs = {
            "budget": budget_res,
            "volunteer": volunteer_res,
            "sponsor": sponsor_res,
            "attendance_forecast": attendance_forecast
        }
        
        # Save final execution state back to graph memory
        self.graph.update_state(self.thread_config, {
            "marketing_copy": marketing_assets,
            "email_logs": email_logs,
            "agent_outputs": agent_outputs
        })
        
        # 3. SELF-IMPROVEMENT LOOP
        event_name = event_data.get("name", "Unknown Event")
        crowd = event_data.get("expected_crowd", "Unknown")
        memory_string = f"SUCCESSFUL EVENT '{event_name}' ({crowd} attendees). Schedule used: {final_schedule}. Marketing used: {marketing_assets}"
        store_memory(memory_string)
        
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
        """Allows the user to forcefully edit the locked schedule or inject a custom crisis."""
        action_type = override_data.get("override_type") 
        
        if action_type == "edit_schedule":
            await streamer.broadcast("Orchestrator", "Manual schedule override initiated by Organizer.", "error")
            new_schedule = override_data.get("new_schedule", [])
            
            # Wake up the EmailAgent to blast the manual update
            await streamer.broadcast("EmailAgent", "Notifying participants of manual schedule change...", "thinking")
            logs = self.email.send_invites(
                csv_content=override_data.get("csv_content", ""), 
                base_draft="URGENT: The event schedule has been manually updated by the organizer. Please check the live dashboard for the new timings."
            )
            
            await streamer.broadcast("Orchestrator", "Manual override complete. Participants notified.", "success")
            return {"status": "Schedule manually updated", "new_schedule": new_schedule, "emails_sent": len(logs)}
            
        elif action_type == "custom_crisis":
            # Route custom user text directly into our Monte Carlo crisis engine
            crisis_desc = override_data.get("description", "A custom emergency has occurred.")
            await streamer.broadcast("Orchestrator", f"CUSTOM CRISIS INJECTED: {crisis_desc}", "error")
            
            # We reuse our existing robust handle_crisis pipeline
            return await self.handle_crisis(override_data, streamer, "manual_trigger")
            
        return {"error": "Unknown override type."}

    async def handle_crisis(self, crisis_data, streamer, crisis_event):
        crisis_desc = crisis_data.get('description', 'Unknown anomaly detected.')
        event_name = crisis_data.get("event_name", "the current event") 
        crowd_size = crisis_data.get("expected_crowd", 500)
        
        await streamer.broadcast("Orchestrator", f"CRISIS DETECTED: {crisis_desc}", "error")
        
        # 1. VECTOR DB SEARCH
        await streamer.broadcast("WorldModelAgent", "Querying VectorDB for historical crisis data...", "simulating")
        search_query = f"Crisis: {crisis_desc} during event: {event_name}"
        past_crises = search_memory(search_query)
        
        # 2. STRATEGY GENERATION (AI dynamically invents options)
        await streamer.broadcast("StrategyGenerator", "Inventing context-aware mitigation strategies...", "thinking")
        possible_actions = await self.strategy_gen.generate(crisis_desc, crowd_size)
        
        # 3. MONTE CARLO TREE SEARCH (Simulating the AI's ideas)
        await streamer.broadcast("MonteCarloPlanner", f"Running 100x physics simulations on proposed strategies...", "simulating")
        base_state = {"delay": 0, "crowd_size": crowd_size}
        
        # MCTS finds which of the LLM's ideas was mathematically the safest
        best_math_action = self.mcts.plan(possible_actions, simulations=100)
        best_action_name = best_math_action.get("name", "Dynamic Reschedule")
        
        await streamer.broadcast("MonteCarloPlanner", f"MCTS Converged. Safest path: '{best_action_name}'", "success")

        # 4. LLM CRISIS RESOLUTION
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
        
        # 5. COMMIT TO MEMORY & ALERT
        store_memory(f"Event: {event_name} | Crisis: {crisis_desc} | MCTS Action: {best_action_name} | Mitigation: {mitigation_text}")
        
        await streamer.broadcast("EmailAgent", "Crisis override: Blasting urgent updates to participants...", "warning")

        csv_content = crisis_data.get("csv_content", "") 
        emergency_logs = self.email.send_invites(csv_content, f"URGENT EVENT UPDATE: {mitigation_text}")
        
        await streamer.broadcast("Orchestrator", "Crisis resolved. Knowledge stored in VectorDB.", "success")
        
        return {
            "status": "Resolved & Participants Notified",
            "crisis_injected": crisis_desc, 
            "applied_solution": solution, 
            "new_schedule": new_schedule,
            "emergency_emails_sent": emergency_logs
        }