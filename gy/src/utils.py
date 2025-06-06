"""
Utility functions for data handling, etc.
"""
import pandas as pd
import os
import numpy as np
import xarray as xr
from . import config

def load_climate_data(lat, lon, time_start, time_end, freq):
    """
    Loads and prepares climate input data for the simulation.

    This function loads data from a remote NetCDF source, extracts the relevant
    time series for a specific location, and generates synthetic solar radiation data.

    Args:
        lat (float): Latitude for the simulation point.
        lon (float): Longitude for the simulation point.
        time_start (str): Start date for the time series (e.g., '2024-01-01').
        time_end (str): End date for the time series (e.g., '2043-12-31').
        freq (str): Frequency for the time series (e.g., '1M').

    Returns:
        dict: A dictionary containing two pandas.Series:
              'tmax' (maximum air temperature in °C) and
              'srad' (solar radiation in W/m^2).
    """
    try:
        # Load the remote dataset
        climate_data = xr.open_dataset(config.CLIMATE_DATA_URL)
        
        # The longitude in the dataset is in degrees East (0-360). Convert from (-180, 180).
        lon_conformed = lon if lon >= 0 else 360 + lon
        
        # Select the data point nearest to the specified lat/lon
        data_point = climate_data.sel(lat=lat, lon=lon_conformed, method='nearest')

        # The historical data ends in 2005. We will use the last 20 years of available
        # data (1986-2005) as a repeating climatology for our future simulation period.
        climatology = data_point.sel(time=slice('1986-01-01', '2005-12-31'))
        
        # Create the new time index for our simulation period
        time_index = pd.date_range(start=time_start, end=time_end, freq=freq)
        
        # Create the temperature time series by using the climatology directly.
        # Convert from Kelvin to Celsius.
        temp_values = climatology['air_temperature'].values
        tmax_series_values = temp_values - 273.15
        
        tmax_series = pd.Series(tmax_series_values, index=time_index, name='tmax')
        
        # Generate synthetic solar radiation (insolation) data
        # This is a simple sinusoidal model based on the month of the year for mid-latitudes
        month_of_year = time_index.month
        srad_values = 600 + 400 * np.sin((month_of_year - 4) * np.pi / 12)
        srad_series = pd.Series(srad_values, index=time_index, name='srad')
        
        climate_data.close()

        return {'tmax': tmax_series, 'srad': srad_series}

    except Exception as e:
        print(f"FATAL: Failed to load or process climate data: {e}")
        # In a real application, you might want to fall back to a default dataset or exit.
        # For this simulation, we will exit if data loading fails.
        raise 