# -----------------------------------------------------------------------------
# Script: 7_odb-final-score.py
# Author: Vijayaraj Nagarajan PhD
# Assistant: Google Gemini
#
# Objective:
# To rank all benchmarked tools based on a final, composite "Groundedness-Weighted"
# score. This script applies a predefined set of weights to the primary metrics
# for each task, calculates a single weighted score for each tool, and then
# generates a final, sorted ranking table.
#
# Inputs:
#   - `<tool_name>_average_scores.csv` (for each tool in the `TOOLS` dictionary)
#
# Outputs:
#   - `ODB_FINAL_USER_WEIGHTED_RANKING_TABLE.csv`: A single CSV file containing
#     the final ranked list of tools and their composite scores.
# -----------------------------------------------------------------------------

import pandas as pd
import numpy as np
import os

# Defines the mapping between user-friendly tool labels and their folder names.
TOOLS = {
    "Gemini (DEG Only)": "gemini_2_5_pro_gex",
    "Gemini (DEG + Exp)": "gemini_2_5_pro_gex_exp",
    "ChatGPT (DEG Only)": "chatgpt_gex",
    "ChatGPT (DEG + Exp)": "chatgpt_gex_exp",
    "Claude (DEG Only)": "claude_gex",
    "Claude (DEG + Exp)": "claude_gex_exp",
    "IAN": "ian_outputs"
}
# Defines the name for the final output CSV file.
FINAL_OUTPUT_CSV = "ODB_FINAL_USER_WEIGHTED_RANKING_TABLE.csv"

# These weights are derived and normalized from a specific user proposal, prioritizing grounded tasks.
FINAL_WEIGHTS = {
    'System Model': 0.155,
    'Hub Gene Annotation': 0.116,
    'Regulatory Network': 0.116,
    'Enrichment Categorization': 0.116,
    'Hub Gene Identification': 0.116,
    'Biological Synthesis': 0.116,
    'Hypothesis Generation': 0.039,
    'Novel Insight ID': 0.039,
    'Component Summaries': 0.031,
    'Analogous Systems': 0.023,
    'Publication Title': 0.016,
    'Enrichment Fidelity': 0.0 # This task is explicitly given a weight of zero.
}

# This dictionary maps each analysis task to its specific primary scoring metric column name.
PRIMARY_METRICS_FINAL = {
    'Hub Gene Identification': 'hub_gene_ndcg',
    'Enrichment Fidelity': 'enrichment_fidelity_jaccard',
    'Enrichment Categorization': 'enrichment_categorization_jaccard',
    'Regulatory Network': 'regulatory_network_mrr',
    'Biological Synthesis': 'biological_synthesis_cosine',
    'Hypothesis Generation': 'hypotheses_semantic',
    'Novel Insight ID': 'novel_insights_semantic',
    'Analogous Systems': 'analogous_systems_jaccard',
    'Publication Title': 'publication_title_cosine',
    'System Model': 'system_model_jaccard',
    'Hub Gene Annotation': 'hub_gene_annotation_f1',
    'Component Summaries': 'component_summaries_cosine'
}

# Print the starting message for the analysis.
print("--- [START] Final User-Weighted Ranking Analysis ---")
# Print a message indicating the scoring model has been defined.
print("1. Loaded final user-defined 'groundedness' scoring model.\n")

# Print a message indicating the start of score calculation for all tools.
print(f"2. Calculating final scores for {len(TOOLS)} tools...")
# Initialize an empty list to store the results for each tool.
final_results = []

# Loop through each tool defined in the TOOLS dictionary.
for tool_label, tool_folder_name in TOOLS.items():
    # Construct the filename for the tool's average scores CSV.
    tool_avg_scores_file = f"{tool_folder_name}_average_scores.csv"
    # Initialize the weighted score for the current tool.
    weighted_score = 0.0
    
    # Use a try-except block to handle file loading and processing errors.
    try:
        # Read the tool's average scores into a pandas DataFrame.
        tool_df = pd.read_csv(tool_avg_scores_file)
        
        # Iterate through each task and its corresponding metric.
        for task, metric in PRIMARY_METRICS_FINAL.items():
            # Get the weight for the current task from the FINAL_WEIGHTS dictionary, defaulting to 0.
            weight = FINAL_WEIGHTS.get(task, 0)
            # Check if the metric column exists in the tool's DataFrame.
            if metric in tool_df.columns:
                # Get the score from the first row of the metric's column.
                score = tool_df[metric].iloc[0]
                # Add the product of the score and its weight to the total weighted score.
                weighted_score += score * weight
            else:
                # Print a warning if a specific metric is not found for the tool.
                print(f"   [WARNING] Metric '{metric}' not found for tool '{tool_folder_name}'.")

        # Print the calculated final score for the current tool.
        print(f"   - Calculated Final Score for {tool_label}: {weighted_score:.4f}")
        
        # Append the tool's label and final score to the results list.
        final_results.append({
            "Tool": tool_label,
            "Final Grounded Score": weighted_score
        })

    # Handle the case where the scores file is not found.
    except FileNotFoundError:
        print(f"   [ERROR] Scores file '{tool_avg_scores_file}' not found. Score will be 0.")
        # Append a result with a score of 0.
        final_results.append({ "Tool": tool_label, "Final Grounded Score": 0 })
    # Handle any other exceptions during the process.
    except Exception as e:
        print(f"   [ERROR] Failed to process scores for {tool_label}: {e}. Score will be 0.")
        # Append a result with a score of 0.
        final_results.append({ "Tool": tool_label, "Final Grounded Score": 0 })

# Print a message indicating the final table is being assembled.
print("\n3. Assembling the final ranking table...")
# Create a DataFrame from the list of final results.
final_ranking_df = pd.DataFrame(final_results)
# Sort the DataFrame by the 'Final Grounded Score' in descending order.
final_ranking_df.sort_values(by="Final Grounded Score", ascending=False, inplace=True)
# Reset the DataFrame index after sorting.
final_ranking_df.reset_index(drop=True, inplace=True)

# Print a formatted header for the final ranking table.
print("\n" + "="*60)
print("--- ODB BENCHMARK - FINAL USER-WEIGHTED RANKING ---")
print("="*60)
# Print the entire DataFrame as a string without the index.
print(final_ranking_df.to_string(index=False))
print("="*60)

# Print a message indicating the table is being saved to a CSV file.
print(f"\n4. Saving final ranking table to '{FINAL_OUTPUT_CSV}'...")
try:
    # Save the final ranking DataFrame to a CSV file, without the index.
    final_ranking_df.to_csv(FINAL_OUTPUT_CSV, index=False)
    # Print a success message.
    print("   [SUCCESS] Final ranking table successfully saved.")
except Exception as e:
    # Print an error message if saving fails.
    print(f"   [ERROR] Could not write to final CSV file. Error: {e}")

# Print the final message indicating the end of the analysis.
print("\n--- [END] Final User-Weighted Ranking Analysis ---")
