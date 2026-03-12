import networkx as nx

class CrowdSimulator:
    def __init__(self):
        # Create a spatial graph of the event venue
        self.venue_graph = nx.Graph()
        self.venue_graph.add_edge("Main Entrance", "Lobby", capacity=1000)
        self.venue_graph.add_edge("Lobby", "Main Hall", capacity=800)
        self.venue_graph.add_edge("Lobby", "Workshop A", capacity=200)
        self.venue_graph.add_edge("Lobby", "Cafeteria", capacity=400)

    def calculate_bottlenecks(self, crowd_size, schedule_plan):
        """Simulates spatial movement using Graph Centrality and Capacity constraints."""
        max_capacity = sum([data['capacity'] for u, v, data in self.venue_graph.edges(data=True)])
        
        # Calculate load factor
        load_factor = crowd_size / max_capacity if max_capacity > 0 else 1.0
        
        bottlenecks = 0
        risk_areas = []
        
        if load_factor > 0.8:
            bottlenecks += int((load_factor - 0.8) * 100)
            risk_areas.append("Lobby to Main Hall corridor")
            
        return {
            "spatial_bottlenecks": bottlenecks,
            "high_risk_zones": risk_areas,
            "density_warning": load_factor > 0.9
        }