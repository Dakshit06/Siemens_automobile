"""
Digital Twin Core Module
Defines the main components and sensors for the Siemens automobile digital twin.
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import json


class Sensor:
    """Base class for all sensor types"""
    
    def __init__(self, sensor_id: str, sensor_type: str, location: str, unit: str):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.location = location
        self.unit = unit
        self.value = 0.0
        self.timestamp = datetime.now()
        self.status = "active"
        self.calibration_factor = 1.0
        
    def read(self) -> float:
        """Read sensor value with noise simulation"""
        noise = np.random.normal(0, 0.02 * abs(self.value))
        return self.value * self.calibration_factor + noise
    
    def update(self, value: float):
        """Update sensor value"""
        self.value = value
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict:
        return {
            "sensor_id": self.sensor_id,
            "type": self.sensor_type,
            "location": self.location,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }


class ElectricMotor:
    """Electric motor model for the powertrain"""
    
    def __init__(self, max_power_kw: float = 150, max_torque_nm: float = 310):
        self.max_power_kw = max_power_kw
        self.max_torque_nm = max_torque_nm
        self.current_rpm = 0
        self.current_torque_nm = 0
        self.current_power_kw = 0
        self.temperature_c = 25.0
        self.efficiency = 0.95
        self.total_runtime_hours = 0
        self.health_score = 100.0
        
        # Sensors
        self.temp_sensor = Sensor("motor_temp", "temperature", "motor_housing", "°C")
        self.torque_sensor = Sensor("motor_torque", "torque", "motor_shaft", "Nm")
        self.rpm_sensor = Sensor("motor_rpm", "speed", "motor_shaft", "RPM")
        
    def apply_load(self, requested_torque: float, rpm: float):
        """Apply load to motor and calculate performance"""
        # Limit torque to max
        self.current_torque_nm = min(requested_torque, self.max_torque_nm)
        self.current_rpm = rpm
        
        # Calculate power output (P = T * ω / 1000)
        omega = rpm * 2 * np.pi / 60  # Convert RPM to rad/s
        self.current_power_kw = (self.current_torque_nm * omega / 1000) * self.efficiency
        self.current_power_kw = min(self.current_power_kw, self.max_power_kw)
        
        # Calculate temperature increase
        heat_generated = self.current_power_kw * (1 - self.efficiency)
        self.temperature_c += heat_generated * 0.1
        
        # Ambient cooling
        cooling_rate = (self.temperature_c - 25) * 0.05
        self.temperature_c -= cooling_rate
        
        # Update sensors
        self.temp_sensor.update(self.temperature_c)
        self.torque_sensor.update(self.current_torque_nm)
        self.rpm_sensor.update(self.current_rpm)
        
        # Health degradation
        if self.temperature_c > 120:
            self.health_score -= 0.001
            
    def get_status(self) -> Dict:
        return {
            "power_kw": round(self.current_power_kw, 2),
            "torque_nm": round(self.current_torque_nm, 2),
            "rpm": round(self.current_rpm, 2),
            "temperature_c": round(self.temperature_c, 2),
            "efficiency": self.efficiency,
            "health_score": round(self.health_score, 2)
        }


class BatteryPack:
    """Battery management system model"""
    
    def __init__(self, capacity_kwh: float = 75, nominal_voltage: float = 400):
        self.capacity_kwh = capacity_kwh
        self.nominal_voltage = nominal_voltage
        self.current_charge_kwh = capacity_kwh * 0.8  # Start at 80%
        self.current_voltage = nominal_voltage
        self.current_amperage = 0
        self.temperature_c = 25.0
        self.health_soh = 100.0  # State of Health
        self.cycle_count = 0
        self.cells_series = 96
        self.cells_parallel = 4
        
        # Cell voltage sensors (sample some cells)
        self.cell_voltages = [Sensor(f"cell_{i}_voltage", "voltage", f"cell_{i}", "V") 
                             for i in range(10)]
        self.temp_sensors = [Sensor(f"battery_temp_{i}", "temperature", f"pack_{i}", "°C") 
                            for i in range(4)]
        
    def discharge(self, power_kw: float, time_step_hours: float):
        """Discharge battery"""
        energy_consumed = power_kw * time_step_hours
        self.current_charge_kwh -= energy_consumed / self.efficiency_discharge()
        self.current_charge_kwh = max(0, self.current_charge_kwh)
        
        # Update current and voltage
        self.current_amperage = (power_kw * 1000) / self.current_voltage
        self.current_voltage = self.nominal_voltage * self.get_soc()
        
        # Heat generation
        heat = power_kw * (1 - self.efficiency_discharge()) * 0.5
        self.temperature_c += heat
        self.temperature_c -= (self.temperature_c - 25) * 0.1  # Cooling
        
        # Update sensors
        for i, sensor in enumerate(self.cell_voltages):
            cell_voltage = self.current_voltage / self.cells_series
            sensor.update(cell_voltage + np.random.normal(0, 0.01))
            
        avg_temp = self.temperature_c
        for sensor in self.temp_sensors:
            sensor.update(avg_temp + np.random.normal(0, 2))
        
    def charge(self, power_kw: float, time_step_hours: float):
        """Charge battery"""
        energy_added = power_kw * time_step_hours * self.efficiency_charge()
        self.current_charge_kwh += energy_added
        self.current_charge_kwh = min(self.capacity_kwh, self.current_charge_kwh)
        
        self.current_amperage = -(power_kw * 1000) / self.current_voltage
        
    def get_soc(self) -> float:
        """Get state of charge (0-1)"""
        return self.current_charge_kwh / self.capacity_kwh
    
    def efficiency_discharge(self) -> float:
        """Calculate discharge efficiency based on temperature and SOC"""
        temp_factor = 1.0 if 20 <= self.temperature_c <= 40 else 0.95
        return 0.95 * temp_factor
    
    def efficiency_charge(self) -> float:
        """Calculate charge efficiency"""
        return 0.92
    
    def get_status(self) -> Dict:
        return {
            "soc_percent": round(self.get_soc() * 100, 2),
            "charge_kwh": round(self.current_charge_kwh, 2),
            "voltage": round(self.current_voltage, 2),
            "current_a": round(self.current_amperage, 2),
            "temperature_c": round(self.temperature_c, 2),
            "health_soh": round(self.health_soh, 2),
            "cycle_count": self.cycle_count
        }


class VehicleDynamics:
    """Vehicle dynamics model"""
    
    def __init__(self, mass_kg: float = 1800):
        self.mass_kg = mass_kg
        self.velocity_mps = 0  # meters per second
        self.acceleration_mps2 = 0
        self.position_m = 0
        self.drag_coefficient = 0.28
        self.frontal_area_m2 = 2.3
        self.rolling_resistance = 0.015
        self.brake_force_n = 0
        
        # Sensors
        self.speed_sensor = Sensor("vehicle_speed", "speed", "wheel", "km/h")
        self.accel_sensor = Sensor("acceleration", "acceleration", "chassis", "m/s²")
        self.position_sensor = Sensor("gps_position", "position", "roof", "m")
        
    def update(self, motor_torque_nm: float, time_step_s: float, gear_ratio: float = 10.0):
        """Update vehicle dynamics"""
        # Calculate forces
        wheel_radius_m = 0.35
        drive_force_n = (motor_torque_nm * gear_ratio) / wheel_radius_m
        
        # Air resistance: F_drag = 0.5 * ρ * Cd * A * v²
        air_density = 1.225
        drag_force_n = 0.5 * air_density * self.drag_coefficient * self.frontal_area_m2 * (self.velocity_mps ** 2)
        
        # Rolling resistance: F_roll = Crr * m * g
        rolling_force_n = self.rolling_resistance * self.mass_kg * 9.81
        
        # Net force
        net_force_n = drive_force_n - drag_force_n - rolling_force_n - self.brake_force_n
        
        # Acceleration: a = F / m
        self.acceleration_mps2 = net_force_n / self.mass_kg
        
        # Update velocity and position
        self.velocity_mps += self.acceleration_mps2 * time_step_s
        self.velocity_mps = max(0, self.velocity_mps)  # Can't go backwards
        self.position_m += self.velocity_mps * time_step_s
        
        # Update sensors
        self.speed_sensor.update(self.velocity_mps * 3.6)  # Convert to km/h
        self.accel_sensor.update(self.acceleration_mps2)
        self.position_sensor.update(self.position_m)
        
    def apply_brakes(self, brake_percentage: float):
        """Apply braking force (0-100%)"""
        max_brake_force = self.mass_kg * 9.81 * 0.8  # 0.8g max deceleration
        self.brake_force_n = max_brake_force * (brake_percentage / 100.0)
        
    def get_status(self) -> Dict:
        return {
            "speed_kmh": round(self.velocity_mps * 3.6, 2),
            "acceleration_mps2": round(self.acceleration_mps2, 2),
            "position_km": round(self.position_m / 1000, 2),
            "brake_force_n": round(self.brake_force_n, 2)
        }


class DigitalTwin:
    """Main Digital Twin orchestrator"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.motor = ElectricMotor(
            max_power_kw=config['powertrain']['max_power_kw'],
            max_torque_nm=config['powertrain']['max_torque_nm']
        )
        self.battery = BatteryPack(
            capacity_kwh=config['battery']['capacity_kwh'],
            nominal_voltage=config['battery']['voltage_nominal']
        )
        self.dynamics = VehicleDynamics(mass_kg=config['vehicle']['weight_kg'])
        
        self.simulation_time = 0
        self.telemetry_log = []
        
    def step(self, throttle_percent: float, brake_percent: float, time_step_s: float = 0.1):
        """Execute one simulation step"""
        # Calculate motor demand
        max_torque = self.motor.max_torque_nm
        requested_torque = max_torque * (throttle_percent / 100.0)
        
        # Motor speed based on vehicle speed
        gear_ratio = 10.0
        wheel_radius = 0.35
        motor_rpm = (self.dynamics.velocity_mps / wheel_radius) * gear_ratio * (60 / (2 * np.pi))
        
        # Update motor
        self.motor.apply_load(requested_torque, motor_rpm)
        
        # Update battery
        if self.motor.current_power_kw > 0:
            self.battery.discharge(self.motor.current_power_kw, time_step_s / 3600)
        
        # Apply brakes
        self.dynamics.apply_brakes(brake_percent)
        
        # Update vehicle dynamics
        self.dynamics.update(self.motor.current_torque_nm, time_step_s, gear_ratio)
        
        self.simulation_time += time_step_s
        
    def get_telemetry(self) -> Dict:
        """Get current telemetry data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "simulation_time": round(self.simulation_time, 2),
            "motor": self.motor.get_status(),
            "battery": self.battery.get_status(),
            "vehicle": self.dynamics.get_status()
        }
    
    def log_telemetry(self):
        """Log telemetry data"""
        self.telemetry_log.append(self.get_telemetry())
        
    def export_telemetry(self, filename: str):
        """Export telemetry to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.telemetry_log, f, indent=2)
