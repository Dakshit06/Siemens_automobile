"""
3D Visualization Module
Creates an interactive 3D model of the Siemens automobile digital twin.
Uses PyVista for 3D rendering and visualization.
"""

import pyvista as pv
import numpy as np
from typing import Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Vehicle3DModel:
    """3D model of the electric vehicle"""
    
    def __init__(self):
        self.plotter = None
        self.actors = {}
        self.battery_temp_colors = []
        self.motor_mesh = None
        self.battery_mesh = None
        self.wheel_meshes = []
        self.chassis_mesh = None
        
    def create_vehicle_geometry(self):
        """Create the 3D geometry for the vehicle"""
        
        # Chassis (simplified car body)
        chassis_length = 4.5
        chassis_width = 1.8
        chassis_height = 1.5
        
        self.chassis_mesh = pv.Box(
            bounds=(-chassis_length/2, chassis_length/2,
                   -chassis_width/2, chassis_width/2,
                   0, chassis_height)
        )
        
        # Wheels (4 cylinders)
        wheel_radius = 0.35
        wheel_width = 0.25
        wheel_positions = [
            (-1.3, -1.0, 0),  # Front left
            (-1.3, 1.0, 0),   # Front right
            (1.3, -1.0, 0),   # Rear left
            (1.3, 1.0, 0)     # Rear right
        ]
        
        for pos in wheel_positions:
            wheel = pv.Cylinder(
                center=pos,
                direction=(0, 1, 0),
                radius=wheel_radius,
                height=wheel_width
            )
            self.wheel_meshes.append(wheel)
        
        # Battery pack (underneath chassis)
        battery_length = 2.5
        battery_width = 1.4
        battery_height = 0.15
        
        self.battery_mesh = pv.Box(
            bounds=(-battery_length/2, battery_length/2,
                   -battery_width/2, battery_width/2,
                   -battery_height, 0)
        )
        
        # Electric motor (front of vehicle)
        self.motor_mesh = pv.Cylinder(
            center=(-1.5, 0, 0.3),
            direction=(1, 0, 0),
            radius=0.25,
            height=0.5
        )
        
        # Battery cells visualization (grid of small boxes)
        self.battery_cells = []
        cells_x = 10
        cells_y = 8
        cell_size = 0.08
        
        for i in range(cells_x):
            for j in range(cells_y):
                x = -battery_length/2 + (i + 0.5) * (battery_length / cells_x)
                y = -battery_width/2 + (j + 0.5) * (battery_width / cells_y)
                z = -battery_height / 2
                
                cell = pv.Cube(center=(x, y, z), x_length=cell_size, 
                              y_length=cell_size, z_length=cell_size)
                self.battery_cells.append(cell)
    
    def initialize_plotter(self, window_size=(1200, 800)):
        """Initialize the PyVista plotter"""
        self.plotter = pv.Plotter(window_size=window_size)
        self.plotter.set_background('white')
        
        # Add lighting
        self.plotter.add_light(pv.Light(position=(10, 10, 10), light_type='scene light'))
        
    def add_vehicle_to_scene(self):
        """Add all vehicle components to the scene"""
        if self.plotter is None:
            self.initialize_plotter()
        
        # Add chassis
        self.actors['chassis'] = self.plotter.add_mesh(
            self.chassis_mesh,
            color='lightblue',
            opacity=0.7,
            show_edges=True,
            edge_color='black',
            line_width=2
        )
        
        # Add wheels
        for i, wheel in enumerate(self.wheel_meshes):
            self.actors[f'wheel_{i}'] = self.plotter.add_mesh(
                wheel,
                color='black',
                show_edges=True
            )
        
        # Add battery pack
        self.actors['battery'] = self.plotter.add_mesh(
            self.battery_mesh,
            color='orange',
            opacity=0.8,
            show_edges=True,
            label='Battery Pack'
        )
        
        # Add battery cells with temperature coloring
        for i, cell in enumerate(self.battery_cells):
            actor = self.plotter.add_mesh(
                cell,
                color='green',
                show_edges=True
            )
            self.actors[f'battery_cell_{i}'] = actor
        
        # Add motor
        self.actors['motor'] = self.plotter.add_mesh(
            self.motor_mesh,
            color='red',
            opacity=0.9,
            show_edges=True,
            label='Electric Motor'
        )
        
        # Add axes
        self.plotter.add_axes(
            xlabel='X (m)',
            ylabel='Y (m)',
            zlabel='Z (m)'
        )
        
        # Add grid
        self.plotter.show_grid()
        
    def update_visualization(self, telemetry: Dict):
        """Update the 3D visualization based on telemetry data"""
        
        # Update motor color based on temperature
        motor_temp = telemetry['motor']['temperature_c']
        motor_color = self._temperature_to_color(motor_temp, 25, 120)
        if 'motor' in self.actors and self.motor_mesh is not None:
            self.plotter.remove_actor(self.actors['motor'])
            self.actors['motor'] = self.plotter.add_mesh(
                self.motor_mesh,
                color=motor_color,
                opacity=0.9,
                show_edges=True
            )
        
        # Update battery color based on SOC
        soc = telemetry['battery']['soc_percent']
        battery_color = self._soc_to_color(soc)
        if 'battery' in self.actors and self.battery_mesh is not None:
            self.plotter.remove_actor(self.actors['battery'])
            self.actors['battery'] = self.plotter.add_mesh(
                self.battery_mesh,
                color=battery_color,
                opacity=0.8,
                show_edges=True
            )
        
        # Update battery cells based on temperature
        battery_temp = telemetry['battery']['temperature_c']
        for i, cell in enumerate(self.battery_cells):
            # Simulate individual cell temperatures with variation
            cell_temp = battery_temp + np.random.normal(0, 2)
            cell_color = self._temperature_to_color(cell_temp, 20, 60)
            
            if f'battery_cell_{i}' in self.actors:
                self.plotter.remove_actor(self.actors[f'battery_cell_{i}'])
                self.actors[f'battery_cell_{i}'] = self.plotter.add_mesh(
                    cell,
                    color=cell_color,
                    show_edges=True
                )
        
        # Rotate wheels based on distance traveled
        # (This would require animation support)
        
    def _temperature_to_color(self, temp: float, min_temp: float, max_temp: float) -> str:
        """Convert temperature to color (blue=cold, red=hot)"""
        normalized = (temp - min_temp) / (max_temp - min_temp)
        normalized = max(0, min(1, normalized))
        
        if normalized < 0.5:
            # Blue to Yellow
            r = int(normalized * 2 * 255)
            g = int(normalized * 2 * 255)
            b = 255 - int(normalized * 2 * 255)
        else:
            # Yellow to Red
            r = 255
            g = 255 - int((normalized - 0.5) * 2 * 255)
            b = 0
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _soc_to_color(self, soc: float) -> str:
        """Convert battery SOC to color (red=low, green=high)"""
        normalized = soc / 100.0
        
        if normalized > 0.5:
            # Green
            return 'green'
        elif normalized > 0.2:
            # Yellow
            return 'yellow'
        else:
            # Red
            return 'red'
    
    def add_info_panel(self, telemetry: Dict):
        """Add information panel with telemetry data"""
        info_text = (
            f"SIEMENS EV DIGITAL TWIN\\n"
            f"{'='*40}\\n"
            f"Speed: {telemetry['vehicle']['speed_kmh']:.1f} km/h\\n"
            f"Battery SOC: {telemetry['battery']['soc_percent']:.1f}%\\n"
            f"Battery Temp: {telemetry['battery']['temperature_c']:.1f}°C\\n"
            f"Motor Power: {telemetry['motor']['power_kw']:.1f} kW\\n"
            f"Motor Temp: {telemetry['motor']['temperature_c']:.1f}°C\\n"
            f"Motor Torque: {telemetry['motor']['torque_nm']:.1f} Nm\\n"
            f"Distance: {telemetry['vehicle']['position_km']:.2f} km\\n"
            f"Motor Health: {telemetry['motor']['health_score']:.1f}%\\n"
        )
        
        self.plotter.add_text(info_text, position='upper_left', font_size=10)
    
    def render(self, telemetry: Optional[Dict] = None):
        """Render the 3D scene"""
        if self.plotter is None:
            self.initialize_plotter()
        
        self.create_vehicle_geometry()
        self.add_vehicle_to_scene()
        
        if telemetry:
            self.update_visualization(telemetry)
            self.add_info_panel(telemetry)
        
        # Set camera position
        self.plotter.camera_position = [
            (8, -8, 5),   # Camera position
            (0, 0, 0.5),  # Focal point
            (0, 0, 1)     # View up
        ]
        
        self.plotter.show()
    
    def save_screenshot(self, filename: str, telemetry: Optional[Dict] = None):
        """Save a screenshot of the current view"""
        if self.plotter is None:
            self.initialize_plotter()
            self.create_vehicle_geometry()
            self.add_vehicle_to_scene()
        
        if telemetry:
            self.update_visualization(telemetry)
            self.add_info_panel(telemetry)
        
        # Set camera position
        self.plotter.camera_position = [
            (8, -8, 5),
            (0, 0, 0.5),
            (0, 0, 1)
        ]
        
        self.plotter.screenshot(filename, transparent_background=False)
        print(f"Screenshot saved to: {filename}")
    
    def create_animation(self, telemetry_log: list, output_file: str):
        """Create an animation from telemetry log"""
        if self.plotter is None:
            self.initialize_plotter()
            self.create_vehicle_geometry()
            self.add_vehicle_to_scene()
        
        # Set up for animation
        self.plotter.open_movie(output_file)
        
        for i, telemetry in enumerate(telemetry_log):
            if i % 5 == 0:  # Update every 5 frames
                self.update_visualization(telemetry)
                self.add_info_panel(telemetry)
                self.plotter.write_frame()
        
        self.plotter.close()
        print(f"Animation saved to: {output_file}")


def main():
    """Test the 3D visualization"""
    import yaml
    import json
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               'config', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Load or generate telemetry data
    telemetry_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 'data', 'telemetry_urban.json')
    
    if os.path.exists(telemetry_path):
        with open(telemetry_path, 'r') as f:
            telemetry_log = json.load(f)
        telemetry = telemetry_log[len(telemetry_log) // 2]  # Middle snapshot
    else:
        # Create sample telemetry
        telemetry = {
            "motor": {
                "power_kw": 75.5,
                "torque_nm": 280.0,
                "temperature_c": 85.3,
                "health_score": 98.5
            },
            "battery": {
                "soc_percent": 65.4,
                "temperature_c": 35.2
            },
            "vehicle": {
                "speed_kmh": 60.0,
                "position_km": 15.3
            }
        }
    
    # Create and render 3D model
    model = Vehicle3DModel()
    
    # Save screenshot
    screenshot_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                  'reports', 'vehicle_3d_model.png')
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    model.save_screenshot(screenshot_path, telemetry)
    
    # Render interactive view
    model.render(telemetry)


if __name__ == "__main__":
    main()
