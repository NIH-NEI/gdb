# -----------------------------------------------------------------------------
# Script: 3_odb_validate_io.py
# Author: Vijayaraj Nagarajan PhD
# Assistant: Google Gemini
#
# Objective:
# To automatically validate that all required input files for the benchmark
# are present and correctly structured before running the main scoring script.
# For a specified tool, it discovers all datasets and checks for the existence
# and integrity of both the ground truth and the tool's output JSON file,
# ensuring they are valid JSON and contain all 12 mandatory keys.
#
# Inputs:
#   - `ODB/groundtruthdatasets/<ID>/ground_truth.json` (for all discovered datasets)
#   - `tools_outputs/<tool_name>/<ID>/odb_tool_output.json` (for all discovered datasets)
#
# Outputs:
#   - This script does not generate files. It prints its validation results
#     (success or failure with detailed logs) directly to the console.
# -----------------------------------------------------------------------------

import json
import os

# Set the single parameter for the validation run.
# The name of the tool output directory we are evaluating.
# This corresponds to a subfolder within 'tools_outputs/'.
TOOL_NAME = "ian_outputs"

# These paths are based on the official project directory structure.
# The base directory where the ODB ground truth datasets are located.
GROUND_TRUTH_BASE_DIR = "ODB/groundtruthdatasets"
# The base directory for all standardized tool outputs.
TOOL_OUTPUTS_DIR = "tools_outputs"

# Print a header indicating the start of the validation script.
print("--- [START] ODB Automated Input File Validation ---")
# Print the tool being validated.
print(f"Configuration: Validating all datasets for Tool '{TOOL_NAME}'\n")

# The 12 mandatory keys that MUST exist in both the ground truth and tool output JSON files.
EXPECTED_KEYS = [
    "hub_genes_ranked",
    "enriched_pathways",
    "enrichment_categorization",
    "regulatory_network_edges",
    "biological_process_synthesis",
    "hypotheses",
    "novel_insights",
    "analogous_systems",
    "publication_title",
    "integrated_system_nodes",
    "hub_gene_annotation",
    "component_summaries"
]

# Automatically find all dataset directories inside the ground truth folder.
try:
    # List all items in the ground truth base directory.
    all_dirs = os.listdir(GROUND_TRUTH_BASE_DIR)
    # Filter the list to include only directories, creating a list of dataset IDs.
    dataset_ids = [d for d in all_dirs if os.path.isdir(os.path.join(GROUND_TRUTH_BASE_DIR, d))]
    
    # Check if any dataset directories were found.
    if not dataset_ids:
        # If not, print an error and exit the script.
        print(f"[ERROR] No dataset directories found in '{GROUND_TRUTH_BASE_DIR}'. Please check your directory structure.")
        exit()

    # Print the number of discovered datasets and their names.
    print(f"1. Discovered {len(dataset_ids)} potential datasets: {dataset_ids}\n")
    # Print a separator line.
    print("=" * 60)

# Handle the case where the ground truth directory itself is not found.
except FileNotFoundError:
    # Print a fatal error message with the expected path.
    print(f"[FATAL ERROR] Ground truth directory not found at: '{GROUND_TRUTH_BASE_DIR}'")
    print("Please ensure you are running this script from the 'My_ODB_Project/' root directory.")
    # Exit the script.
    exit()

