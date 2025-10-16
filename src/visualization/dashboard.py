"""
Web Dashboard for Real-time Digital Twin Monitoring
Flask-based dashboard with real-time updates using WebSocket.
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import json
import yaml
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_twin.core import DigitalTwin
from simulation.engine import SimulationEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'siemens_digital_twin_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global simulation state
simulation_running = False
digital_twin = None
simulation_thread = None


def load_config():
    """Load configuration file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               'config', 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Get current simulation status"""
    if digital_twin is None:
        return jsonify({'running': False, 'telemetry': None})
    
    telemetry = digital_twin.get_telemetry()
    return jsonify({
        'running': simulation_running,
        'telemetry': telemetry
    })


@app.route('/api/config')
def get_config():
    """Get vehicle configuration"""
    config = load_config()
    return jsonify(config)


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'message': 'Connected to Digital Twin'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('start_simulation')
def handle_start_simulation(data):
    """Start simulation"""
    global simulation_running, digital_twin, simulation_thread
    
    if simulation_running:
        emit('error', {'message': 'Simulation already running'})
        return
    
    scenario = data.get('scenario', 'urban')
    print(f"Starting simulation with scenario: {scenario}")
    
    # Initialize digital twin
    config = load_config()
    digital_twin = DigitalTwin(config)
    
    # Start simulation in background thread
    simulation_running = True
    simulation_thread = threading.Thread(
        target=run_simulation_loop,
        args=(scenario,)
    )
    simulation_thread.daemon = True
    simulation_thread.start()
    
    emit('simulation_started', {'scenario': scenario})


@socketio.on('stop_simulation')
def handle_stop_simulation():
    """Stop simulation"""
    global simulation_running
    
    simulation_running = False
    print("Stopping simulation")
    emit('simulation_stopped', {})


@socketio.on('set_throttle')
def handle_set_throttle(data):
    """Manually set throttle"""
    if digital_twin and simulation_running:
        throttle = float(data.get('throttle', 0))
        print(f"Throttle set to: {throttle}%")


def run_simulation_loop(scenario: str):
    """Run simulation loop and broadcast updates"""
    global simulation_running, digital_twin
    
    engine = SimulationEngine(digital_twin, time_step=0.1)
    scenario_obj = engine.scenarios.get(scenario)
    
    if not scenario_obj:
        print(f"Unknown scenario: {scenario}")
        simulation_running = False
        return
    
    step = 0
    max_steps = int(scenario_obj.duration_s / 0.1)
    
    while simulation_running and step < max_steps:
        current_time = step * 0.1
        throttle, brake = scenario_obj.get_control_inputs(current_time)
        
        # Execute simulation step
        digital_twin.step(throttle, brake, 0.1)
        
        # Broadcast telemetry every 10 steps (1 second)
        if step % 10 == 0:
            telemetry = digital_twin.get_telemetry()
            socketio.emit('telemetry_update', telemetry)
            digital_twin.log_telemetry()
        
        step += 1
        time.sleep(0.1)  # Real-time simulation
    
    simulation_running = False
    
    # Export final telemetry
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        'data', f'telemetry_{scenario}.json'
    )
    digital_twin.export_telemetry(output_path)
    
    socketio.emit('simulation_complete', {
        'telemetry_file': output_path,
        'total_steps': step
    })
    
    print(f"Simulation complete. Data saved to: {output_path}")


def create_dashboard_html():
    """Create HTML dashboard template"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Siemens EV Digital Twin Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.18.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .controls {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .btn {
            padding: 12px 24px;
            margin: 5px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn-start { background: #4CAF50; color: white; }
        .btn-stop { background: #f44336; color: white; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,255,255,0.2);
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #4CAF50;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.9em;
            color: rgba(255,255,255,0.7);
            text-transform: uppercase;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-running { background: #4CAF50; }
        .status-stopped { background: #f44336; }
        .charts {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
        }
        .chart-container {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        select {
            padding: 10px;
            border-radius: 5px;
            border: none;
            font-size: 16px;
            margin: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Siemens EV Digital Twin Dashboard</h1>
            <p>Real-time monitoring and simulation control</p>
            <p><span id="status-indicator" class="status-indicator status-stopped"></span> 
               <span id="status-text">Stopped</span></p>
        </div>
        
        <div class="controls">
            <h3>Simulation Controls</h3>
            <select id="scenario-select">
                <option value="urban">Urban Driving</option>
                <option value="highway">Highway Driving</option>
                <option value="aggressive">Aggressive Driving</option>
                <option value="eco">Eco Mode</option>
            </select>
            <button class="btn btn-start" onclick="startSimulation()">Start Simulation</button>
            <button class="btn btn-stop" onclick="stopSimulation()">Stop Simulation</button>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Speed</div>
                <div class="metric-value" id="speed">0</div>
                <div class="metric-label">km/h</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Battery SOC</div>
                <div class="metric-value" id="battery-soc">0</div>
                <div class="metric-label">%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Motor Power</div>
                <div class="metric-value" id="motor-power">0</div>
                <div class="metric-label">kW</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Motor Temperature</div>
                <div class="metric-value" id="motor-temp">0</div>
                <div class="metric-label">°C</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Distance</div>
                <div class="metric-value" id="distance">0</div>
                <div class="metric-label">km</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Motor Health</div>
                <div class="metric-value" id="motor-health">100</div>
                <div class="metric-label">%</div>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart-container">
                <div id="speed-chart"></div>
            </div>
            <div class="chart-container">
                <div id="battery-chart"></div>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        
        let speedData = {x: [], y: []};
        let batteryData = {x: [], y: []};
        
        socket.on('connect', () => {
            console.log('Connected to server');
        });
        
        socket.on('telemetry_update', (data) => {
            updateMetrics(data);
            updateCharts(data);
        });
        
        socket.on('simulation_started', (data) => {
            document.getElementById('status-indicator').className = 'status-indicator status-running';
            document.getElementById('status-text').textContent = 'Running: ' + data.scenario;
        });
        
        socket.on('simulation_stopped', () => {
            document.getElementById('status-indicator').className = 'status-indicator status-stopped';
            document.getElementById('status-text').textContent = 'Stopped';
        });
        
        socket.on('simulation_complete', (data) => {
            document.getElementById('status-indicator').className = 'status-indicator status-stopped';
            document.getElementById('status-text').textContent = 'Complete';
            alert('Simulation complete! Data saved to: ' + data.telemetry_file);
        });
        
        function updateMetrics(data) {
            document.getElementById('speed').textContent = data.vehicle.speed_kmh.toFixed(1);
            document.getElementById('battery-soc').textContent = data.battery.soc_percent.toFixed(1);
            document.getElementById('motor-power').textContent = data.motor.power_kw.toFixed(1);
            document.getElementById('motor-temp').textContent = data.motor.temperature_c.toFixed(1);
            document.getElementById('distance').textContent = data.vehicle.position_km.toFixed(2);
            document.getElementById('motor-health').textContent = data.motor.health_score.toFixed(1);
        }
        
        function updateCharts(data) {
            speedData.x.push(data.simulation_time);
            speedData.y.push(data.vehicle.speed_kmh);
            
            batteryData.x.push(data.simulation_time);
            batteryData.y.push(data.battery.soc_percent);
            
            // Keep only last 100 points
            if (speedData.x.length > 100) {
                speedData.x.shift();
                speedData.y.shift();
                batteryData.x.shift();
                batteryData.y.shift();
            }
            
            Plotly.newPlot('speed-chart', [{
                x: speedData.x,
                y: speedData.y,
                type: 'scatter',
                mode: 'lines',
                line: {color: '#4CAF50', width: 2}
            }], {
                title: 'Speed Over Time',
                xaxis: {title: 'Time (s)'},
                yaxis: {title: 'Speed (km/h)'},
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(255,255,255,0.1)',
                font: {color: '#fff'}
            });
            
            Plotly.newPlot('battery-chart', [{
                x: batteryData.x,
                y: batteryData.y,
                type: 'scatter',
                mode: 'lines',
                line: {color: '#FFC107', width: 2}
            }], {
                title: 'Battery State of Charge',
                xaxis: {title: 'Time (s)'},
                yaxis: {title: 'SOC (%)'},
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(255,255,255,0.1)',
                font: {color: '#fff'}
            });
        }
        
        function startSimulation() {
            const scenario = document.getElementById('scenario-select').value;
            socket.emit('start_simulation', {scenario: scenario});
        }
        
        function stopSimulation() {
            socket.emit('stop_simulation');
        }
    </script>
</body>
</html>"""
    
    # Create templates directory
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    with open(os.path.join(templates_dir, 'dashboard.html'), 'w') as f:
        f.write(html_content)


def main():
    """Start the web dashboard"""
    print("="*60)
    print("Siemens Automobile Digital Twin Dashboard")
    print("="*60)
    
    # Create HTML template
    create_dashboard_html()
    
    print("\nStarting web server...")
    print("Dashboard URL: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
