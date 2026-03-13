# models/edge_server.py
from models import edge_layer  # import your logic layer

class EdgeServer:
    def __init__(self, node_id):
        self.node_id = node_id

    def handle_vehicle_data(self, vehicle_id, data):
        print(f"[Edge-{self.node_id}] Received data from {vehicle_id}")
        
        # Call the edge layer logic here
        delay, route = edge_layer.run_edge_model()
        
        print(f"[Edge-{self.node_id}] Best route: {route}, Delay: {delay:.2f}s")
        return delay, route