# Initialize a flag to track the overall success of the validation.
overall_success = True
# Iterate through each discovered dataset ID.
for dataset_id in dataset_ids:
    # Print a header for the current dataset.
    print(f"\nProcessing Dataset: [{dataset_id}]")
    # Print a separator line.
    print("-" * 30)

    # Construct the full file paths for the ground truth and tool output JSONs for the current dataset.
    ground_truth_path = os.path.join(GROUND_TRUTH_BASE_DIR, dataset_id, "ground_truth.json")
    tool_output_path = os.path.join(TOOL_OUTPUTS_DIR, TOOL_NAME, dataset_id, "odb_tool_output.json")

    # Print the path of the ground truth file being validated.
    print(f"2. Validating ground truth file: {ground_truth_path}")
    # Initialize a flag for the validity of the ground truth file.
    is_ground_truth_valid = False
    # Check if the ground truth file exists.
    if not os.path.exists(ground_truth_path):
        # If not, print a failure message.
        print("   [FAIL] File not found.")
    else:
        # If it exists, print a success message.
        print("   [OK] File found.")
        try:
            # Open the file in read mode.
            with open(ground_truth_path, 'r') as f:
                # Attempt to load the file as JSON.
                ground_truth_data = json.load(f)
            # If successful, print a success message.
            print("   [OK] File is a valid JSON document.")
            
            # Check for any missing keys from the expected list.
            missing_keys = [key for key in EXPECTED_KEYS if key not in ground_truth_data]
            # If there are no missing keys.
            if not missing_keys:
                # Print a success message and set the validity flag to True.
                print("   [OK] All 12 required keys are present.")
                is_ground_truth_valid = True
            else:
                # If keys are missing, print a failure message with the list of missing keys.
                print(f"   [FAIL] Missing keys: {missing_keys}")
        # Catch errors if the file is not valid JSON.
        except json.JSONDecodeError:
            print("   [FAIL] File is not a valid JSON.")
        # Catch any other unexpected errors during file processing.
        except Exception as e:
            print(f"   [FAIL] An unexpected error occurred: {e}")
    
    # Print the path of the tool output file being validated.
    print(f"\n3. Validating tool output file: {tool_output_path}")
    # Initialize a flag for the validity of the tool output file.
    is_tool_output_valid = False
    # Check if the tool output file exists.
    if not os.path.exists(tool_output_path):
        # If not, print a failure message.
        print("   [FAIL] File not found.")
    else:
        # If it exists, print a success message.
        print("   [OK] File found.")
        try:
            # Open and attempt to load the file as JSON.
            with open(tool_output_path, 'r') as f:
                tool_output_data = json.load(f)
            # If successful, print a success message.
            print("   [OK] File is a valid JSON document.")
            
            # Check for any missing keys.
            missing_keys = [key for key in EXPECTED_KEYS if key not in tool_output_data]
            # If no keys are missing.
            if not missing_keys:
                # Print a success message and set the validity flag to True.
                print("   [OK] All 12 required keys are present.")
                is_tool_output_valid = True
            else:
                # If keys are missing, print a failure message with the list of missing keys.
                print(f"   [FAIL] Missing keys: {missing_keys}")
        # Catch JSON decoding errors.
        except json.JSONDecodeError:
            print("   [FAIL] File is not a valid JSON.")
        # Catch any other unexpected errors.
        except Exception as e:
            print(f"   [FAIL] An unexpected error occurred: {e}")

    # Check if both the ground truth and tool output files for the dataset are valid.
    if is_ground_truth_valid and is_tool_output_valid:
        # If both are valid, print a success status for the dataset.
        print(f"\n   >>> STATUS for [{dataset_id}]: SUCCESS <<<")
    else:
        # If either is invalid, print a failure status.
        print(f"\n   >>> STATUS for [{dataset_id}]: FAILED <<<")
        # Set the overall success flag to False, as at least one dataset has failed.
        overall_success = False
    
    # Print a separator line.
    print("=" * 60)

# Print a final summary header.
print("\n--- Overall Validation Summary ---")
# Check the final status of the overall success flag.
if overall_success:
    # If all datasets passed, print a success message.
    print("[SUCCESS] All discovered datasets and their corresponding tool outputs are valid and correctly structured.")
    print("Ready to proceed to the scoring phase.")
else:
    # If any dataset failed, print a failure message, prompting the user to review the logs.
    print("[FAILURE] One or more datasets failed validation. Please review the logs above and correct the files or directory structure before proceeding.")

# Print a final message indicating the end of the script.
print("\n--- [END] ODB Automated Input File Validation ---")
