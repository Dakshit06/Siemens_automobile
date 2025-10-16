# 🚗 Siemens Automobile Digital Twin# Siemens Automobile Digital Twin Project



A comprehensive digital twin implementation for an electric vehicle, featuring real-time 3D visualization, physics-based simulation, predictive analytics, and interactive dashboards.## Overview

This project implements a comprehensive Digital Twin for a Siemens electric vehicle, featuring real-time simulation, 3D visualization, predictive maintenance, and comprehensive analytics.

![Project Banner](https://img.shields.io/badge/Digital%20Twin-Siemens%20EV-blue?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3.12-green?style=for-the-badge&logo=python)## Project Structure

![Three.js](https://img.shields.io/badge/Three.js-WebGL-red?style=for-the-badge&logo=three.js)```

![Flask](https://img.shields.io/badge/Flask-SocketIO-black?style=for-the-badge&logo=flask)├── src/

│   ├── digital_twin/       # Core digital twin models

## 📑 Table of Contents│   ├── simulation/         # Simulation engine

│   ├── visualization/      # 3D rendering and dashboard

- [Overview](#overview)│   └── analysis/           # Data analysis and reporting

- [Features](#features)├── data/                   # Sensor data and telemetry

- [Architecture](#architecture)├── reports/                # Generated reports

- [Installation](#installation)├── models/                 # 3D model files

- [Quick Start](#quick-start)├── config/                 # Configuration files

- [Usage](#usage)└── tests/                  # Unit tests

- [Project Structure](#project-structure)

- [Technologies](#technologies)```



## 🎯 Overview## Features

- **Real-time Simulation**: Vehicle dynamics, powertrain, battery management

This project implements a complete digital twin for a Siemens electric vehicle, simulating:- **3D Visualization**: Interactive 3D model with real-time updates

- **Electric Motor**: 150 kW motor with thermal dynamics- **Predictive Maintenance**: AI-powered component health monitoring

- **Battery Management System**: 75 kWh battery with 96 cells- **Analytics Dashboard**: Web-based monitoring and control interface

- **Vehicle Dynamics**: Physics-based motion simulation- **Automated Reporting**: Comprehensive performance and analysis reports

- **160 Virtual Sensors**: Real-time monitoring of all components

## Technology Stack

## ✨ Features- Python 3.10+

- PyVista/VTK for 3D visualization

### 🎨 Real-time 3D Visualization- Flask for web dashboard

- **Three.js WebGL Rendering**: Smooth, interactive 3D graphics- NumPy/Pandas for data processing

- **80 Individual Battery Cells**: Color-coded temperature mapping- Matplotlib/Plotly for analytics

- **Dynamic Components**: Motor, battery, chassis, and wheels- SQLite for data storage

- **Interactive Camera Controls**: Orbit, zoom, and pan

- **Auto-rotation Mode**: Automated presentation view## Installation

- **Wireframe Toggle**: Technical visualization mode```bash

pip install -r requirements.txt

### 📊 Live Dashboard```

- **Real-time Metrics**: Speed, SOC, power, temperature

- **Interactive Charts**: Plotly-powered data visualization## Usage

- **Scenario Control**: Urban, Highway, Aggressive, Eco modes```bash

- **WebSocket Updates**: 10 Hz data streaming# Start the digital twin simulation

- **Mobile Responsive**: Works on all devicespython src/main.py



### 🔬 Simulation Engine# Generate analysis report

- **4 Driving Scenarios**: Comprehensive test casespython src/analysis/generate_report.py

- **Physics-based Calculations**: Realistic vehicle behavior

- **Thermal Dynamics**: Component heating and cooling# Launch 3D visualization

- **Energy Management**: Battery charge/discharge modelingpython src/visualization/render_3d.py

- **Telemetry Logging**: Complete data capture

# Start web dashboard

### 📈 Analytics & Reportingpython src/visualization/dashboard.py

- **Performance Metrics**: Detailed component analysis```

- **Anomaly Detection**: Predictive maintenance alerts

- **13 Visualization Charts**: Comprehensive data insights## Digital Twin Components

- **Export Capabilities**: JSON data export1. **Electric Powertrain**: Motor, inverter, transmission

- **Health Scoring**: Component degradation tracking2. **Battery Management System**: Cell monitoring, thermal management

3. **Vehicle Dynamics**: Suspension, braking, steering

## 🏗️ Architecture4. **Sensor Network**: Temperature, pressure, vibration, position sensors

5. **Control Systems**: ECU, BMS, ADAS

```

┌─────────────────────────────────────────────────────┐## Author

│                   User Interface                     │Siemens Automobile Digital Innovation Team

├──────────────────┬──────────────────────────────────┤
│  3D Viewer       │  Dashboard                        │
│  (Three.js)      │  (Plotly Charts)                  │
│  Port 5001       │  Port 5000                        │
└────────┬─────────┴────────┬────────────────────────┘
         │                  │
         │   WebSocket (Socket.IO)
         │                  │
┌────────┴──────────────────┴────────────────────────┐
│              Flask Backend Servers                  │
├─────────────────────────────────────────────────────┤
│  • viewer_3d.py    (3D streaming)                   │
│  • dashboard.py    (2D metrics)                     │
└────────┬────────────────────────────────────────────┘
         │
┌────────┴────────────────────────────────────────────┐
│           Simulation Engine & Digital Twin          │
├─────────────────────────────────────────────────────┤
│  • core.py         (Digital twin logic)             │
│  • engine.py       (Simulation scenarios)           │
│  • generate_report (Analytics)                      │
└─────────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prerequisites
- Python 3.12 or higher
- pip package manager
- Git

### Clone Repository

```bash
git clone https://github.com/Dakshit06/Siemens_automobile.git
cd Siemens_automobile
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 🎮 Quick Start

### Option 1: Run Everything
```bash
python src/main.py all
```

### Option 2: Individual Components

#### 1. Run Simulation
```bash
python src/main.py simulate --scenario urban
```

#### 2. Generate Reports
```bash
python src/main.py report
```

#### 3. Launch 3D Viewer
```bash
python src/main.py viewer
```
Then open: http://localhost:5001

#### 4. Launch Dashboard
```bash
python src/main.py dashboard
```
Then open: http://localhost:5000

### Quick Demo Script
```bash
chmod +x demo.sh
./demo.sh
```

## 📖 Usage

### Running Different Scenarios

```bash
# Urban driving (stop-and-go traffic)
python src/main.py simulate --scenario urban

# Highway driving (steady speed)
python src/main.py simulate --scenario highway

# Aggressive driving (hard acceleration/braking)
python src/main.py simulate --scenario aggressive

# Eco mode (efficient driving)
python src/main.py simulate --scenario eco
```

### Viewing Results

```bash
# View generated reports
cat reports/analysis_report.txt

# List all generated files
ls -lh reports/

# Check system status
./check_status.sh
```

### Interactive 3D Viewer Controls

- **Drag**: Rotate the vehicle
- **Scroll**: Zoom in/out
- **Reset View**: Return to default camera position
- **Auto Rotate**: Enable automatic rotation
- **Wireframe**: Toggle wireframe mode

## 📁 Project Structure

```
Siemens_automobile/
├── config/
│   └── config.yaml              # Configuration parameters
├── src/
│   ├── main.py                  # CLI entry point
│   ├── digital_twin/
│   │   └── core.py              # Digital twin implementation
│   ├── simulation/
│   │   └── engine.py            # Simulation engine
│   ├── analysis/
│   │   └── generate_report.py  # Analytics and reporting
│   └── visualization/
│       ├── dashboard.py         # Web dashboard server
│       ├── viewer_3d.py         # 3D viewer server
│       ├── render_3d.py         # PyVista rendering
│       ├── templates/           # HTML templates
│       └── static/              # Static assets
├── data/                        # Simulation outputs
├── reports/                     # Generated reports
├── images/                      # Documentation images
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🛠️ Technologies

### Backend
- **Python 3.12**: Core language
- **NumPy**: Numerical computations
- **Pandas**: Data processing
- **SciPy**: Scientific computing
- **scikit-learn**: Anomaly detection

### Web Stack
- **Flask**: Web framework
- **Flask-SocketIO**: Real-time communication
- **Socket.IO**: WebSocket protocol

### Visualization
- **Three.js**: 3D WebGL rendering
- **Plotly**: Interactive charts
- **Matplotlib**: Static plots
- **PyVista**: Advanced 3D visualization

## 🎯 Key Statistics

- **Python Code**: 2,000+ lines
- **Documentation**: 500+ lines
- **Virtual Sensors**: 160
- **Driving Scenarios**: 4
- **3D Components**: 85+ (chassis, motor, battery, 80 cells, 4 wheels)
- **Charts Generated**: 13
- **Telemetry Points**: 600+ per simulation
- **Update Frequency**: 10 Hz

## 👤 Author

**Dakshit06**
- GitHub: [@Dakshit06](https://github.com/Dakshit06)

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

<div align="center">
  <p><strong>⭐ Star this repository if you find it helpful!</strong></p>
  <p>Made with ❤️ for Digital Twin Technology</p>
</div>
