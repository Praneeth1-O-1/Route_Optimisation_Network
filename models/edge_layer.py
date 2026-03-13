import random
import time

# Edge nodes and their status
edge_nodes = {'A': True, 'B': True, 'C': True, 'D': True, 'E': True}

# Backup nodes for fault-tolerant task offloading
backup_nodes = {'B': 'B_backup', 'C': 'C_backup', 'D': 'D_backup'}

# Possible routes through the edge network
routes = {
    'Route1': ['A', 'B', 'E'],
    'Route2': ['A', 'C', 'E'],
    'Route3': ['A', 'D', 'E']
}

# Reward score for each route
route_rewards = {'Route1': 0.8, 'Route2': 0.6, 'Route3': 0.9}

# Tasks
tasks = [
    {'name': 'Obstacle Avoidance', 'deadline': 3, 'node': 'B'},
    {'name': 'Sensor Update', 'deadline': 5, 'node': 'C'},
    {'name': 'Route Recalculation', 'deadline': 2, 'node': 'D'},
    {'name': 'Traffic Sync', 'deadline': 4, 'node': 'B'}
]

# Simulate a random edge node failure
def simulate_failure():
    failed_node = random.choice(list(edge_nodes.keys()))
    edge_nodes[failed_node] = False
    print(f"\n⚠️ Edge node '{failed_node}' has failed.")
    return failed_node

# Check if a route is still usable
def is_route_valid(route):
    return all(edge_nodes.get(node, True) for node in routes[route])

# Select the best valid route based on reward
def select_best_route():
    valid_routes = [r for r in routes if is_route_valid(r)]
    if not valid_routes:
        return None
    best_route = max(valid_routes, key=lambda r: route_rewards[r])
    return best_route

# Offload tasks from failed node
def offload_tasks(failed_node):
    for task in tasks:
        if task['node'] == failed_node:
            backup = backup_nodes.get(failed_node)
            if backup:
                print(f"✅ Task '{task['name']}' offloaded to '{backup}'.")
            else:
                print(f"❌ Task '{task['name']}' failed — no backup available.")

# Run the edge layer and return delay + route
def run_edge_model():
    failed_node = simulate_failure()
    best_route = select_best_route()
    offload_tasks(failed_node)
    
    if not best_route:
        print("❌ No valid routes available — using delay penalty.")
        total_delay = random.uniform(2.0, 4.0)
        return total_delay, None

    # Simulate computation + offloading delay
    base_delay = random.uniform(0.5, 1.5)
    offload_penalty = random.uniform(0.3, 0.8)
    total_delay = base_delay + offload_penalty
    
    print(f"\n🚗 Best route: {best_route} (Reward: {route_rewards[best_route]})")
    print(f"⏱️ Total delay added: {total_delay:.2f}s\n")

    return total_delay, best_route
