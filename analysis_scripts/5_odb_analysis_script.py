# -----------------------------------------------------------------------------
# Script: 5_odb_analysis_script.py
# Author: Vijayaraj Nagarajan PhD
# Assistant: Google Gemini
#
# Objective:
# To analyze the per-dataset benchmark results for multiple tools. This script
# reads the detailed output from the main benchmark run and calculates
# aggregate statistics (mean and standard deviation) for every scoring metric,
# providing a high-level summary of each tool's performance.
#
# Inputs:
#   - `<tool_name>_benchmark_results.csv` (for each tool in the `TOOL_NAMES` list)
#
# Outputs:
#   - For each tool, it generates a summary CSV file:
#     - `<tool_name>_final_summary.csv`: Contains the mean and standard deviation for each metric.
# -----------------------------------------------------------------------------

import pandas as pd
import numpy as np

# A list of all tool names to analyze. The script will loop through these.
TOOL_NAMES = [
    "gemini_2_5_pro_gex",
    "gemini_2_5_pro_gex_exp",
    "ian_outputs",
    "chatgpt_gex",
    "chatgpt_gex_exp",
    "claude_gex",
    "claude_gex_exp"
]

# Print a header indicating the start of the analysis script.
print(f"--- [START] ODB Multi-Tool Analysis ---")

# Loop through each tool name specified in the TOOL_NAMES list.
for tool_name in TOOL_NAMES:
    # Print a separator and header for the currently processing tool.
    print("\n" + "="*80)
    print(f"--- Processing Tool: [{tool_name}] ---")
    print("="*80)

    # Construct the full filename for the raw results CSV for the current tool.
    input_csv_file = f"{tool_name}_benchmark_results.csv"
    # Print a message indicating which file is being loaded.
    print(f"1. Loading data from input file: '{input_csv_file}'\n")

    # Use a try-except block to handle cases where a tool's result file might not exist.
    try:
        # Read the CSV file into a pandas DataFrame.
        results_df = pd.read_csv(input_csv_file)
        # Print a success message if the file is loaded.
        print("   [SUCCESS] Data loaded successfully.")
    # Catch the specific error for a file not being found.
    except FileNotFoundError:
        # Print an error message indicating the missing file.
        print(f"   [ERROR] The file '{input_csv_file}' was not found.")
        # Print a message that analysis for this tool will be skipped.
        print("   Skipping analysis for this tool.\n")
        # Continue to the next iteration of the loop, skipping the rest of the code for this tool.
        continue

    # Print a header for the data inspection step.
    print("\n2. Inspecting the first 5 rows of the loaded data:")
    # Use the .head() method to display the first 5 rows of the DataFrame.
    print(results_df.head())

    # Create a list of column names that contain scores, excluding the 'dataset' identifier column.
    metric_columns = [col for col in results_df.columns if col != 'dataset']
    # Print the number of metric columns that were identified.
    print(f"\n3. Identified {len(metric_columns)} metric columns to analyze.")

    # Print a header for the statistics calculation step.
    print("\n4. Calculating Mean and Standard Deviation for each metric...")
    # Initialize a dictionary to store the summary statistics.
    summary_stats = {
        'Metric': [],
        'Mean': [],
        'Standard Deviation': []
    }

    # Loop through each identified metric column.
    for metric in metric_columns:
        # Extract the Series (column) of scores for the current metric.
        scores = results_df[metric]
        # Calculate the mean of the scores using NumPy.
        mean_score = np.mean(scores)
        # Calculate the standard deviation of the scores using NumPy.
        std_dev_score = np.std(scores)
        # Append the metric name to the 'Metric' list in the dictionary.
        summary_stats['Metric'].append(metric)
        # Append the calculated mean to the 'Mean' list.
        summary_stats['Mean'].append(mean_score)
        # Append the calculated standard deviation to the 'Standard Deviation' list.
        summary_stats['Standard Deviation'].append(std_dev_score)

    # Print a header for the final summary table generation.
    print("\n5. Generating final summary table...")
    # Create a new pandas DataFrame from the summary statistics dictionary.
    summary_df = pd.DataFrame(summary_stats)
    # Set the 'Metric' column as the DataFrame's index for better readability.
    summary_df.set_index('Metric', inplace=True)

    # Print a formatted header and the final summary table for the current tool.
    print(f"\n--- ODB Benchmark - Final Aggregate Results for [{tool_name}] ---")
    print(summary_df)
    print("----------------------------------------------------------")

    # Define the name of the output file for the final summary.
    output_summary_csv_file = f"{tool_name}_final_summary.csv"
    # Print a message indicating that the summary table is being saved.
    print(f"\n6. Saving final summary table to '{output_summary_csv_file}'...")
    try:
        # Use the .to_csv() method to write the DataFrame to a CSV file.
        # `index=True` ensures the 'Metric' index is included in the CSV.
        summary_df.to_csv(output_summary_csv_file, index=True)
        # Print a success message upon successful saving.
        print("   [SUCCESS] Final summary table successfully saved.")
    # Catch any exceptions that might occur during the file writing process.
    except Exception as e:
        # Print an error message with the specific error.
        print(f"   [ERROR] Could not write to summary CSV file. Error: {e}")

# Print a final message indicating the end of the entire script.
print("\n\n--- [END] ODB Multi-Tool Analysis ---")
