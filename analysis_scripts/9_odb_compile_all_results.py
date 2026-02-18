# -----------------------------------------------------------------------------
# Script: 9_odb_compile_all_results.py
# Author: Vijayaraj Nagarajan PhD
# Assistant: Google Gemini
#
# Objective:
# To compile the detailed, per-dataset benchmark results from all individual
# tool output files into a single, master CSV file. This creates a "long format"
# tidy dataset, which is useful for comprehensive cross-tool analysis and
# plotting in other software (e.g., R, Tableau).
#
# Inputs:
#   - `<tool_name>_benchmark_results.csv` (for each tool in the `TOOLS` dictionary)
#
# Outputs:
#   - `MASTER_ALL_SCORES.csv`: A single CSV file containing all scores from all
#     tools, with an added 'Tool' column to identify the source of each row.
# -----------------------------------------------------------------------------

import pandas as pd
import os

# Defines a dictionary mapping user-friendly tool labels to their corresponding file prefixes.
TOOLS = {
    "Gemini (DEG Only)": "gemini_2_5_pro_gex",
    "Gemini (DEG + Exp)": "gemini_2_5_pro_gex_exp",
    "ChatGPT (DEG Only)": "chatgpt_gex",
    "ChatGPT (DEG + Exp)": "chatgpt_gex_exp",
    "Claude (DEG Only)": "claude_gex",
    "Claude (DEG + Exp)": "claude_gex_exp",
    "IAN": "ian_outputs"
}

# Initializes an empty list to hold the DataFrames for each tool.
all_dfs = []
# Prints a starting message to the console.
print("--- Starting to Compile All Tool Results ---")
# Iterates through the TOOLS dictionary to process each tool.
for tool_label, tool_folder in TOOLS.items():
    # Constructs the expected file path for the tool's benchmark results CSV.
    file_path = f"{tool_folder}_benchmark_results.csv"
    # Uses a try-except block to handle cases where a file might not exist.
    try:
        # Reads the CSV file into a pandas DataFrame.
        df = pd.read_csv(file_path)
        # Adds a new column 'Tool' to the DataFrame to identify the data source.
        df['Tool'] = tool_label
        # Appends the newly created DataFrame to the 'all_dfs' list.
        all_dfs.append(df)
        # Prints a success message indicating the file was loaded.
        print(f"  - Successfully loaded and tagged: {file_path}")
    # Catches the FileNotFoundError if the CSV does not exist.
    except FileNotFoundError:
        # Prints a warning message that the file was not found and is being skipped.
        print(f"  [WARNING] File not found, skipping: {file_path}")

# Checks if the 'all_dfs' list is not empty (i.e., if at least one file was loaded).
if all_dfs:
    # Concatenates all DataFrames in the list into a single master DataFrame.
    master_df = pd.concat(all_dfs, ignore_index=True)
    # Saves the master DataFrame to a new CSV file named 'MASTER_ALL_SCORES.csv'.
    master_df.to_csv("MASTER_ALL_SCORES.csv", index=False)
    # Prints a success message indicating the master file has been created.
    print("\n[SUCCESS] Master data file 'MASTER_ALL_SCORES.csv' created.")
# Executes if no data files were found.
else:
    # Prints an error message.
    print("\n[ERROR] No data files found. Cannot create master file.")
# Prints a final message indicating the script has finished.
print("--- Compilation Complete ---")
