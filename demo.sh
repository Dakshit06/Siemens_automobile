#!/bin/bash

# Siemens Automobile Digital Twin - Demo Script
# This script runs a complete demonstration of the digital twin system

echo "============================================================"
echo "SIEMENS AUTOMOBILE DIGITAL TWIN - COMPLETE DEMO"
echo "============================================================"
echo ""

# Step 1: Run Simulation
echo "Step 1/3: Running Urban Driving Simulation..."
echo "------------------------------------------------------------"
python src/main.py simulate --scenario urban
echo ""

# Step 2: Generate Reports
echo "Step 2/3: Generating Analysis Reports..."
echo "------------------------------------------------------------"
python src/main.py report
echo ""

# Step 3: Display Results
echo "Step 3/3: Summary of Generated Files"
echo "------------------------------------------------------------"
echo ""
echo "📊 TELEMETRY DATA:"
ls -lh data/
echo ""
echo "📈 GENERATED REPORTS:"
ls -lh reports/
echo ""

# Display report summary
echo "============================================================"
echo "SIMULATION RESULTS SUMMARY"
echo "============================================================"
cat reports/analysis_report.txt | grep -A 15 "EXECUTIVE SUMMARY"
echo ""

echo "============================================================"
echo "DEMO COMPLETE!"
echo "============================================================"
echo ""
echo "✓ Simulation data: data/telemetry_urban.json"
echo "✓ Text report: reports/analysis_report.txt"
echo "✓ Performance charts: reports/telemetry_analysis.png"
echo "✓ Health dashboard: reports/health_dashboard.png"
echo ""
echo "Next steps:"
echo "  1. View charts: open reports/*.png"
echo "  2. Read full report: cat reports/analysis_report.txt"
echo "  3. Launch 3D view: python src/main.py visualize"
echo "  4. Start dashboard: python src/main.py dashboard"
echo ""
echo "For more options: python src/main.py --help"
echo "============================================================"
