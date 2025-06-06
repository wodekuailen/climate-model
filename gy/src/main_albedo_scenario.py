"""
Main entry point for the high-albedo PV scenario.
"""
from .simulation import Simulation
from .utils import save_results
from . import config
import os

def main():
    """
    Initializes and runs a special simulation for a high-albedo PV material,
    then saves the results to a separate file.
    """
    print("--- Running High-Albedo Scenario ---")

    # Create results directory if it doesn't exist
    if not os.path.exists(config.RESULTS_DIR):
        os.makedirs(config.RESULTS_DIR)

    # Initialize the simulation
    sim = Simulation()

    # --- Modify PV parameters for this specific scenario ---
    # Assume this high-albedo material has a slightly lower efficiency
    sim.pv.efficiency = 0.22
    sim.pv.albedo = 0.40 # Higher than ground albedo (0.25)
    print(f"PV parameters modified for high-albedo scenario: efficiency={sim.pv.efficiency}, albedo={sim.pv.albedo}")

    # Run the simulation
    results = sim.run()

    # Save the results to a new file
    output_file = os.path.join(config.RESULTS_DIR, "simulation_output_high_albedo.csv")
    save_results(results, output_file)

    print(f"All done. High-albedo scenario results are in {output_file}")


if __name__ == "__main__":
    main() 