# -----------------------------------------------------------------------------
# Script: 8_odb_discovery_fidelity_plot.py
# Author: Vijayaraj Nagarajan PhD
# Assistant: Google Gemini
#
# Objective:
# To generate the "Discovery vs. Fidelity" quadrant plot, visualizing the
# analytical profile of each tool. It calculates two meta-scores ('Fidelity'
# and 'Discovery & Synthesis') for each tool by averaging specific groups of
# primary metrics and plots them on a 2D scatter plot with labeled quadrants.
#
# Inputs:
#   - `<tool_name>_average_scores.csv` (for each tool in the `TOOLS` dictionary)
#
# Outputs:
#   - `ODB_DISCOVERY_VS_FIDELITY_QUADRANT.png`: A PNG image file of the
#     final quadrant plot.
# -----------------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

# Defines the name for the output plot image file.
OUTPUT_FIGURE_FILE = "ODB_DISCOVERY_VS_FIDELITY_QUADRANT.png"

# Defines which metrics contribute to the "Fidelity" score (precision, recall, etc.).
FIDELITY_METRICS = [
    'hub_gene_ndcg',
    'enrichment_fidelity_jaccard',
    'analogous_systems_jaccard',
    'publication_title_cosine'
]

# Defines which metrics contribute to the "Discovery & Synthesis" score (reasoning, structure, etc.).
DISCOVERY_METRICS = [
    'system_model_jaccard',
    'hub_gene_annotation_f1',
    'regulatory_network_mrr',
    'enrichment_categorization_jaccard',
    'biological_synthesis_cosine',
    'hypotheses_semantic',
    'novel_insights_semantic',
    'component_summaries_cosine'
]

# Print the starting message for the plot generation script.
print("--- [START] Discovery vs. Fidelity Quadrant Plot Generation ---")
# Print a message indicating the configuration has been loaded.
print("1. Loaded meta-score configurations.\n")

# Print a message indicating the start of meta-score calculation.
print(f"2. Calculating meta-scores for {len(TOOLS)} tools...")
# Initialize an empty list to store the data for plotting.
plot_data = []

# Loop through each tool to calculate its scores.
for tool_label, tool_folder_name in TOOLS.items():
    # Construct the path to the tool's average scores file.
    tool_avg_scores_file = f"{tool_folder_name}_average_scores.csv"
    
    # Use a try-except block to handle file loading errors.
    try:
        # Read the average scores CSV into a pandas DataFrame.
        tool_df = pd.read_csv(tool_avg_scores_file)
        
        # Create a list of scores for fidelity metrics that exist in the DataFrame.
        fidelity_scores = [tool_df[metric].iloc[0] for metric in FIDELITY_METRICS if metric in tool_df.columns]
        # Calculate the mean of the fidelity scores.
        avg_fidelity = np.mean(fidelity_scores) if fidelity_scores else 0
        
        # Create a list of scores for discovery metrics that exist in the DataFrame.
        discovery_scores = [tool_df[metric].iloc[0] for metric in DISCOVERY_METRICS if metric in tool_df.columns]
        # Calculate the mean of the discovery scores.
        avg_discovery = np.mean(discovery_scores) if discovery_scores else 0

        # Print the calculated scores for the current tool.
        print(f"   - {tool_label}: Fidelity = {avg_fidelity:.4f}, Discovery = {avg_discovery:.4f}")
        
        # Append the results as a dictionary to the plot_data list.
        plot_data.append({
            "Tool": tool_label,
            "Fidelity Score": avg_fidelity,
            "Discovery & Synthesis Score": avg_discovery
        })

    # Handle cases where the score file for a tool is not found.
    except FileNotFoundError:
        print(f"   [ERROR] Scores file not found for {tool_label}. Skipping.")
    # Handle any other exceptions during score processing.
    except Exception as e:
        print(f"   [ERROR] Failed to process scores for {tool_label}: {e}. Skipping.")

# Convert the list of dictionaries into a pandas DataFrame for easier plotting.
plot_df = pd.DataFrame(plot_data)

# Print a message indicating the start of plot generation.
print("\n3. Generating the quadrant plot...")

# Set the visual style of the plot to "whitegrid".
sns.set_style("whitegrid")
# Create a new figure with a specified size.
plt.figure(figsize=(10, 10))

# Create the scatter plot using seaborn.
scatterplot = sns.scatterplot(
    data=plot_df, # The DataFrame containing the data.
    x="Fidelity Score", # The variable for the x-axis.
    y="Discovery & Synthesis Score", # The variable for the y-axis.
    hue="Tool", # Color the points based on the 'Tool' column.
    s=150,      # Set the size of the markers.
    palette="viridis", # Use the "viridis" color palette.
    style="Tool", # Use different marker styles for each tool.
    markers=True # Ensure markers are drawn.
)

# Loop through each row of the DataFrame to add text labels to the points.
for i in range(plot_df.shape[0]):
    # Add the tool's name as a text label slightly offset from the point.
    plt.text(plot_df['Fidelity Score'][i] + 0.005,
             plot_df['Discovery & Synthesis Score'][i],
             plot_df['Tool'][i],
             fontdict={'size': 9})

# Calculate the mean of the scores to define the center of the quadrants.
x_mid = plot_df['Fidelity Score'].mean()
y_mid = plot_df['Discovery & Synthesis Score'].mean()

# Draw a vertical dashed line at the x-midpoint.
plt.axvline(x_mid, color='grey', linestyle='--', lw=1)
# Draw a horizontal dashed line at the y-midpoint.
plt.axhline(y_mid, color='grey', linestyle='--', lw=1)

# Add text labels to describe each of the four quadrants.
plt.text(x_mid - 0.01, y_mid - 0.01, "Low Discovery\nLow Fidelity", ha='right', va='top', fontsize=10, color='grey', alpha=0.8)
plt.text(x_mid + 0.01, y_mid - 0.01, "Low Discovery\nHigh Fidelity\n(Precise Librarian)", ha='left', va='top', fontsize=10, color='grey', alpha=0.8)
plt.text(x_mid - 0.01, y_mid + 0.01, "High Discovery\nLow Fidelity\n(Creative Explorer)", ha='right', va='bottom', fontsize=10, color='grey', alpha=0.8)
plt.text(x_mid + 0.01, y_mid + 0.01, "High Discovery\nHigh Fidelity\n(Ideal Bio-Interpreter)", ha='left', va='bottom', fontsize=10, color='grey', alpha=0.8)

# Set the main title and axis labels for the plot with specified font sizes.
plt.title('ODB Benchmark: Tool Performance Profile', fontsize=16)
plt.xlabel('Fidelity Score (Precision & Recall)', fontsize=12)
plt.ylabel('Discovery & Synthesis Score (Reasoning & Structure)', fontsize=12)

# Move the legend outside of the main plot area to avoid overlap.
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

# Adjust the plot layout to ensure all elements, including the legend, fit neatly.
plt.tight_layout(rect=[0, 0, 0.85, 1])

# Print a message indicating that the plot is being saved.
print(f"\n4. Saving quadrant plot to '{OUTPUT_FIGURE_FILE}'...")
# Save the figure to a file with 300 DPI for high quality.
plt.savefig(OUTPUT_FIGURE_FILE, dpi=300)
# Print a success message.
print("   [SUCCESS] Figure saved.")

# Display the plot in the current environment (e.g., a Jupyter notebook or a new window).
plt.show()

# Print the final message indicating the end of the script.
print("\n--- [END] Quadrant Plot Generation ---")
