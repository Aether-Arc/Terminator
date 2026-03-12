from langgraph.graph import END

class AgentRouter:
    @staticmethod
    def pop_queue(state):
        """Removes the finished agent from the waiting list."""
        pending = state.get("pending_agents", [])
        if pending:
            return {"pending_agents": pending[1:]} 
        return {}

    @staticmethod
    def dynamic_router(state):
        """Routes the graph to the next agent in line, or END if finished."""
        pending = state.get("pending_agents", [])
        if not pending:
            return END
        return pending[0]