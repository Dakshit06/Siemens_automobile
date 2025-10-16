"""
3D Viewer Web Server
Streams digital twin telemetry data to a Three.js web interface.
"""
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import time
import yaml
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from digital_twin.core import DigitalTwin
from simulation.engine import SimulationEngine

# --- FLASK APP SETUP ---
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'siemens_3d_viewer_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- GLOBAL STATE ---
digital_twin = None
simulation_thread = None
simulation_running = False

def load_config():
    """Load configuration file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# --- SIMULATION LOOP ---
def simulation_loop():
    """Runs the simulation and broadcasts data."""
    global digital_twin, simulation_running
    
    print("▶️ Starting background simulation for 3D viewer...")
    config = load_config()
    digital_twin = DigitalTwin(config)
    engine = SimulationEngine(digital_twin, time_step=0.1)
    scenario = engine.scenarios['urban'] # Default to urban for continuous demo
    
    step = 0
    simulation_running = True

    while simulation_running:
        current_time = (step * 0.1) % scenario.duration_s
        throttle, brake = scenario.get_control_inputs(current_time)
        
        digital_twin.step(throttle, brake, time_step_s=0.1)
        
        # Broadcast telemetry at 10 Hz
        telemetry = digital_twin.get_telemetry()
        socketio.emit('telemetry_update', telemetry)
        
        step += 1
        time.sleep(0.1) # Simulate real-time

    print("⏹️ Background simulation stopped.")

# --- FLASK ROUTES & SOCKET.IO EVENTS ---
@app.route('/')
def index():
    """Serve the 3D viewer HTML page."""
    return render_template('viewer_3d.html')

@socketio.on('connect')
def handle_connect():
    """Handle new client connection."""
    global simulation_thread
    print(f"✅ Client connected. Starting simulation stream...")
    if simulation_thread is None or not simulation_thread.is_alive():
        simulation_thread = threading.Thread(target=simulation_loop)
        simulation_thread.daemon = True
        simulation_thread.start()

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print("❌ Client disconnected.")
    # Optionally stop the simulation if no clients are connected
    # global simulation_running
    # simulation_running = False

def main():
    """Start the 3D Viewer web server."""
    print("============================================================")
    print("🚗 Siemens Automobile - 3D Digital Twin Viewer")
    print("============================================================")
    print("\n🚀 Starting 3D viewer web server...")
    print("   🔗 URL: http://localhost:5001")
    print("\nPress Ctrl+C to stop the server")
    print("============================================================")
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()
