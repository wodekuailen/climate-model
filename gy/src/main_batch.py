import pandas as pd
import numpy as np
import time
from tqdm import tqdm

from . import config, utils
from .simulation import Simulation
from .pv_model import PVModel

def calculate_global_impact(total_energy_gwh):
    """Calculates the global temperature impact from CO2 reduction."""
    # 1. Convert GWh to kWh for the emission factor
    total_energy_kwh = total_energy_gwh * 1e6 

    # 2. Calculate total CO2 reduction in tonnes
    total_co2_reduction_tonnes = total_energy_kwh * config.CO2_EMISSION_FACTOR_Kwh / 1000

    # 3. Convert tonnes to GtCO2
    total_co2_reduction_gtco2 = total_co2_reduction_tonnes / 1e9

    # 4. Calculate global temperature change in °C
    # The TCRE constant is per 1000 GtCO2, so we must divide our value by 1000.
    global_temp_change_c = -( (total_co2_reduction_gtco2 / 1000) * config.TCRE_C_PER_1000_GTCO2)
    
    return global_temp_change_c, total_co2_reduction_gtco2

def main():
    """
    Main function to run the batch simulation for all scenarios using the correct Simulation Engine.
    """
    print("Starting batch simulation for all scenarios...")
    start_time = time.time()

    all_results = []
    total_scenarios = len(config.SURFACE_TYPES) * len(config.MATERIAL_TYPES) * len(config.COVERAGE_SCENARIOS)
    
    with tqdm(total=total_scenarios, desc="Simulating Scenarios") as pbar:
        # Loop through all defined scenarios
        for surface_key, surface_params in config.SURFACE_TYPES.items():
            for material_key, material_params in config.MATERIAL_TYPES.items():
                
                # --- UNIFIED SIMULATION ENGINE ---
                # 1. Create a fresh simulation instance for each scenario
                sim = Simulation()

                # 2. Set the parameters for the PV model within the simulation
                # If material is 'bare_ground', its albedo is the same as the surface albedo
                panel_albedo = material_params.get('albedo', surface_params['albedo'])
                if panel_albedo is None:
                    panel_albedo = surface_params['albedo']
                
                sim.pv.albedo = panel_albedo
                sim.pv.efficiency = material_params['efficiency']
                
                # Override the ground albedo in the config for this specific run
                config.GROUND_ALBEDO = surface_params['albedo']

                # 3. Run the simulation
                raw_results = sim.run()
                scenario_df = pd.DataFrame(raw_results)
                # ---
                
                # Calculate local impact: average temperature anomaly
                avg_local_temp_anomaly = scenario_df['temp_anomaly_C'].mean()

                # Calculate total simulation hours for energy calculation
                simulation_hours = (pd.to_datetime(config.TIME_END) - pd.to_datetime(config.TIME_START)).total_seconds() / 3600

                # Now, iterate through coverage scales to calculate global impact
                for coverage_key, coverage_params in config.COVERAGE_SCENARIOS.items():
                    # If material doesn't produce power, global impact is zero
                    if material_params['efficiency'] == 0:
                        global_temp_change = 0.0
                        total_co2_reduction = 0.0
                    else:
                        # Convert power from W to power density in W/m^2
                        # The simulation pv area is hardcoded as 1000 m^2 in the Simulation class
                        scenario_df['pv_power_density_W_m2'] = scenario_df['pv_power_W'] / 1000 

                        # Calculate total panel area based on Earth's surface and coverage percentage
                        total_panel_area_m2 = config.EARTH_SURFACE_AREA_M2 * coverage_params['percentage']
                        
                        # CRITICAL FIX: Calculate total energy generated over the simulation period in GWh
                        # Use the MEAN power density, not the SUM.
                        # Total Energy (Wh) = Mean Power Density (W/m^2) * Total Area (m^2) * Total Hours
                        mean_power_density_w_m2 = scenario_df['pv_power_density_W_m2'].mean()
                        total_energy_wh = mean_power_density_w_m2 * total_panel_area_m2 * simulation_hours
                        total_energy_gwh = total_energy_wh / 1e9
                        
                        # Calculate the global temperature impact
                        global_temp_change, total_co2_reduction = calculate_global_impact(total_energy_gwh)

                    # Store results
                    result = {
                        'surface_type': surface_key,
                        'material_type': material_params['name'],
                        'coverage_scenario': coverage_params['name'],
                        'surface_albedo': surface_params['albedo'],
                        'panel_albedo': panel_albedo,
                        'panel_efficiency': material_params['efficiency'],
                        'avg_local_temp_anomaly_C': avg_local_temp_anomaly,
                        'global_temp_change_C': global_temp_change,
                        'total_co2_reduction_Gt': total_co2_reduction
                    }
                    all_results.append(result)
                    pbar.update(1)

    # Convert results to DataFrame and save
    summary_df = pd.DataFrame(all_results)
    output_path = 'results/scenario_summary.csv'
    summary_df.to_csv(output_path, index=False, encoding='utf-8-sig')

    end_time = time.time()
    print(f"\nBatch simulation complete!")
    print(f"Total scenarios simulated: {len(all_results)}")
    print(f"Results saved to {output_path}")
    print(f"Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == '__main__':
    main() 