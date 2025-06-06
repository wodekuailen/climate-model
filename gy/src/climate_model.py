"""
Climate model component.
Handles climate data and related calculations.
"""
import xarray as xr
import numpy as np
from . import config

class ClimateModel:
    def __init__(self, temp_data_url, rad_data_url):
        self.temp_data_url = temp_data_url
        self.rad_data_url = rad_data_url
        self.temp_data = None
        self.rad_data = None
        self.temperature_anomaly_C = 0.0
        print("ClimateModel initialized with separate Temp and Rad sources.")

    def load_data(self):
        print(f"Loading temperature data from {self.temp_data_url}...")
        try:
            self.temp_data = xr.open_dataset(self.temp_data_url)
            print("Temperature data loaded successfully.")
        except Exception as e:
            print(f"Failed to load temperature data: {e}")
            self.temp_data = None

        print(f"Loading radiation data from {self.rad_data_url}...")
        try:
            self.rad_data = xr.open_dataset(self.rad_data_url)
            print("Radiation data loaded successfully.")
        except Exception as e:
            print(f"Failed to load radiation data: {e}")
            self.rad_data = None

    def get_variables(self, lat, lon, time_index):
        """
        Extracts climate variables for a given location and time step from their respective datasets.
        """
        if self.temp_data is None or self.rad_data is None:
            print("Error: Climate data (Temp or Rad) not loaded.")
            return None

        # The longitude in the dataset is in degrees East (0-360). Convert from (-180, 180).
        lon_conformed = lon if lon >= 0 else 360 + lon

        try:
            # Select the data point nearest to the specified lat/lon from the TEMP dataset
            temp_data_point = self.temp_data.sel(
                lat=lat,
                lon=lon_conformed,
                time=self.temp_data.time[time_index],
                method='nearest'
            )
            # Select the data point nearest to the specified lat/lon from the RAD dataset
            rad_data_point = self.rad_data.sel(
                lat=lat,
                lon=lon_conformed,
                time=self.rad_data.time[time_index],
                method='nearest'
            )

            # Extract temperature and convert from Kelvin to Celsius
            temp_k = temp_data_point['air_temperature'].item()
            baseline_temp_c = temp_k - 273.15

            # The actual temperature includes the anomaly from previous steps
            current_temp_c = baseline_temp_c + self.temperature_anomaly_C

            # Extract downward shortwave radiation (rsds) as insolation
            # The variable name in the NetCDF file is 'surface_downwelling_shortwave_flux_in_air'
            insolation = rad_data_point['surface_downwelling_shortwave_flux_in_air'].item()

            return {"temperature": current_temp_c, "insolation": insolation}

        except Exception as e:
            print(f"Error extracting data for time_index {time_index}: {e}")
            return None

    def apply_energy_forcing(self, energy_watts, area_m2):
        """
        Calculates the temperature change from an energy forcing (in Watts)
        over a given area (in m^2) and updates the internal anomaly.
        This is a highly simplified model.
        """
        # Convert total watts to W/m^2
        forcing_w_m2 = energy_watts / area_m2
        
        # Apply the sensitivity factor to get the temperature change.
        # This is now a direct effect, not a cumulative one.
        self.temperature_anomaly_C = forcing_w_m2 * config.CLIMATE_SENSITIVITY 

def calculate_local_temperature_anomaly(net_radiation_change):
    """
    Calculates the local temperature anomaly based on the net radiation change.

    Args:
        net_radiation_change (pd.Series): Change in net radiation at the surface (W/m^2).

    Returns:
        pd.Series: Local temperature anomaly in degrees Celsius.
    """
    # This is a highly simplified model. In reality, the relationship is
    # incredibly complex and involves atmospheric dynamics, heat capacity of
    # the ground/water, etc. We use a simple sensitivity factor.
    # The temperature anomaly is a direct result of the current radiation change,
    # not a cumulative effect over time.
    temperature_anomaly = net_radiation_change * config.CLIMATE_SENSITIVITY
    return temperature_anomaly

def calculate_net_radiation_change(solar_irradiance, ground_albedo, panel_albedo, pv_efficiency):
    """
    Calculates the change in net radiation at the surface due to the PV installation.

    Args:
        solar_irradiance (pd.Series): Solar irradiance data (W/m^2).
        ground_albedo (float): The albedo of the ground surface.
        panel_albedo (float): The albedo of the PV panel.
        pv_efficiency (float): The efficiency of the PV panel in converting solar energy to electricity.

    Returns:
        pd.Series: Change in net radiation at the surface (W/m^2).
    """
    # Energy absorbed by the ground (before PV)
    energy_absorbed_ground = solar_irradiance * (1 - ground_albedo)

    # Energy absorbed by the PV panel
    energy_absorbed_panel = solar_irradiance * (1 - panel_albedo)

    # Of the absorbed energy, some is converted to electricity, the rest is waste heat
    waste_heat = energy_absorbed_panel * (1 - pv_efficiency)

    # The change in net radiation is the difference between the heat released by the
    # panel and the energy that would have been absorbed by the ground.
    # Positive value means more energy is being added to the local environment (warming).
    net_radiation_change = waste_heat - energy_absorbed_ground

    return net_radiation_change 