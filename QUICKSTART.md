# Siemens Automobile Digital Twin - Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation:**
   ```bash
   python --version  # Should be Python 3.10+
   ```

## Usage

### 1. Run a Simulation

Run different driving scenarios:

```bash
# Urban driving (stop-and-go traffic)
python src/main.py simulate --scenario urban

# Highway driving (constant speed)
python src/main.py simulate --scenario highway

# Aggressive driving (hard acceleration/braking)
python src/main.py simulate --scenario aggressive

# Eco mode (efficient driving)
python src/main.py simulate --scenario eco
```

### 2. Generate Analysis Report

After running a simulation, generate comprehensive reports:

```bash
python src/main.py report
```

This creates:
- `reports/analysis_report.txt` - Detailed text report
- `reports/telemetry_analysis.png` - Performance charts
- `reports/health_dashboard.png` - Component health metrics

### 3. View 3D Visualization

Render an interactive 3D model of the vehicle:

```bash
python src/main.py visualize
```

This will:
- Open an interactive 3D window
- Save screenshot to `reports/vehicle_3d_model.png`
- Color-code components by temperature and status

### 4. Start Web Dashboard

Launch the real-time monitoring dashboard:

```bash
python src/main.py dashboard
```

Then open your browser to: `http://localhost:5000`

Features:
- Real-time telemetry visualization
- Interactive scenario selection
- Live charts and metrics
- Start/stop simulation controls

### 5. Complete Workflow

Run simulation and generate all reports at once:

```bash
python src/main.py all --scenario urban
```

## Project Structure

```
Siemens_automobile/
├── src/
│   ├── digital_twin/        # Core digital twin models
│   │   └── core.py          # Vehicle components and sensors
│   ├── simulation/          # Simulation engine
│   │   └── engine.py        # Driving scenarios
│   ├── visualization/       # 3D rendering and dashboard
│   │   ├── render_3d.py     # PyVista 3D visualization
│   │   └── dashboard.py     # Flask web dashboard
│   ├── analysis/            # Analytics and reporting
│   │   └── generate_report.py
│   └── main.py              # Main entry point
├── config/
│   └── config.yaml          # Configuration parameters
├── data/                    # Telemetry data (generated)
├── reports/                 # Generated reports (generated)
└── requirements.txt         # Python dependencies
```

## Key Components

### Digital Twin Components
- **Electric Motor**: 150 kW motor with thermal management
- **Battery Pack**: 75 kWh lithium-ion with cell monitoring
- **Vehicle Dynamics**: Physics-based motion simulation
- **Sensor Network**: 24+ sensors for comprehensive monitoring

### Driving Scenarios
1. **Urban**: Stop-and-go traffic, 10 minutes
2. **Highway**: High-speed cruise, 30 minutes
3. **Aggressive**: Hard acceleration/braking, 5 minutes
4. **Eco**: Efficient driving patterns, 15 minutes

### Analytics Features
- Performance metrics calculation
- Anomaly detection
- Predictive maintenance
- Energy efficiency analysis
- Component health monitoring

## Configuration

Edit `config/config.yaml` to customize:
- Vehicle parameters (weight, max speed)
- Powertrain specifications
- Battery capacity and voltage
- Sensor configuration
- Simulation settings

## Outputs

### Telemetry Data
- JSON files in `data/` directory
- Timestamped sensor readings
- Complete vehicle state history

### Reports
- Text reports with metrics and recommendations
- Performance visualization charts
- Health monitoring dashboards
- 3D model screenshots

## Troubleshooting

**ImportError for pyvista/vtk:**
```bash
pip install pyvista vtk
```

**No display for 3D visualization:**
Set environment variable: `export DISPLAY=:0`

**Port 5000 already in use:**
Edit `dashboard.py` and change the port number

## Example Workflow

```bash
# 1. Run simulation
python src/main.py simulate --scenario highway

# 2. Generate reports
python src/main.py report

# 3. View 3D model
python src/main.py visualize

# 4. Check reports
ls -lh reports/

# Output:
# - analysis_report.txt
# - telemetry_analysis.png
# - health_dashboard.png
# - vehicle_3d_model.png
```

## Advanced Usage

### Custom Scenario
Modify `src/simulation/engine.py` to add custom scenarios:

```python
class CustomScenario(DrivingScenario):
    def __init__(self):
        super().__init__("Custom", 600)
    
    def get_control_inputs(self, time: float):
        # Your custom logic here
        return throttle, brake
```

### API Integration
Use the digital twin programmatically:

```python
from digital_twin.core import DigitalTwin
import yaml

# Load config
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

# Create digital twin
dt = DigitalTwin(config)

# Run simulation step
dt.step(throttle_percent=50, brake_percent=0, time_step_s=0.1)

# Get telemetry
data = dt.get_telemetry()
print(data)
```

## Support

For issues or questions about the digital twin implementation, please refer to the documentation in each source file or contact the development team.
