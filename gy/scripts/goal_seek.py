"""
This script performs a "goal-seeking" analysis to determine the required
solar panel coverage to achieve a specific global cooling target.
"""
import pandas as pd
import numpy as np

from src import config, utils
from src.simulation import Simulation
from src.main_batch import calculate_global_impact

# --- Analysis Target ---
# What is the desired global cooling effect in degrees Celsius?
TARGET_COOLING_C = 1.5

def reverse_calculate_impact(target_cooling_c):
    """
    Reverse-engineers the calculations to find the required CO2 reduction
    and total energy generation for a given cooling target.
    """
    # 1. Reverse the TCRE formula to find required GtCO2 reduction
    # target_cooling = (GtCO2 / 1000) * TCRE  =>  GtCO2 = (target_cooling * 1000) / TCRE
    required_gtco2 = (target_cooling_c * 1000) / config.TCRE_C_PER_1000_GTCO2

    # 2. Reverse the CO2 emission factor to find required energy in GWh
    # GtCO2 = ( (GWh * 1e6 * CO2_FACTOR_kWh) / 1000 ) / 1e9
    # GtCO2 = GWh * 1e-6 * CO2_FACTOR_kWh
    # GWh = GtCO2 / (1e-6 * CO2_FACTOR_kWh)
    required_gwh = required_gtco2 / (1e-6 * config.CO2_EMISSION_FACTOR_Kwh)
    
    return required_gwh, required_gtco2

def main():
    """
    Main function to run the goal-seeking analysis.
    """
    print("="*80)
    print(f" Goal-Seeking Analysis: Finding parameters for {TARGET_COOLING_C}°C Global Cooling ".center(80))
    print("="*80)

    # 1. Calculate the required energy and CO2 reduction for our target
    required_gwh, required_gtco2 = reverse_calculate_impact(TARGET_COOLING_C)
    print(f"\nTo achieve a global cooling of {TARGET_COOLING_C}°C, we must generate enough clean energy")
    print(f"to offset a total of {required_gtco2:,.2f} Gt (billion tonnes) of CO2 over 20 years.")
    print(f"This requires a total generation of {required_gwh:,.2f} GWh of electricity.\n")

    # 2. For each scenario, calculate the coverage needed to produce this energy
    print("Calculating required coverage for each viable scenario...\n")
    
    goal_seek_results = []

    # Calculate total simulation hours (remains constant)
    simulation_hours = (pd.to_datetime(config.TIME_END) - pd.to_datetime(config.TIME_START)).total_seconds() / 3600

    # Loop through material/surface combinations to find their unique power density
    for surface_key, surface_params in config.SURFACE_TYPES.items():
        for material_key, material_params in config.MATERIAL_TYPES.items():
            
            # We only care about materials that can generate power
            if material_params['efficiency'] == 0:
                continue

            # --- Run a unit simulation to get performance characteristics ---
            sim = Simulation()
            panel_albedo = material_params.get('albedo', surface_params['albedo'])
            sim.pv.albedo = panel_albedo
            sim.pv.efficiency = material_params['efficiency']
            config.GROUND_ALBEDO = surface_params['albedo']
            
            # Suppress print statements from the simulation run for a cleaner output
            with utils.suppress_stdout():
                raw_results = sim.run()

            scenario_df = pd.DataFrame(raw_results)
            # ---

            # Calculate the two key metrics for this scenario
            avg_local_temp_anomaly_c = scenario_df['temp_anomaly_C'].mean()
            # The simulation pv area is 1000 m^2, so we divide by it to get power DENSITY
            mean_power_density_w_m2 = (scenario_df['pv_power_W'] / 1000).mean()

            # 3. Calculate the required area for this specific scenario
            # Total Energy (Wh) = Mean Power Density (W/m^2) * Total Area (m^2) * Total Hours
            # Total Area (m^2) = Total Energy (Wh) / (Mean Power Density * Total Hours)
            required_wh = required_gwh * 1e9
            required_area_m2 = required_wh / (mean_power_density_w_m2 * simulation_hours)
            
            # Convert area to a percentage of Earth's surface
            required_coverage_percent = (required_area_m2 / config.EARTH_SURFACE_AREA_M2) * 100

            goal_seek_results.append({
                "Scenario": f"{material_params['name']} on {surface_key}",
                "Required Coverage (%)": required_coverage_percent,
                "Resulting Local Warming (°C)": avg_local_temp_anomaly_c,
                "Power Density (W/m2)": mean_power_density_w_m2
            })
            
    # 4. Present results in a clean table
    results_df = pd.DataFrame(goal_seek_results)
    results_df = results_df.sort_values(by="Required Coverage (%)", ascending=True)
    results_df.set_index("Scenario", inplace=True)

    pd.set_option('display.float_format', '{:,.4f}'.format)
    print(results_df)

    print("\n" + "="*80)
    print(" Interpretation ".center(80))
    print("="*80)
    print("The table above shows the percentage of the *entire Earth's surface* that would need to")
    print("be covered by each specific type of solar panel to achieve the 1.5°C cooling target.")
    print("\nKey Takeaways:")
    print("1. **Feasibility**: The 'Required Coverage' column shows the immense scale required.")
    print("2. **Efficiency Matters**: Scenarios with higher 'Power Density' require less land.")
    print("3. **The Trade-Off**: Crucially, 'Resulting Local Warming' shows the severe local climate")
    print("   consequences of such a massive deployment. A solution for the globe could be a")
    print("   disaster for the local region.")

if __name__ == '__main__':
    main() 