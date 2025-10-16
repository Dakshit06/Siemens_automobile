"""
Main entry point for the Siemens Automobile Digital Twin
Provides a command-line interface to run different components.
"""

import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def run_simulation(scenario='urban'):
    """Run a driving simulation"""
    import yaml
    from digital_twin.core import DigitalTwin
    from simulation.engine import SimulationEngine
    
    print(f"\n{'='*60}")
    print("SIEMENS AUTOMOBILE DIGITAL TWIN - SIMULATION")
    print(f"{'='*60}\n")
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'config', 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Create digital twin
    print("Initializing digital twin...")
    dt = DigitalTwin(config)
    
    # Create simulation engine
    sim = SimulationEngine(dt)
    
    # Run scenario
    sim.run_scenario(scenario)
    
    # Export telemetry
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, f'telemetry_{scenario}.json')
    dt.export_telemetry(output_path)
    
    print(f"\n✓ Simulation complete!")
    print(f"✓ Telemetry data saved to: {output_path}\n")


def generate_report():
    """Generate analysis report"""
    from analysis.generate_report import main as report_main
    
    print(f"\n{'='*60}")
    print("SIEMENS AUTOMOBILE DIGITAL TWIN - REPORT GENERATION")
    print(f"{'='*60}\n")
    
    report_main()


def render_3d():
    """Render 3D visualization"""
    from visualization.render_3d import main as viz_main
    
    print(f"\n{'='*60}")
    print("SIEMENS AUTOMOBILE DIGITAL TWIN - 3D VISUALIZATION")
    print(f"{'='*60}\n")
    
    viz_main()


def start_dashboard():
    """Start web dashboard"""
    from visualization.dashboard import main as dashboard_main
    
    dashboard_main()


def start_3d_viewer():
    """Start the 3D viewer web server"""
    from visualization.viewer_3d import main as viewer_main
    
    print(f"\n{'='*60}")
    print("SIEMENS AUTOMOBILE DIGITAL TWIN - 3D VIEWER")
    print(f"{'='*60}\n")
    
    viewer_main()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Siemens Automobile Digital Twin System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run urban driving simulation
  python src/main.py simulate --scenario urban
  
  # Generate analysis report
  python src/main.py report
  
  # Render 3D visualization (Desktop)
  python src/main.py visualize
  
  # Start web dashboard
  python src/main.py dashboard

  # Start 3D Web Viewer
  python src/main.py viewer
  
  # Run complete workflow
  python src/main.py all --scenario urban
        """
    )
    
    parser.add_argument(
        'command',
        choices=['simulate', 'report', 'visualize', 'dashboard', 'viewer', 'all'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--scenario',
        default='urban',
        choices=['urban', 'highway', 'aggressive', 'eco'],
        help='Driving scenario for simulation (default: urban)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == 'simulate':
            run_simulation(args.scenario)
            
        elif args.command == 'report':
            generate_report()
            
        elif args.command == 'visualize':
            render_3d()
            
        elif args.command == 'dashboard':
            start_dashboard()

        elif args.command == 'viewer':
            start_3d_viewer()
            
        elif args.command == 'all':
            print("\n🚀 Running complete Digital Twin workflow...\n")
            run_simulation(args.scenario)
            generate_report()
            print("\n✓ Workflow complete! Check the 'reports' directory for outputs.\n")
            print("To view 3D visualization, run: python src/main.py visualize")
            print("To start dashboard, run: python src/main.py dashboard")
            print("To start 3D web viewer, run: python src/main.py viewer\n")
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
