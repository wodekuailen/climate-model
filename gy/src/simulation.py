"""
Simulation engine.
Coordinates the different model components.
"""
from .climate_model import ClimateModel, calculate_net_radiation_change, calculate_local_temperature_anomaly
from .pv_model import PVModel, calculate_pv_power
from . import config, utils
import pandas as pd

class Simulation:
    def __init__(self):
        print("Initializing simulation...")
        self.climate = ClimateModel(
            temp_data_url=config.TEMP_DATA_URL,
            rad_data_url=config.RAD_DATA_URL
        )
        # We can increase the area to see a more pronounced effect
        self.pv = PVModel(area=1000) # 1000 m^2 PV installation
        self.results = []

    def run(self):
        print("Starting simulation run...")
        
        # Load climate data before starting the loop
        self.climate.load_data()
        if self.climate.temp_data is None or self.climate.rad_data is None:
            print("Halting simulation due to climate data loading failure.")
            return []

        for step in range(config.SIMULATION_STEPS):
            # Get climate variables for the current time step. 
            # Note: The temperature returned is the *current* local temperature,
            # including the anomaly from all previous steps.
            climate_vars = self.climate.get_variables(
                lat=config.SIMULATION_LAT,
                lon=config.SIMULATION_LON,
                time_index=step
            )
            
            if climate_vars is None:
                print(f"Skipping step {step} due to data error.")
                continue
            
            # --- Start Feedback Loop Calculation ---
            
            insolation = climate_vars["insolation"]
            current_local_temp = climate_vars["temperature"]

            # Calculate the power generated under the current local conditions
            final_power_W = self.pv.calculate_power(
                insolation, 
                current_local_temp
            )
            
            # Albedo effect: difference in absorbed radiation between PV and ground
            albedo_forcing_W = insolation * self.pv.area * (config.GROUND_ALBEDO - self.pv.albedo)
            
            # Waste heat effect: absorbed energy that is not converted to electricity
            absorbed_energy_W = insolation * self.pv.area * (1 - self.pv.albedo)
            waste_heat_forcing_W = absorbed_energy_W - final_power_W
            
            total_forcing_W = albedo_forcing_W + waste_heat_forcing_W
            
            # Apply this energy forcing to the climate model. This will update the 
            # internal temperature anomaly, which will be used in the *next* time step.
            self.climate.apply_energy_forcing(total_forcing_W, self.pv.area)

            # --- End Feedback Loop ---
            
            # Store results for this step
            self.results.append({
                "month": step,
                "local_temp_C": current_local_temp,
                "temp_anomaly_C": self.climate.temperature_anomaly_C,
                "insolation_W_m2": insolation,
                "albedo_forcing_W": albedo_forcing_W,
                "waste_heat_forcing_W": waste_heat_forcing_W,
                "pv_power_W": final_power_W
            })
            
        print("Simulation run finished.")
        return self.results