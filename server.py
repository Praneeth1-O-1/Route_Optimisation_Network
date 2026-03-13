import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime

# Add models to path
sys.path.append('models/')
import environment
import agent
import dijkstra

app = Flask(__name__)
CORS(app)  # Enable CORS for generic frontend access from localhost

# --- Configuration ---
# You must set SUMO_HOME environment variable or configure it here
if 'SUMO_HOME' not in os.environ:
    # Try to find it or default to a common path (User might need to edit this)
    # Common paths for Mac/Linux: /usr/share/sumo, /opt/homebrew/share/sumo
    # Common paths for Windows: C:\Program Files (x86)\Eclipse\Sumo
    pass 

# Configuration constants matching main.py
NETWORKS = {
    "2x3 Network": {
        "file": './network_files/2x3_network.net.xml',
        "congestion": [("gneF_I", 10), ("gneI_F", 10), ("gneB_E", 20), ("gneE_B", 20), ("gneJ_M", 30), ("gneM_J", 30)],
        "traffic_light": [("B", 5), ("I", 5), ("G", 5)],
        "default_start": "F",
        "default_end": "M"
    },
    "Sunway Network": {
        "file": './network_files/sunway_network.net.xml',
        "congestion": [("gne2124969573_1000000001", 10), ("gne677583745_2302498575", 10)], # Simplified for demo, full list in main.py
        "traffic_light": [], # Simplified
        "default_start": "107",
        "default_end": "105"
    }
}

ALGORITHMS = ["Dijkstra", "Q-Learning", "SARSA"]

@app.route('/api/config', methods=['GET'])
def get_config():
    """Return available networks and algorithms"""
    return jsonify({
        "networks": list(NETWORKS.keys()),
        "algorithms": ALGORITHMS
    })

@app.route('/api/optimize', methods=['POST'])
def optimize():
    data = request.json
    network_name = data.get('network')
    algo_name = data.get('algorithm')
    start_node = data.get('start_node')
    end_node = data.get('end_node')

    if network_name not in NETWORKS:
        return jsonify({"error": "Invalid network selected"}), 400
    
    net_config = NETWORKS[network_name]
    
    # Initialize environment
    try:
        # Note: congestion and traffic_light logic is minimal here for the wrapper, 
        # ideally we should expose all options from main.py if needed.
        # For now, we use the values from the dictionary above.
        env = environment.traffic_env(
            net_config['file'], 
            congestion=net_config['congestion'], 
            traffic_light=net_config['traffic_light'], 
            evaluation="d" # Default to distance for now
        )
    except Exception as e:
        return jsonify({"error": f"Failed to initialize SUMO environment: {str(e)}"}), 500

    start_time = datetime.datetime.now()
    node_path = []
    edge_path = []
    
    try:
        if algo_name == "Dijkstra":
            d_agent = dijkstra.Dijkstra(env, start_node, end_node)
            node_path, edge_path = d_agent.search()
            
        elif algo_name == "Q-Learning":
            q_agent = agent.Q_Learning(env, start_node, end_node)
            # Reduced episodes for web responsiveness, normally 5000
            node_path, edge_path, episode, logs = q_agent.train(num_episodes=500, threshold=5)
            
        elif algo_name == "SARSA":
            # Reduced episodes for web responsiveness
            s_agent = agent.SARSA(env, start_node, end_node, exploration_rate=0.1)
            node_path, edge_path, episode, logs = s_agent.train(num_episodes=500, threshold=5)
            
        else:
            return jsonify({"error": "Invalid algorithm"}), 400
            
    except SystemExit as e:
        # The existing code uses sys.exit() for errors (like invalid node). 
        # We need to catch this or the server dies. 
        # Ideally, we refactor the models to raise Exceptions instead of sys.exit.
        # Since we can't easily refactor deep code right now, we might not catch it if it's a hard exit.
        return jsonify({"error": "Algorithm failed (likely invalid start/end node)"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Calculate cost (distance or time)
    # The environment defaults to 'distance' in our init above
    total_cost = env.get_edge_distance(edge_path)
    units = "meters"

    return jsonify({
        "path_nodes": node_path,
        "path_edges": edge_path,
        "cost": round(total_cost, 2),
        "units": units,
        "processing_time": duration
    })

if __name__ == '__main__':
    print("Starting Flask API Server for Traffic Optimization...")
    print("Ensure SUMO_HOME is set if SUMO is not in standard paths.")
    app.run(debug=True, port=5000)
