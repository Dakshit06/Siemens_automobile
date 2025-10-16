"""
Simulation Engine
Runs various driving scenarios for the digital twin.
"""

import numpy as np
from typing import List, Tuple
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_twin.core import DigitalTwin


class DrivingScenario:
    """Base class for driving scenarios"""
    
    def __init__(self, name: str, duration_s: float):
        self.name = name
        self.duration_s = duration_s
        
    def get_control_inputs(self, time: float) -> Tuple[float, float]:
        """Return (throttle_percent, brake_percent) at given time"""
        raise NotImplementedError


class UrbanDrivingScenario(DrivingScenario):
    """Urban driving with stop-and-go traffic"""
    
    def __init__(self):
        super().__init__("Urban Driving", 600)  # 10 minutes
        
    def get_control_inputs(self, time: float) -> Tuple[float, float]:
        # Simulate stop-and-go traffic
        cycle_time = 60  # 60 second cycles
        t = time % cycle_time
        
        if t < 20:  # Accelerate
            throttle = min(40 + t * 2, 60)
            brake = 0
        elif t < 30:  # Cruise
            throttle = 30
            brake = 0
        elif t < 40:  # Decelerate
            throttle = 0
            brake = 20 + (t - 30) * 3
        else:  # Stop
            throttle = 0
            brake = 50
            
        return throttle, brake


class HighwayDrivingScenario(DrivingScenario):
    """Highway driving at constant high speed"""
    
    def __init__(self):
        super().__init__("Highway Driving", 1800)  # 30 minutes
        
    def get_control_inputs(self, time: float) -> Tuple[float, float]:
        if time < 60:  # Ramp up
            throttle = min(70 + time, 100)
            brake = 0
        elif time > self.duration_s - 120:  # Slow down at end
            throttle = 30
            brake = 20
        else:  # Cruise at highway speed
            throttle = 45 + np.sin(time * 0.1) * 5  # Minor variations
            brake = 0
            
        return throttle, brake


class AggressiveDrivingScenario(DrivingScenario):
    """Aggressive driving with hard accelerations and braking"""
    
    def __init__(self):
        super().__init__("Aggressive Driving", 300)  # 5 minutes
        
    def get_control_inputs(self, time: float) -> Tuple[float, float]:
        cycle_time = 30
        t = time % cycle_time
        
        if t < 10:  # Hard acceleration
            throttle = 100
            brake = 0
        elif t < 15:  # Coast
            throttle = 0
            brake = 0
        elif t < 20:  # Hard braking
            throttle = 0
            brake = 80
        else:  # Stop
            throttle = 0
            brake = 50
            
        return throttle, brake


class EcoModeScenario(DrivingScenario):
    """Eco-friendly driving with smooth accelerations"""
    
    def __init__(self):
        super().__init__("Eco Mode", 900)  # 15 minutes
        
    def get_control_inputs(self, time: float) -> Tuple[float, float]:
        cycle_time = 90
        t = time % cycle_time
        
        if t < 30:  # Gentle acceleration
            throttle = min(20 + t * 0.8, 40)
            brake = 0
        elif t < 60:  # Cruise
            throttle = 35
            brake = 0
        else:  # Gentle deceleration
            throttle = max(35 - (t - 60) * 1.2, 0)
            brake = 10
            
        return throttle, brake


class SimulationEngine:
    """Main simulation engine"""
    
    def __init__(self, digital_twin: DigitalTwin, time_step: float = 0.1):
        self.digital_twin = digital_twin
        self.time_step = time_step
        self.scenarios = {
            "urban": UrbanDrivingScenario(),
            "highway": HighwayDrivingScenario(),
            "aggressive": AggressiveDrivingScenario(),
            "eco": EcoModeScenario()
        }
        
    def run_scenario(self, scenario_name: str, log_interval: int = 10):
        """Run a specific driving scenario"""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
            
        scenario = self.scenarios[scenario_name]
        print(f"\n{'='*60}")
        print(f"Running scenario: {scenario.name}")
        print(f"Duration: {scenario.duration_s}s")
        print(f"{'='*60}\n")
        
        steps = int(scenario.duration_s / self.time_step)
        log_counter = 0
        
        for step in range(steps):
            current_time = step * self.time_step
            throttle, brake = scenario.get_control_inputs(current_time)
            
            # Execute simulation step
            self.digital_twin.step(throttle, brake, self.time_step)
            
            # Log telemetry periodically
            log_counter += 1
            if log_counter >= log_interval:
                self.digital_twin.log_telemetry()
                log_counter = 0
                
            # Print progress
            if step % 100 == 0:
                progress = (step / steps) * 100
                telemetry = self.digital_twin.get_telemetry()
                print(f"Progress: {progress:.1f}% | "
                      f"Speed: {telemetry['vehicle']['speed_kmh']:.1f} km/h | "
                      f"Battery: {telemetry['battery']['soc_percent']:.1f}% | "
                      f"Motor Temp: {telemetry['motor']['temperature_c']:.1f}°C")
        
        print(f"\nScenario '{scenario.name}' completed!")
        self._print_summary()
        
    def run_custom_scenario(self, duration_s: float, throttle_profile: List[float], 
                          brake_profile: List[float]):
        """Run a custom scenario with provided throttle and brake profiles"""
        steps = len(throttle_profile)
        
        for step in range(steps):
            throttle = throttle_profile[step]
            brake = brake_profile[step]
            
            self.digital_twin.step(throttle, brake, self.time_step)
            
            if step % 10 == 0:
                self.digital_twin.log_telemetry()
                
    def _print_summary(self):
        """Print simulation summary"""
        if not self.digital_twin.telemetry_log:
            return
            
        final = self.digital_twin.telemetry_log[-1]
        initial = self.digital_twin.telemetry_log[0]
        
        distance_km = final['vehicle']['position_km']
        energy_consumed = (initial['battery']['charge_kwh'] - 
                          final['battery']['charge_kwh'])
        efficiency = (distance_km / energy_consumed) if energy_consumed > 0 else 0
        
        print(f"\n{'='*60}")
        print("SIMULATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Distance: {distance_km:.2f} km")
        print(f"Energy Consumed: {energy_consumed:.2f} kWh")
        print(f"Efficiency: {efficiency:.2f} km/kWh")
        print(f"Final Battery SOC: {final['battery']['soc_percent']:.1f}%")
        print(f"Max Speed: {max([t['vehicle']['speed_kmh'] for t in self.digital_twin.telemetry_log]):.1f} km/h")
        print(f"Motor Health: {final['motor']['health_score']:.1f}%")
        print(f"{'='*60}\n")


def main():
    """Test the simulation engine"""
    import yaml
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               'config', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Create digital twin
    dt = DigitalTwin(config)
    
    # Create simulation engine
    sim = SimulationEngine(dt)
    
    # Run urban driving scenario
    sim.run_scenario("urban")
    
    # Export telemetry
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                              'data', 'telemetry_urban.json')
    dt.export_telemetry(output_path)
    print(f"Telemetry exported to: {output_path}")


if __name__ == "__main__":
    main()
