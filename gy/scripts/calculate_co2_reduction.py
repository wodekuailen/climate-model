import pandas as pd

def calculate_co2_reduction(simulation_results_path, emission_factor):
    """
    Calculates the total CO2 reduction based on PV power generation data.

    Args:
        simulation_results_path (str): Path to the simulation results CSV file.
        emission_factor (float): CO2 emission factor in kgCO2/kWh.

    Returns:
        float: Total CO2 reduction in tonnes.
    """
    # Load the simulation results
    df = pd.read_csv(simulation_results_path)

    # Power is in Watts (W), and each time step is one month.
    # 1. Convert power from W to kW
    df['pv_power_kW'] = df['pv_power_W'] / 1000

    # 2. Calculate energy generated per month (Energy = Power * Time)
    # Average hours in a month = 24 hours/day * 365.25 days/year / 12 months/year ≈ 730.5 hours
    hours_per_month = 24 * 30.44
    df['monthly_energy_kWh'] = df['pv_power_kW'] * hours_per_month

    # 3. Calculate total energy generated over the whole simulation period
    total_energy_kWh = df['monthly_energy_kWh'].sum()

    # 4. Calculate total CO2 offset
    total_co2_offset_kg = total_energy_kWh * emission_factor
    
    # 5. Convert from kg to tonnes
    total_co2_offset_tonnes = total_co2_offset_kg / 1000
    
    return total_co2_offset_tonnes, total_energy_kWh

def main():
    """
    Main function to run the calculation and print the results.
    """
    # --- Parameters ---
    # Using the standard perovskite scenario for this calculation
    SIMULATION_FILE = 'results/simulation_output.csv' 
    # Official 2022 value from China's Ministry of Ecology and Environment
    CO2_EMISSION_FACTOR_CHINA = 0.5366  # kgCO2/kWh

    # --- Calculation ---
    total_reduction_tonnes, total_generation_gwh = calculate_co2_reduction(
        SIMULATION_FILE, 
        CO2_EMISSION_FACTOR_CHINA
    )
    # Convert kWh to GWh for readability
    total_generation_gwh = total_generation_gwh / 1_000_000

    # --- Output ---
    print("\n--- 全球效益分析：二氧化碳减排量计算 ---")
    print(f"\n基于模拟数据: '{SIMULATION_FILE}'")
    print(f"使用的电网排放因子: {CO2_EMISSION_FACTOR_CHINA} kgCO₂/kWh (中国2022年均值)")
    print("-" * 50)
    print(f"光伏电站在20年内总发电量: {total_generation_gwh:.2f} GWh (吉瓦时)")
    print(f"相当于抵消了电网的二氧化碳排放: {total_reduction_tonnes:,.0f} 吨")
    print("-" * 50)

    # --- Contextualizing the result ---
    # Average annual CO2 emissions for a passenger car is ~4.6 tonnes
    # Source: EPA (https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle)
    car_emissions_per_year = 4.6 # tonnes
    equivalent_cars_off_road = total_reduction_tonnes / car_emissions_per_year
    print("\n换算一下，这相当于：")
    print(f"让 {equivalent_cars_off_road:,.0f} 辆家用汽车停驶一年所减少的排放。")
    print("\n--- 分析结束 ---\n")

if __name__ == "__main__":
    main() 