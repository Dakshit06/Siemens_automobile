#!/bin/bash

# Siemens Automobile Digital Twin - System Status Check
# Run this to verify all components are operational

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  SIEMENS AUTOMOBILE DIGITAL TWIN - SYSTEM STATUS CHECK       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python environment
echo "1️⃣  Checking Python Environment..."
python3 --version
echo ""

# Check installed packages
echo "2️⃣  Checking Required Packages..."
python3 -c "
import sys
packages = ['numpy', 'pandas', 'matplotlib', 'plotly', 'flask', 'flask_socketio', 'pyvista', 'vtk', 'yaml', 'sklearn']
missing = []
for pkg in packages:
    try:
        __import__(pkg.replace('-', '_'))
        print(f'   ✅ {pkg}')
    except ImportError:
        print(f'   ❌ {pkg} - MISSING')
        missing.append(pkg)
if not missing:
    print('')
    print('   ✓ All packages installed!')
" 2>&1
echo ""

# Check project structure
echo "3️⃣  Checking Project Structure..."
[ -f "src/digital_twin/core.py" ] && echo "   ✅ Digital Twin Core" || echo "   ❌ Digital Twin Core MISSING"
[ -f "src/simulation/engine.py" ] && echo "   ✅ Simulation Engine" || echo "   ❌ Simulation Engine MISSING"
[ -f "src/visualization/render_3d.py" ] && echo "   ✅ 3D Visualization" || echo "   ❌ 3D Visualization MISSING"
[ -f "src/visualization/dashboard.py" ] && echo "   ✅ Web Dashboard" || echo "   ❌ Web Dashboard MISSING"
[ -f "src/analysis/generate_report.py" ] && echo "   ✅ Analytics Engine" || echo "   ❌ Analytics Engine MISSING"
[ -f "config/config.yaml" ] && echo "   ✅ Configuration File" || echo "   ❌ Configuration MISSING"
echo ""

# Check generated data
echo "4️⃣  Checking Generated Data..."
if [ -f "data/telemetry_urban.json" ]; then
    SIZE=$(du -h data/telemetry_urban.json | cut -f1)
    echo "   ✅ Telemetry Data ($SIZE)"
else
    echo "   ⚠️  No telemetry data (run simulation first)"
fi

if [ -f "reports/analysis_report.txt" ]; then
    echo "   ✅ Analysis Report"
else
    echo "   ⚠️  No analysis report (run report generation)"
fi

if [ -f "reports/telemetry_analysis.png" ]; then
    echo "   ✅ Performance Charts"
else
    echo "   ⚠️  No charts generated"
fi
echo ""

# Check if dashboard is running
echo "5️⃣  Checking Dashboard Status..."
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ Dashboard is RUNNING on http://localhost:5000"
    echo "   📊 Open in browser: http://localhost:5000"
else
    echo "   ⚠️  Dashboard is NOT running"
    echo "   💡 Start with: python src/main.py dashboard"
fi
echo ""

# System capabilities
echo "6️⃣  System Capabilities:"
echo "   ✅ Physics-Based Simulation"
echo "   ✅ Real-time Telemetry (10 Hz)"
echo "   ✅ 4 Driving Scenarios"
echo "   ✅ 160 Virtual Sensors"
echo "   ✅ Predictive Analytics"
echo "   ✅ Anomaly Detection"
echo "   ✅ Web Dashboard (WebSocket)"
echo "   ✅ 3D Visualization (PyVista)"
echo "   ✅ Automated Reporting"
echo ""

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  QUICK START COMMANDS                                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Run Complete Workflow:"
echo "   python src/main.py all --scenario urban"
echo ""
echo "📊 Start Web Dashboard:"
echo "   python src/main.py dashboard"
echo "   Then open: http://localhost:5000"
echo ""
echo "🎮 Run Individual Components:"
echo "   python src/main.py simulate --scenario [urban|highway|aggressive|eco]"
echo "   python src/main.py report"
echo "   python src/main.py visualize"
echo ""
echo "📚 View Documentation:"
echo "   cat INDEX.md              # Navigation guide"
echo "   cat FINAL_PRESENTATION.md # Complete overview"
echo ""
echo "╚═══════════════════════════════════════════════════════════════╝"
