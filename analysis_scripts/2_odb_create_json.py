# -----------------------------------------------------------------------------
# Script: 2_odb_create_json.py
# Author: Vijayaraj Nagarajan PhD
# Assistant: Google Gemini
#
# Objective:
# This script acts as a parser to convert a tool's raw text and JSON outputs
# into the standardized `odb_tool_output.json` format required for benchmarking.
# It iterates through each dataset subfolder within a specified tool's output
# directory, reads the 12 individual output files (e.g., `title.txt`,
# `hub_genes_ranked.txt`, `regulatory_edges.json`), and consolidates them
# into a single, structured JSON file.
#
# Inputs:
#   - Reads files from a tool-specific directory, e.g., `tools_outputs/ian_outputs/`.
#   - For each dataset ID (e.g., 'BC', 'PAD'), it reads 12 files:
#     - `title.txt`, `synthesis.txt`, `hub_genes_ranked.txt`, etc.
#     - `regulatory_edges.json`, `system_model.json`, etc.
#
# Outputs:
#   - For each dataset ID, it generates one file in the same directory:
#     - `tools_outputs/<tool_name>/<ID>/odb_tool_output.json`
# -----------------------------------------------------------------------------

import os
import json
import sys

# This is the only part you need to edit.
# Set the name of the tool output folder you want to process.
tool_name = 'ian_outputs'

# This part constructs the path and checks if it exists.
# Construct the relative path to the main tool directory from the 'tools_outputs' folder.
main_tool_dir = os.path.join('tools_outputs', tool_name)

# Print a header to indicate the start of the script.
print(f"\n=== Starting ODB Parser ===")
# Print the target directory that will be processed.
print(f"Targeting tool directory: '{main_tool_dir}'")

# Verify that the main tool directory exists before proceeding.
if not os.path.isdir(main_tool_dir):
    # If the directory doesn't exist, print an error message.
    print(f"\nError: Main tool directory not found at '{main_tool_dir}'")
    print("Please make sure the folder exists and the 'tool_name' in Step 1 is correct.")
    # Exit the script with an error code.
    sys.exit(1)
# If the directory is found.
else:
    # Print a confirmation message.
    print("Directory found. Proceeding to the main loop...")

