"""
Configuration settings for the simulation.
"""

# File paths
DATA_DIR = "data/"
RESULTS_DIR = "results/"

# Simulation parameters
SIMULATION_STEPS = 240 # Number of months to simulate
SIMULATION_LAT = 40.0150  # Latitude for the simulation point (Boulder, CO)
SIMULATION_LON = -105.2705 # Longitude for the simulation point (Boulder, CO)

# -----------------------------------------------------------------------------
# GLOBAL CONSTANTS & SCENARIO PARAMETERS
# -----------------------------------------------------------------------------

# Earth Constants
EARTH_SURFACE_AREA_M2 = 5.101e14  # m^2

# Climate Model Parameters
CLIMATE_SENSITIVITY = 0.02  # °C / (W/m^2), lowered based on previous results
GROUND_ALBEDO_DEFAULT = 0.25      # Default average albedo for standard land
PV_TEMPERATURE_COEFFICIENT = -0.08  # %/°C, for perovskite cells

# CO2 Emission Parameters (Global Impact)
CO2_EMISSION_FACTOR_Kwh = 0.5366  # kgCO2/kWh (China's grid average 2022)
TCRE_C_PER_1000_GTCO2 = 0.5       # Transient Climate Response to Emissions, °C per 1000 GtCO2

# --- Simulation Scenarios ---

# 1. Surface Types (Ground Albedo)
SURFACE_TYPES = {
    'standard_land': {'albedo': 0.25},
    'desert': {'albedo': 0.40},
    'ocean': {'albedo': 0.08}
}

# 2. Material Types (PV Albedo and Efficiency)
# Efficiency = 0 means it does not generate power (e.g., mirror or bare ground)
MATERIAL_TYPES = {
    'perovskite_pv': {'albedo': 0.15, 'efficiency': 0.25, 'name': '新型光伏 (钙钛矿)'},
    'silicon_pv':    {'albedo': 0.10, 'efficiency': 0.18, 'name': '传统光伏 (晶硅)'},
    'mirror':        {'albedo': 0.85, 'efficiency': 0.0,  'name': '镜面'},
    'bare_ground':   {'albedo': None, 'efficiency': 0.0,  'name': '地表本身'} # Albedo will be inherited from the surface type
}

# 3. Coverage Scenarios (as a fraction of Earth's total surface area)
COVERAGE_SCENARIOS = {
    'small_scale':  {'percentage': 0.0001, 'name': '0.01%'}, # Equivalent to 0.0001 fraction
    'medium_scale': {'percentage': 0.001,  'name': '0.1%'},
    'large_scale':  {'percentage': 0.01,   'name': '1%'},
    'extreme_scale':{'percentage': 0.1,    'name': '10%'}
}


# Simulation Time Parameters (remains the same for all scenarios)
TIME_START = '2024-01-01'
TIME_END = '2043-12-31' # 20 years
TIME_FREQ = 'ME'

# --- Data Sources ---
# MACA v2 CONUS monthly max temperature data (online)
TEMP_DATA_URL = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_tasmax_BNU-ESM_r1i1p1_historical_1950_2005_CONUS_monthly.nc"
# MACA v2 CONUS monthly average downward shortwave radiation data (online)
RAD_DATA_URL = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_macav2metdata_rsds_BNU-ESM_r1i1p1_historical_1950_2005_CONUS_monthly.nc" 