import pandas as pd
import matplotlib.pyplot as plt
import os

# Define file paths
RESULTS_DIR = 'results'
INPUT_CSV = os.path.join(RESULTS_DIR, 'simulation_output.csv')
OUTPUT_PLOT_FILE = os.path.join(RESULTS_DIR, 'simulation_results.png')

def plot_results():
    """
    Loads simulation results from a CSV and plots them.
    """
    # Check if the results file exists
    if not os.path.exists(INPUT_CSV):
        print(f"Error: Results file not found at {INPUT_CSV}")
        print("Please run the main simulation first using 'python3 -m src.main'")
        return

    # Load the data
    print(f"Loading results from {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    print("Data loaded successfully.")

    # Create a figure with multiple subplots
    fig, axs = plt.subplots(3, 1, figsize=(15, 18), sharex=True)
    fig.suptitle('Simulation Results: Impact of PV Installation on Local Climate', fontsize=16)

    # --- Plot 1: Temperature Anomaly ---
    axs[0].plot(df['month'], df['temp_anomaly_C'], label='Temperature Anomaly', color='r')
    axs[0].set_ylabel('Temperature Anomaly (°C)')
    axs[0].set_title('Cumulative Local Temperature Change Caused by PV Panel')
    axs[0].grid(True, linestyle='--', alpha=0.6)
    axs[0].legend()

    # --- Plot 2: Local Temperature vs Baseline ---
    axs[1].plot(df['month'], df['local_temp_C'], label='Local Temperature (with PV)', color='orange')
    # To calculate the baseline, we subtract the anomaly from the local temp
    baseline_temp = df['local_temp_C'] - df['temp_anomaly_C']
    axs[1].plot(df['month'], baseline_temp, label='Baseline Temperature (no PV)', color='b', linestyle='--')
    axs[1].set_ylabel('Temperature (°C)')
    axs[1].set_title('Local Temperature vs. Baseline')
    axs[1].grid(True, linestyle='--', alpha=0.6)
    axs[1].legend()

    # --- Plot 3: PV Power Output ---
    axs[2].plot(df['month'], df['pv_power_W'], label='PV Power Output', color='g')
    axs[2].set_xlabel('Simulation Month')
    axs[2].set_ylabel('Power (W)')
    axs[2].set_title('PV Power Generation Over Time')
    axs[2].grid(True, linestyle='--', alpha=0.6)
    axs[2].legend()

    # Save the figure
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    print(f"Saving plot to {OUTPUT_PLOT_FILE}...")
    plt.savefig(OUTPUT_PLOT_FILE)
    print(f"Plot saved successfully. You can view it at {OUTPUT_PLOT_FILE}")
    plt.close()

if __name__ == "__main__":
    plot_results() 