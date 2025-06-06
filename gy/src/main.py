"""
Main entry point for the climate simulation project.
"""
from .simulation import Simulation
from .utils import save_results
from . import config
import os

def main():
    """
    Initializes and runs the simulation, then saves the results.
    """
    # Create results directory if it doesn't exist
    if not os.path.exists(config.RESULTS_DIR):
        os.makedirs(config.RESULTS_DIR)

    # Initialize and run the simulation
    sim = Simulation()
    results = sim.run()

    # Save the results
    output_file = os.path.join(config.RESULTS_DIR, "simulation_output.csv")
    save_results(results, output_file)

    print(f"All done. Results are in {output_file}")


if __name__ == "__main__":
    main() 