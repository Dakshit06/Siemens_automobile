"""
Analysis and Reporting Module
Generates comprehensive reports with analytics, predictions, and visualizations.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from datetime import datetime
from typing import Dict, List
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DigitalTwinAnalyzer:
    """Analyzes telemetry data and generates insights"""
    
    def __init__(self, telemetry_log: List[Dict]):
        self.telemetry_log = telemetry_log
        self.df = self._convert_to_dataframe()
        
    def _convert_to_dataframe(self) -> pd.DataFrame:
        """Convert telemetry log to pandas DataFrame"""
        data = []
        for entry in self.telemetry_log:
            row = {
                'timestamp': entry.get('timestamp', ''),
                'simulation_time': entry.get('simulation_time', 0),
                'speed_kmh': entry['vehicle']['speed_kmh'],
                'position_km': entry['vehicle']['position_km'],
                'acceleration_mps2': entry['vehicle']['acceleration_mps2'],
                'motor_power_kw': entry['motor']['power_kw'],
                'motor_torque_nm': entry['motor']['torque_nm'],
                'motor_rpm': entry['motor']['rpm'],
                'motor_temp_c': entry['motor']['temperature_c'],
                'motor_health': entry['motor']['health_score'],
                'battery_soc': entry['battery']['soc_percent'],
                'battery_voltage': entry['battery']['voltage'],
                'battery_current': entry['battery']['current_a'],
                'battery_temp_c': entry['battery']['temperature_c'],
                'battery_health': entry['battery']['health_soh']
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def calculate_performance_metrics(self) -> Dict:
        """Calculate key performance metrics"""
        metrics = {
            'total_distance_km': self.df['position_km'].max(),
            'max_speed_kmh': self.df['speed_kmh'].max(),
            'avg_speed_kmh': self.df['speed_kmh'].mean(),
            'max_acceleration_mps2': self.df['acceleration_mps2'].max(),
            'total_energy_consumed_kwh': self._calculate_energy_consumed(),
            'energy_efficiency_km_per_kwh': self._calculate_efficiency(),
            'max_motor_power_kw': self.df['motor_power_kw'].max(),
            'avg_motor_power_kw': self.df['motor_power_kw'].mean(),
            'max_motor_temp_c': self.df['motor_temp_c'].max(),
            'avg_motor_temp_c': self.df['motor_temp_c'].mean(),
            'max_battery_temp_c': self.df['battery_temp_c'].max(),
            'avg_battery_temp_c': self.df['battery_temp_c'].mean(),
            'final_battery_soc': self.df['battery_soc'].iloc[-1],
            'battery_health_degradation': 100 - self.df['battery_health'].iloc[-1],
            'motor_health_degradation': 100 - self.df['motor_health'].iloc[-1]
        }
        
        return metrics
    
    def _calculate_energy_consumed(self) -> float:
        """Calculate total energy consumed"""
        if len(self.df) < 2:
            return 0.0
        initial_soc = self.df['battery_soc'].iloc[0]
        final_soc = self.df['battery_soc'].iloc[-1]
        
        # Assuming 75 kWh battery capacity
        battery_capacity = 75
        energy_consumed = (initial_soc - final_soc) / 100 * battery_capacity
        return max(0, energy_consumed)
    
    def _calculate_efficiency(self) -> float:
        """Calculate energy efficiency"""
        distance = self.df['position_km'].max()
        energy = self._calculate_energy_consumed()
        
        if energy > 0:
            return distance / energy
        return 0.0
    
    def detect_anomalies(self) -> List[Dict]:
        """Detect anomalies in the telemetry data"""
        anomalies = []
        
        # Check for temperature anomalies
        if self.df['motor_temp_c'].max() > 110:
            anomalies.append({
                'type': 'motor_overheating',
                'severity': 'high',
                'description': f"Motor temperature exceeded 110°C (max: {self.df['motor_temp_c'].max():.1f}°C)",
                'recommendation': 'Reduce load or check cooling system'
            })
        
        if self.df['battery_temp_c'].max() > 50:
            anomalies.append({
                'type': 'battery_overheating',
                'severity': 'medium',
                'description': f"Battery temperature exceeded 50°C (max: {self.df['battery_temp_c'].max():.1f}°C)",
                'recommendation': 'Activate thermal management system'
            })
        
        # Check for efficiency anomalies
        efficiency = self._calculate_efficiency()
        if efficiency < 4.0:
            anomalies.append({
                'type': 'low_efficiency',
                'severity': 'medium',
                'description': f"Energy efficiency below expected (current: {efficiency:.2f} km/kWh)",
                'recommendation': 'Review driving patterns and vehicle systems'
            })
        
        # Check for battery health
        battery_health = self.df['battery_health'].iloc[-1]
        if battery_health < 80:
            anomalies.append({
                'type': 'battery_degradation',
                'severity': 'high',
                'description': f"Battery health below 80% (current: {battery_health:.1f}%)",
                'recommendation': 'Schedule battery inspection and possible replacement'
            })
        
        return anomalies
    
    def predict_maintenance(self) -> List[Dict]:
        """Predict maintenance needs"""
        predictions = []
        
        # Motor maintenance prediction
        motor_health = self.df['motor_health'].iloc[-1]
        if motor_health < 95:
            remaining_hours = (motor_health - 70) * 100  # Simplified model
            predictions.append({
                'component': 'Electric Motor',
                'current_health': f"{motor_health:.1f}%",
                'estimated_hours_to_maintenance': max(0, remaining_hours),
                'maintenance_type': 'Inspection and bearing replacement',
                'priority': 'medium' if motor_health > 85 else 'high'
            })
        
        # Battery maintenance prediction
        battery_health = self.df['battery_health'].iloc[-1]
        if battery_health < 95:
            remaining_cycles = (battery_health - 70) * 50
            predictions.append({
                'component': 'Battery Pack',
                'current_health': f"{battery_health:.1f}%",
                'estimated_cycles_to_maintenance': max(0, remaining_cycles),
                'maintenance_type': 'Cell balancing and capacity test',
                'priority': 'medium' if battery_health > 85 else 'high'
            })
        
        # Temperature-based predictions
        avg_motor_temp = self.df['motor_temp_c'].mean()
        if avg_motor_temp > 90:
            predictions.append({
                'component': 'Motor Cooling System',
                'current_health': 'Warning',
                'estimated_hours_to_maintenance': 100,
                'maintenance_type': 'Coolant check and radiator cleaning',
                'priority': 'high'
            })
        
        return predictions
    
    def generate_visualizations(self, output_dir: str):
        """Generate visualization charts"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Speed over time
        ax1 = plt.subplot(3, 3, 1)
        ax1.plot(self.df['simulation_time'], self.df['speed_kmh'], 'b-', linewidth=2)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Speed (km/h)')
        ax1.set_title('Vehicle Speed Over Time')
        ax1.grid(True, alpha=0.3)
        
        # 2. Battery SOC
        ax2 = plt.subplot(3, 3, 2)
        ax2.plot(self.df['simulation_time'], self.df['battery_soc'], 'g-', linewidth=2)
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('SOC (%)')
        ax2.set_title('Battery State of Charge')
        ax2.grid(True, alpha=0.3)
        
        # 3. Motor power
        ax3 = plt.subplot(3, 3, 3)
        ax3.plot(self.df['simulation_time'], self.df['motor_power_kw'], 'r-', linewidth=2)
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Power (kW)')
        ax3.set_title('Motor Power Output')
        ax3.grid(True, alpha=0.3)
        
        # 4. Motor temperature
        ax4 = plt.subplot(3, 3, 4)
        ax4.plot(self.df['simulation_time'], self.df['motor_temp_c'], 'orange', linewidth=2)
        ax4.axhline(y=100, color='r', linestyle='--', label='Warning threshold')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Temperature (°C)')
        ax4.set_title('Motor Temperature')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Battery temperature
        ax5 = plt.subplot(3, 3, 5)
        ax5.plot(self.df['simulation_time'], self.df['battery_temp_c'], 'purple', linewidth=2)
        ax5.axhline(y=45, color='r', linestyle='--', label='Warning threshold')
        ax5.set_xlabel('Time (s)')
        ax5.set_ylabel('Temperature (°C)')
        ax5.set_title('Battery Temperature')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. Motor torque
        ax6 = plt.subplot(3, 3, 6)
        ax6.plot(self.df['simulation_time'], self.df['motor_torque_nm'], 'brown', linewidth=2)
        ax6.set_xlabel('Time (s)')
        ax6.set_ylabel('Torque (Nm)')
        ax6.set_title('Motor Torque')
        ax6.grid(True, alpha=0.3)
        
        # 7. Energy consumption rate
        ax7 = plt.subplot(3, 3, 7)
        power_consumption = self.df['motor_power_kw']
        ax7.plot(self.df['simulation_time'], power_consumption, 'c-', linewidth=2)
        ax7.set_xlabel('Time (s)')
        ax7.set_ylabel('Power (kW)')
        ax7.set_title('Instantaneous Energy Consumption')
        ax7.grid(True, alpha=0.3)
        
        # 8. Battery current
        ax8 = plt.subplot(3, 3, 8)
        ax8.plot(self.df['simulation_time'], self.df['battery_current'], 'm-', linewidth=2)
        ax8.set_xlabel('Time (s)')
        ax8.set_ylabel('Current (A)')
        ax8.set_title('Battery Current')
        ax8.grid(True, alpha=0.3)
        
        # 9. Efficiency over distance
        ax9 = plt.subplot(3, 3, 9)
        # Calculate rolling efficiency
        if len(self.df) > 10:
            window = 10
            rolling_distance = self.df['position_km'].diff().rolling(window).sum()
            rolling_energy = self.df['battery_soc'].diff().abs().rolling(window).sum() * 0.75  # 75 kWh capacity
            rolling_efficiency = rolling_distance / (rolling_energy + 0.001)
            ax9.plot(self.df['position_km'], rolling_efficiency, 'y-', linewidth=2)
        ax9.set_xlabel('Distance (km)')
        ax9.set_ylabel('Efficiency (km/kWh)')
        ax9.set_title('Energy Efficiency')
        ax9.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = os.path.join(output_dir, 'telemetry_analysis.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to: {output_path}")
        
        # Create separate health dashboard
        self._create_health_dashboard(output_dir)
    
    def _create_health_dashboard(self, output_dir: str):
        """Create a separate health monitoring dashboard"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Motor health
        axes[0, 0].plot(self.df['simulation_time'], self.df['motor_health'], 'b-', linewidth=2)
        axes[0, 0].axhline(y=90, color='orange', linestyle='--', label='Service threshold')
        axes[0, 0].axhline(y=80, color='r', linestyle='--', label='Critical threshold')
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Health (%)')
        axes[0, 0].set_title('Motor Health Score')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Battery health
        axes[0, 1].plot(self.df['simulation_time'], self.df['battery_health'], 'g-', linewidth=2)
        axes[0, 1].axhline(y=90, color='orange', linestyle='--', label='Service threshold')
        axes[0, 1].axhline(y=80, color='r', linestyle='--', label='Critical threshold')
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Health (%)')
        axes[0, 1].set_title('Battery State of Health')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Temperature distribution
        axes[1, 0].hist([self.df['motor_temp_c'], self.df['battery_temp_c']], 
                       bins=20, label=['Motor', 'Battery'], alpha=0.7)
        axes[1, 0].set_xlabel('Temperature (°C)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Temperature Distribution')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Power usage histogram
        axes[1, 1].hist(self.df['motor_power_kw'], bins=30, color='purple', alpha=0.7)
        axes[1, 1].set_xlabel('Power (kW)')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Power Usage Distribution')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = os.path.join(output_dir, 'health_dashboard.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Health dashboard saved to: {output_path}")


class ReportGenerator:
    """Generates comprehensive PDF reports"""
    
    def __init__(self, analyzer: DigitalTwinAnalyzer):
        self.analyzer = analyzer
        
    def generate_text_report(self, output_file: str):
        """Generate a comprehensive text report"""
        metrics = self.analyzer.calculate_performance_metrics()
        anomalies = self.analyzer.detect_anomalies()
        maintenance = self.analyzer.predict_maintenance()
        
        report = []
        report.append("=" * 80)
        report.append("SIEMENS AUTOMOBILE DIGITAL TWIN - ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Distance Traveled: {metrics['total_distance_km']:.2f} km")
        report.append(f"Energy Consumed: {metrics['total_energy_consumed_kwh']:.2f} kWh")
        report.append(f"Energy Efficiency: {metrics['energy_efficiency_km_per_kwh']:.2f} km/kWh")
        report.append(f"Final Battery SOC: {metrics['final_battery_soc']:.1f}%")
        report.append("")
        
        # Performance Metrics
        report.append("PERFORMANCE METRICS")
        report.append("-" * 80)
        report.append(f"Maximum Speed: {metrics['max_speed_kmh']:.1f} km/h")
        report.append(f"Average Speed: {metrics['avg_speed_kmh']:.1f} km/h")
        report.append(f"Maximum Acceleration: {metrics['max_acceleration_mps2']:.2f} m/s²")
        report.append(f"Maximum Motor Power: {metrics['max_motor_power_kw']:.1f} kW")
        report.append(f"Average Motor Power: {metrics['avg_motor_power_kw']:.1f} kW")
        report.append("")
        
        # Thermal Management
        report.append("THERMAL MANAGEMENT")
        report.append("-" * 80)
        report.append(f"Motor - Max Temperature: {metrics['max_motor_temp_c']:.1f}°C")
        report.append(f"Motor - Avg Temperature: {metrics['avg_motor_temp_c']:.1f}°C")
        report.append(f"Battery - Max Temperature: {metrics['max_battery_temp_c']:.1f}°C")
        report.append(f"Battery - Avg Temperature: {metrics['avg_battery_temp_c']:.1f}°C")
        report.append("")
        
        # Health Status
        report.append("COMPONENT HEALTH")
        report.append("-" * 80)
        motor_health = 100 - metrics['motor_health_degradation']
        battery_health = 100 - metrics['battery_health_degradation']
        report.append(f"Motor Health: {motor_health:.2f}% "
                     f"(Degradation: {metrics['motor_health_degradation']:.3f}%)")
        report.append(f"Battery Health: {battery_health:.2f}% "
                     f"(Degradation: {metrics['battery_health_degradation']:.3f}%)")
        report.append("")
        
        # Anomalies
        report.append("ANOMALY DETECTION")
        report.append("-" * 80)
        if anomalies:
            for i, anomaly in enumerate(anomalies, 1):
                report.append(f"{i}. [{anomaly['severity'].upper()}] {anomaly['type']}")
                report.append(f"   Description: {anomaly['description']}")
                report.append(f"   Recommendation: {anomaly['recommendation']}")
                report.append("")
        else:
            report.append("No anomalies detected. All systems operating normally.")
            report.append("")
        
        # Predictive Maintenance
        report.append("PREDICTIVE MAINTENANCE")
        report.append("-" * 80)
        if maintenance:
            for i, pred in enumerate(maintenance, 1):
                report.append(f"{i}. Component: {pred['component']}")
                report.append(f"   Current Health: {pred['current_health']}")
                report.append(f"   Maintenance Type: {pred['maintenance_type']}")
                report.append(f"   Priority: {pred['priority'].upper()}")
                if 'estimated_hours_to_maintenance' in pred:
                    report.append(f"   Estimated Time: {pred['estimated_hours_to_maintenance']:.0f} hours")
                elif 'estimated_cycles_to_maintenance' in pred:
                    report.append(f"   Estimated Cycles: {pred['estimated_cycles_to_maintenance']:.0f}")
                report.append("")
        else:
            report.append("No maintenance required at this time.")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 80)
        report.append("1. Continue monitoring motor temperature during high-load operations")
        report.append("2. Maintain battery SOC between 20-80% for optimal longevity")
        report.append("3. Schedule regular calibration of sensor systems")
        report.append("4. Review energy efficiency trends for optimization opportunities")
        report.append("")
        
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Text report generated: {output_file}")
        
        return '\n'.join(report)


def main():
    """Generate comprehensive analysis report"""
    # Load telemetry data
    telemetry_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 'data', 'telemetry_urban.json')
    
    if not os.path.exists(telemetry_path):
        print("Error: No telemetry data found. Please run the simulation first.")
        print("Run: python src/simulation/engine.py")
        return
    
    with open(telemetry_path, 'r') as f:
        telemetry_log = json.load(f)
    
    print(f"Loaded {len(telemetry_log)} telemetry records")
    
    # Create analyzer
    analyzer = DigitalTwinAnalyzer(telemetry_log)
    
    # Generate visualizations
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                              'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    print("\nGenerating visualizations...")
    analyzer.generate_visualizations(reports_dir)
    
    # Generate text report
    report_file = os.path.join(reports_dir, 'analysis_report.txt')
    generator = ReportGenerator(analyzer)
    print("\nGenerating text report...")
    report_text = generator.generate_text_report(report_file)
    
    # Print summary
    print("\n" + "="*80)
    print("REPORT GENERATION COMPLETE")
    print("="*80)
    print(f"Reports saved to: {reports_dir}")
    print(f"- Analysis Report: analysis_report.txt")
    print(f"- Telemetry Charts: telemetry_analysis.png")
    print(f"- Health Dashboard: health_dashboard.png")
    print("="*80)


if __name__ == "__main__":
    main()
