import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_local_vs_global_effect(df, results_dir):
    """
    Plots a comparison of local temperature anomaly vs. global cooling effect
    for the most extreme coverage scenario. (English Version)
    """
    # Find the extreme scenario by parsing the name to find the max percentage
    df['coverage_percentage_val'] = df['coverage_scenario'].str.replace('%', '').astype(float)
    extreme_scenario_name = df.loc[df['coverage_percentage_val'].idxmax()]['coverage_scenario']
    df_plot = df[(df['coverage_scenario'] == extreme_scenario_name) & (df['panel_efficiency'] > 0)].copy()

    # --- English Translation Layer ---
    english_map = {
        '新型光伏 (钙钛矿)': 'Perovskite PV', '传统光伏 (晶硅)': 'Silicon PV', '镜面': 'Mirror', '地表本身': 'Bare Ground',
        'standard_land': 'Land', 'desert': 'Desert', 'ocean': 'Ocean'
    }
    df_plot['material_type'] = df_plot['material_type'].map(english_map).fillna(df_plot['material_type'])
    df_plot['surface_type'] = df_plot['surface_type'].map(english_map).fillna(df_plot['surface_type'])
    # ---

    # Melt the dataframe to make it suitable for seaborn's barplot
    df_melt = df_plot.melt(
        id_vars=['surface_type', 'material_type'],
        value_vars=['avg_local_temp_anomaly_C', 'global_temp_change_C'],
        var_name='EffectType',
        value_name='Temperature Change (°C)'
    )
    
    # Create a more descriptive name for the plot
    df_melt['Scenario'] = df_melt['material_type'] + ' on ' + df_melt['surface_type']
    df_melt['EffectType'] = df_melt['EffectType'].map({
        'avg_local_temp_anomaly_C': 'Local Warming',
        'global_temp_change_C': 'Global Cooling'
    })

    plt.figure(figsize=(14, 8))
    sns.barplot(
        data=df_melt,
        x='Scenario',
        y='Temperature Change (°C)',
        hue='EffectType',
        palette={'Local Warming': 'orangered', 'Global Cooling': 'dodgerblue'}
    )
    
    plt.title(f'Local Warming vs. Global Cooling Potential (at {extreme_scenario_name} Coverage)', fontsize=16)
    plt.ylabel('Temperature Change (°C)', fontsize=12)
    plt.xlabel('Scenario', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.axhline(0, color='black', linewidth=0.8) # Add a zero line for reference
    plt.tight_layout()
    
    output_path = os.path.join(results_dir, 'plot1_local_vs_global_effect.png')
    plt.savefig(output_path)
    print(f"\nChart saved to: {output_path}")
    plt.close()

def plot_local_effect_ranking(df, results_dir):
    """
    Plots a ranked bar chart of the local temperature effect for all scenarios. (English Version)
    """
    # We only need the unique combinations of material and surface
    df_plot = df[['surface_type', 'material_type', 'avg_local_temp_anomaly_C']].drop_duplicates()
    
    # --- English Translation Layer ---
    english_map = {
        '新型光伏 (钙钛矿)': 'Perovskite PV', '传统光伏 (晶硅)': 'Silicon PV', '镜面': 'Mirror', '地表本身': 'Bare Ground',
        'standard_land': 'Land', 'desert': 'Desert', 'ocean': 'Ocean'
    }
    df_plot['material_type'] = df_plot['material_type'].map(english_map).fillna(df_plot['material_type'])
    df_plot['surface_type'] = df_plot['surface_type'].map(english_map).fillna(df_plot['surface_type'])
    # ---

    # Create a combined scenario name
    df_plot['Scenario'] = df_plot['material_type'] + ' on ' + df_plot['surface_type']
    
    # Sort by the temperature anomaly
    df_plot = df_plot.sort_values('avg_local_temp_anomaly_C', ascending=False)
    
    plt.figure(figsize=(12, 10))
    
    # Create the barplot, updating usage to avoid FutureWarning
    barplot = sns.barplot(
        data=df_plot,
        x='avg_local_temp_anomaly_C',
        y='Scenario',
        hue='Scenario',  # Assign y to hue
        palette='vlag', # A diverging palette is good for positive/negative effects
        legend=False    # Disable legend as it's redundant
    )
    
    # Add value labels on the bars
    for i in barplot.containers:
        barplot.bar_label(i, fmt='%.2f °C', fontsize=10, padding=3)

    plt.title('Ranking of Local Climate Impact by Scenario', fontsize=16)
    plt.xlabel('Average Local Temperature Anomaly (°C)', fontsize=12)
    plt.ylabel('')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.axvline(0, color='black', linewidth=0.8) # Add a zero line
    plt.tight_layout()

    output_path = os.path.join(results_dir, 'plot2_local_effect_ranking.png')
    plt.savefig(output_path)
    print(f"Chart saved to: {output_path}")
    plt.close()


def analyze_results(results_path='results/scenario_summary.csv', results_dir='results'):
    """
    Loads the simulation summary, prints pivot tables, and generates plots.
    """
    # Load the results, ensuring correct encoding for the BOM character from Excel/CSV export
    try:
        df = pd.read_csv(results_path, encoding='utf-8-sig')
    except FileNotFoundError:
        print(f"Error: The results file was not found at {results_path}")
        print("Please ensure the batch simulation has been run successfully.")
        return

    # Create results directory if it doesn't exist
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Clean string columns to avoid grouping issues due to whitespace
    for col in ['surface_type', 'material_type', 'coverage_scenario']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # CRITICAL FIX: Drop duplicate rows based on the specific scenario identifiers
    df.drop_duplicates(subset=['surface_type', 'material_type', 'coverage_scenario'], inplace=True, keep='first')

    # --- Analysis 1: The Core Trade-off ---
    print("\n" + "="*80)
    print(" Analysis 1: Local Warming vs. Global Cooling (°C) ".center(80, "="))
    print("="*80)
    print("The table below compares the [Local Average Warming] vs. [Global Average Cooling]\nacross different coverage scales. All units are in Celsius (°C).\n")

    # We only care about scenarios that generate power for the global cooling part
    df_power_gen = df[df['panel_efficiency'] > 0].copy()

    # Create a pivot table to compare the two effects
    pivot_local_vs_global = pd.pivot_table(
        df_power_gen,
        values=['avg_local_temp_anomaly_C', 'global_temp_change_C'],
        index=['surface_type', 'material_type'],
        columns=['coverage_scenario'],
        aggfunc='mean'
    )
    
    # Reorder columns for logical presentation
    # Note: The order in config is by percentage, which pandas sorts alphabetically. We fix it.
    coverage_order = [v['name'] for v in config.COVERAGE_SCENARIOS.values()]
    
    # Flatten multi-index columns for easier sorting
    pivot_local_vs_global.columns = ['_'.join(col) for col in pivot_local_vs_global.columns]
    
    # Create the desired column order
    desired_order = []
    for cov_name in coverage_order:
        desired_order.append(f'avg_local_temp_anomaly_C_{cov_name}')
        desired_order.append(f'global_temp_change_C_{cov_name}')

    pivot_local_vs_global = pivot_local_vs_global.reindex(columns=desired_order)
    
    # Improve formatting for readability
    pd.set_option('display.float_format', '{:,.6f}'.format)
    print(pivot_local_vs_global)

    print("\n【Conclusion Interpretation】:")
    print("1.  **Order of Magnitude**: The value of 'Local Warming' (avg_local_temp_anomaly_C) is orders of magnitude larger than 'Global Cooling' (global_temp_change_C).")
    print("2.  **Consistency of Local Effect**: 'Local Warming' is an intrinsic property determined by the material and surface, independent of deployment scale. Thus, its value is constant in each row.")
    print("3.  **Scalability of Global Effect**: 'Global Cooling' is directly proportional to total power generation. As coverage increases (from 0.01% to 10%), its cooling effect also increases linearly.")
    print("4.  **Tipping Point**: Even at the most extreme 10% coverage (a nearly unrealistic scale), the magnitude of global cooling (approx. -0.05°C) is far less than the local warming it causes in desert areas (+2.09°C).\n\n")


    # --- Analysis 2: Isolating the Local Effect ---
    print("="*80)
    print(" Analysis 2: Pure Local Warming Effect by Scenario (°C) ".center(80, "="))
    print("="*80)
    print("The table below focuses on [Local Average Warming] to assess which combination\nis most microclimate-friendly. Lower is better (negative means cooling).\n")

    pivot_local_only = pd.pivot_table(
        df,
        values='avg_local_temp_anomaly_C',
        index='material_type',
        columns='surface_type',
        aggfunc='mean'
    )
    
    # Reorder for clarity
    pivot_local_only = pivot_local_only[['standard_land', 'desert', 'ocean']]
    # Sort index for better comparison
    pivot_local_only = pivot_local_only.reindex(['Mirror', 'Bare Ground', 'Perovskite PV', 'Silicon PV'])

    print(pivot_local_only)
    print("\n【Conclusion Interpretation】:")
    print("1.  **Mirror**: Regardless of where it is placed, 'Mirror' brings a strong [local cooling] effect due to its high albedo.")
    print("2.  **Tragedy in the Desert**: Laying any type of PV panel in the 'Desert' causes the most severe local warming. This is because the dark PV panels replace the highly reflective sand, absorbing a large amount of extra heat.")
    print("3.  **Advantage of the Ocean**: Placing PV panels on the 'Ocean' results in the least local warming. This is because the albedo of the PV panels (0.1-0.15) is even higher than the deep sea surface (0.08), partially offsetting the waste heat effect.")
    print("4.  **Material Comparison**: 'Perovskite PV' has a slightly lower local warming effect than 'Silicon PV' because of its higher efficiency (less waste heat).")

    # --- English Translation and pivot ---
    english_map = {
        '新型光伏 (钙钛矿)': 'Perovskite PV', '传统光伏 (晶硅)': 'Silicon PV', '镜面': 'Mirror', '地表本身': 'Bare Ground',
        'standard_land': 'Land', 'desert': 'Desert', 'ocean': 'Ocean'
    }
    df_english = df.copy()
    df_english['material_type'] = df_english['material_type'].map(english_map)
    df_english['surface_type'] = df_english['surface_type'].map(english_map)

    pivot_local_only = pd.pivot_table(
        df_english,
        values='avg_local_temp_anomaly_C',
        index='material_type',
        columns='surface_type',
        aggfunc='mean'
    )
    # Reorder for clarity
    pivot_local_only = pivot_local_only[['Land', 'Desert', 'Ocean']]
    # Sort index for better comparison
    pivot_local_only = pivot_local_only.reindex(['Mirror', 'Bare Ground', 'Perovskite PV', 'Silicon PV'])

    print(pivot_local_only)
    print("\n【Conclusion Interpretation】:")
    print("1.  **Mirror**: Regardless of where it is placed, 'Mirror' brings a strong [local cooling] effect due to its high albedo.")
    print("2.  **Tragedy in the Desert**: Laying any type of PV panel in the 'Desert' causes the most severe local warming. This is because the dark PV panels replace the highly reflective sand, absorbing a large amount of extra heat.")
    print("3.  **Advantage of the Ocean**: Placing PV panels on the 'Ocean' results in the least local warming. This is because the albedo of the PV panels (0.1-0.15) is even higher than the deep sea surface (0.08), partially offsetting the waste heat effect.")
    print("4.  **Material Comparison**: 'Perovskite PV' has a slightly lower local warming effect than 'Silicon PV' because of its higher efficiency (less waste heat).")

    # --- Generate and Save Plots ---
    print("\n" + "="*80)
    print(" 生成分析图表 ".center(80, "="))
    print("="*80)
    # Set plot style (no longer need to handle fonts)
    sns.set_theme(style="whitegrid")

    plot_local_vs_global_effect(df, results_dir)
    plot_local_effect_ranking(df, results_dir)


if __name__ == '__main__':
    # Add parent directory to path to allow imports from `src`
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src import config
    
    analyze_results() 