# This is the core of the script. It iterates through each dataset subfolder
# and performs all parsing actions directly inside the loop.
try:
    # Get a sorted list of all items in the tool directory to ensure consistent processing order.
    dataset_subfolders = sorted(os.listdir(main_tool_dir))

    # Loop through each item found in the tool directory.
    for dataset_id in dataset_subfolders:
        # Construct the full path to the specific dataset's subfolder.
        dataset_dir = os.path.join(main_tool_dir, dataset_id)

        # Skip any item that is not a directory (e.g., system files like .DS_Store).
        if not os.path.isdir(dataset_dir):
            continue

        # Print a header indicating which dataset is being parsed.
        print(f"\n--- Parsing Dataset Output from: {dataset_dir} ---")

        # Initialize an empty dictionary to hold the parsed data for the current dataset.
        odb_output = {}

        # Construct the full path to the 'title.txt' file.
        title_path = os.path.join(dataset_dir, "title.txt")
        # Check if the title file exists.
        if os.path.exists(title_path):
            # Open the file with UTF-8 encoding.
            with open(title_path, 'r', encoding='utf-8') as f:
                # Read all lines, stripping whitespace, and filter out empty lines.
                lines = [line.strip() for line in f if line.strip()]
                # Assign the first line to the "publication_title" key, or an empty string if the file is empty.
                odb_output["publication_title"] = lines[0] if lines else ""
        else:
            # If the file doesn't exist, assign an empty string.
            odb_output["publication_title"] = ""

        # Construct the path to the 'synthesis.txt' file.
        synthesis_path = os.path.join(dataset_dir, "synthesis.txt")
        # Check if the synthesis file exists.
        if os.path.exists(synthesis_path):
            # Open the file.
            with open(synthesis_path, 'r', encoding='utf-8') as f:
                # Read the file content, strip whitespace, and store it in a nested dictionary.
                odb_output["biological_process_synthesis"] = {"text": f.read().strip()}
        else:
            # If the file is not found, create the nested dictionary with an empty text value.
            odb_output["biological_process_synthesis"] = {"text": ""}

        # Construct the path to the 'hub_genes_ranked.txt' file.
        hub_genes_path = os.path.join(dataset_dir, "hub_genes_ranked.txt")
        # Check if the file exists.
        if os.path.exists(hub_genes_path):
            # Open the file.
            with open(hub_genes_path, 'r', encoding='utf-8') as f:
                # Read each line, strip whitespace, filter out empty lines, and store as a list in a nested dictionary.
                odb_output["hub_genes_ranked"] = {"genes": [line.strip() for line in f if line.strip()]}
        else:
            # If not found, create a nested dictionary with an empty list of genes.
            odb_output["hub_genes_ranked"] = {"genes": []}
            
        # Construct the path to the 'enriched_pathways.txt' file.
        enriched_pathways_path = os.path.join(dataset_dir, "enriched_pathways.txt")
        # Check if the file exists.
        if os.path.exists(enriched_pathways_path):
            # Open the file.
            with open(enriched_pathways_path, 'r', encoding='utf-8') as f:
                # Read each line, strip whitespace, filter out empty lines, and store as a list of terms.
                odb_output["enriched_pathways"] = {"terms": [line.strip() for line in f if line.strip()]}
        else:
            # If not found, create a nested dictionary with an empty list of terms.
            odb_output["enriched_pathways"] = {"terms": []}

        # Construct the path to the 'hypotheses.txt' file.
        hypotheses_path = os.path.join(dataset_dir, "hypotheses.txt")
        # Check if the file exists.
        if os.path.exists(hypotheses_path):
            # Open the file.
            with open(hypotheses_path, 'r', encoding='utf-8') as f:
                 # Read each line, strip whitespace, filter out empty lines, and store as a list of statements.
                 odb_output["hypotheses"] = {"statements": [line.strip() for line in f if line.strip()]}
        else:
            # If not found, create a nested dictionary with an empty list of statements.
            odb_output["hypotheses"] = {"statements": []}

        # Construct the path to the 'novel_insights.txt' file.
        novel_insights_path = os.path.join(dataset_dir, "novel_insights.txt")
        # Check if the file exists.
        if os.path.exists(novel_insights_path):
            # Open the file.
            with open(novel_insights_path, 'r', encoding='utf-8') as f:
                # Read each line, strip whitespace, filter out empty lines, and store as a list of statements.
                odb_output["novel_insights"] = {"statements": [line.strip() for line in f if line.strip()]}
        else:
            # If not found, create a nested dictionary with an empty list of statements.
            odb_output["novel_insights"] = {"statements": []}
            
        # Construct the path to the 'analogous_systems.txt' file.
        analogous_systems_path = os.path.join(dataset_dir, "analogous_systems.txt")
        # Check if the file exists.
        if os.path.exists(analogous_systems_path):
            # Open the file.
            with open(analogous_systems_path, 'r', encoding='utf-8') as f:
                # Read each line, strip whitespace, filter out empty lines, and store as a list of systems.
                odb_output["analogous_systems"] = {"systems": [line.strip() for line in f if line.strip()]}
        else:
            # If not found, create a nested dictionary with an empty list of systems.
            odb_output["analogous_systems"] = {"systems": []}
        
        # Construct the path to the regulatory edges JSON file.
        reg_edges_path = os.path.join(dataset_dir, "regulatory_edges.json")
        # Check if the file exists.
        if os.path.exists(reg_edges_path):
            try:
                # Open the file.
                with open(reg_edges_path, 'r', encoding='utf-8') as f:
                    # Load the JSON content directly into the output dictionary.
                    odb_output["regulatory_network_edges"] = json.load(f)
            # If the file is not valid JSON.
            except json.JSONDecodeError:
                # Assign an empty dictionary as a fallback.
                odb_output["regulatory_network_edges"] = {}
        else:
            # If the file does not exist, assign an empty dictionary.
            odb_output["regulatory_network_edges"] = {}

        # Construct the path to the system model JSON file.
        system_model_path = os.path.join(dataset_dir, "system_model.json")
        # Check if the file exists.
        if os.path.exists(system_model_path):
            try:
                # Open and load the JSON file.
                with open(system_model_path, 'r', encoding='utf-8') as f:
                    odb_output["integrated_system_nodes"] = json.load(f)
            # If the JSON is malformed.
            except json.JSONDecodeError:
                # Assign an empty dictionary.
                odb_output["integrated_system_nodes"] = {}
        else:
            # If the file is not found, assign an empty dictionary.
            odb_output["integrated_system_nodes"] = {}

        # Construct the path to the enrichment categorization JSON file.
        enrich_cat_path = os.path.join(dataset_dir, "enrichment_categorization.json")
        # Check if the file exists.
        if os.path.exists(enrich_cat_path):
            try:
                # Open and load the JSON file.
                with open(enrich_cat_path, 'r', encoding='utf-8') as f:
                    odb_output["enrichment_categorization"] = json.load(f)
            # If the JSON is malformed.
            except json.JSONDecodeError:
                # Assign an empty dictionary.
                odb_output["enrichment_categorization"] = {}
        else:
            # If the file is not found, assign an empty dictionary.
            odb_output["enrichment_categorization"] = {}

        # Construct the path to the hub gene annotation JSON file.
        hub_anno_path = os.path.join(dataset_dir, "hub_gene_annotation.json")
        # Check if the file exists.
        if os.path.exists(hub_anno_path):
            try:
                # Open and load the JSON file.
                with open(hub_anno_path, 'r', encoding='utf-8') as f:
                    odb_output["hub_gene_annotation"] = json.load(f)
            # If the JSON is malformed.
            except json.JSONDecodeError:
                # Assign an empty dictionary.
                odb_output["hub_gene_annotation"] = {}
        else:
            # If the file is not found, assign an empty dictionary.
            odb_output["hub_gene_annotation"] = {}
            
        # Construct the path to the component summaries JSON file.
        comp_summ_path = os.path.join(dataset_dir, "component_summaries.json")
        # Check if the file exists.
        if os.path.exists(comp_summ_path):
            try:
                # Open and load the JSON file.
                with open(comp_summ_path, 'r', encoding='utf-8') as f:
                    odb_output["component_summaries"] = json.load(f)
            # If the JSON is malformed.
            except json.JSONDecodeError:
                # Assign an empty dictionary.
                odb_output["component_summaries"] = {}
        else:
            # If the file is not found, assign an empty dictionary.
            odb_output["component_summaries"] = {}

        # Define the name of the final consolidated output file.
        output_filename = "odb_tool_output.json"
        # Construct the full path for the output file in the current dataset directory.
        output_filepath = os.path.join(dataset_dir, output_filename)

        # Open the output file in write mode.
        with open(output_filepath, 'w') as f:
            # Write the assembled dictionary to the JSON file with an indent of 4 for readability.
            json.dump(odb_output, f, indent=4)
            
        # Print a success message for the current dataset.
        print(f"  -> Successfully generated '{output_filename}'")

    # Print a final message indicating completion for the entire tool directory.
    print(f"\n=== ODB Parsing Complete for all datasets in '{main_tool_dir}' ===")

# Catch an error if 'main_tool_dir' was not defined (e.g., if code is run out of order).
except NameError:
    print("\nERROR: 'main_tool_dir' was not defined. Please run Step 3 first.")
# Catch an error if the specified tool directory does not exist.
except FileNotFoundError:
    print(f"\nERROR: The directory '{main_tool_dir}' does not exist. Please check the 'tool_name' variable.")
