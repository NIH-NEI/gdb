# -----------------------------------------------------------------------------
# Script: 4_odb_run_benchmark.py
# Author: Vijayaraj Nagarajan PhD
# Assistant: Google Gemini
#
# Objective:
# This is the main scoring engine for the ODB benchmark. It iterates through
# a list of specified tools and, for each tool, scores its performance on all
# 12 benchmark tasks across all datasets. It compares the tool's output
# (`odb_tool_output.json`) against the established ground truth
# (`ground_truth.json`) using a variety of metrics like Jaccard similarity,
# NDCG, MRR, and cosine similarity with a sentence-transformer model.
#
# Inputs:
#   - `ODB/groundtruthdatasets/<ID>/ground_truth.json` (for all datasets)
#   - `tools_outputs/<tool_name>/<ID>/odb_tool_output.json` (for all tools/datasets)
#
# Outputs:
#   - For each tool specified in `TOOL_NAMES`, it generates two CSV files:
#     - `<tool_name>_benchmark_results.csv`: Contains the detailed, per-dataset scores for all 12 tasks.
#     - `<tool_name>_average_scores.csv`: Contains the average scores for each task across all datasets.
# -----------------------------------------------------------------------------

import json
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import csv

# Define a list of tool names to be processed by the benchmark script.
TOOL_NAMES = [
    "gemini_2_5_pro_gex", 
    "gemini_2_5_pro_gex_exp", 
    "ian_outputs",
    "chatgpt_gex", 
    "chatgpt_gex_exp", 
    "claude_gex", 
    "claude_gex_exp"
]

# Print a message indicating the loading of the sentence-transformer model.
print("Loading sentence-transformer model...")
# Initialize the SentenceTransformer model for semantic similarity calculations.
SEMANTIC_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
# Print a confirmation message once the model is loaded.
print("Model loaded successfully.")

# Define the base directory for ground truth datasets.
GROUND_TRUTH_BASE_DIR = "ODB/groundtruthdatasets"
# Define the base directory for tool output files.
TOOL_OUTPUTS_DIR = "tools_outputs"
# Define the list of 12 expected keys for validation within the script.
EXPECTED_KEYS = [
    "hub_genes_ranked", "enriched_pathways", "enrichment_categorization",
    "regulatory_network_edges", "biological_process_synthesis", "hypotheses",
    "novel_insights", "analogous_systems", "publication_title",
    "integrated_system_nodes", "hub_gene_annotation", "component_summaries"
]

# Print the script's start message.
print(f"\n--- [START] ODB Final Benchmark Script ---")
# Print the configuration, showing which tools are being scored.
print(f"Configuration: Scoring all datasets for Tools: {', '.join(TOOL_NAMES)}\n")

# Discover all dataset directories automatically.
try:
    # List all items in the ground truth directory and filter for directories only.
    dataset_ids = [d for d in os.listdir(GROUND_TRUTH_BASE_DIR) if os.path.isdir(os.path.join(GROUND_TRUTH_BASE_DIR, d))]
    # Print the number and names of the discovered datasets.
    print(f"1. Discovered {len(dataset_ids)} datasets: {dataset_ids}\n")
    # Print a separator line.
    print("=" * 70)
# Handle the case where the base directory is not found.
except FileNotFoundError:
    print(f"[FATAL ERROR] Directory not found. Please run from the project root.")
    # Exit the script.
    exit()

# Main loop to iterate through each specified tool.
for tool_name in TOOL_NAMES:
    # Print a header for the current tool being processed.
    print(f"\n--- Processing Tool: [{tool_name}] ---")
    # Initialize an empty list to store the benchmark results for the current tool.
    benchmark_results = []
    
    # Loop through each discovered dataset.
    for dataset_id in dataset_ids:
        # Print a header for the current dataset.
        print(f"\nProcessing Dataset: [{dataset_id}]")
        # Print a separator line.
        print("-" * 50)

        # Validate and load the ground truth and tool output JSON files.
        try:
            # Open and load the ground truth JSON file.
            with open(os.path.join(GROUND_TRUTH_BASE_DIR, dataset_id, "ground_truth.json"), 'r') as f:
                ground_truth_data = json.load(f)
            # Open and load the corresponding tool output JSON file.
            with open(os.path.join(TOOL_OUTPUTS_DIR, tool_name, dataset_id, "odb_tool_output.json"), 'r') as f:
                tool_output_data = json.load(f)
            # If both files load successfully, print a confirmation message.
            print("   [OK] Both files are valid. Proceeding to scoring.")
        # Catch any exception during file loading (e.g., file not found, JSON error).
        except Exception as e:
            # Print a failure message with the error and skip to the next dataset.
            print(f"   [FAIL] Could not load/validate files for {dataset_id}. Error: {e}. Skipping.")
            continue

        # Initialize a dictionary to store scores for the current dataset.
        dataset_scores = {"dataset": dataset_id}
        
        # --- Task 2: Enrichment Analysis Fidelity ---
        print("\n   SCORING TASK 2: 'Enrichment Analysis Fidelity'")
        # Get pathway data safely from ground truth, handling different data structures.
        gt_pathways_data = ground_truth_data.get("enriched_pathways", {})
        tool_pathways_data = tool_output_data.get("enriched_pathways", {})
        gt_pathways = gt_pathways_data.get("terms", []) if isinstance(gt_pathways_data, dict) else gt_pathways_data
        tool_pathways = tool_pathways_data.get("terms", []) if isinstance(tool_pathways_data, dict) else tool_pathways_data
        # Create sets of lowercased, stripped pathway terms for Jaccard calculation.
        gt_set = {item.lower().strip() for item in gt_pathways if item}
        tool_set = {item.lower().strip() for item in tool_pathways if item}
        # Calculate Jaccard similarity.
        dataset_scores["enrichment_fidelity_jaccard"] = len(gt_set.intersection(tool_set)) / len(gt_set.union(tool_set)) if gt_set.union(tool_set) else 1.0
        # Calculate semantic similarity using cosine similarity on sentence embeddings.
        dataset_scores["enrichment_fidelity_semantic"] = np.mean(np.max(cosine_similarity(SEMANTIC_MODEL.encode(gt_pathways), SEMANTIC_MODEL.encode(tool_pathways)), axis=1)) if gt_pathways and tool_pathways else 0.0

        # --- Task 1: Hub Gene Identification ---
        print("\n   SCORING TASK 1: 'Hub Gene Identification'")
        # Get hub gene data safely from both sources.
        gt_hub_genes_data = ground_truth_data.get("hub_genes_ranked", {})
        tool_hub_genes_data = tool_output_data.get("hub_genes_ranked", {})
        gt_hub_genes = gt_hub_genes_data.get("genes", []) if isinstance(gt_hub_genes_data, dict) else gt_hub_genes_data
        tool_hub_genes = tool_hub_genes_data.get("genes", []) if isinstance(tool_hub_genes_data, dict) else tool_hub_genes_data
        # Create a set of ground truth genes for quick lookups.
        gt_hub_genes_set = {gene.upper().strip() for gene in gt_hub_genes if gene}
        # Create a ranked list of tool-provided genes.
        tool_hub_genes_ranked = [gene.upper().strip() for gene in tool_hub_genes if gene]
        # Initialize NDCG score.
        ndcg_score = 0.0
        # Calculate Normalized Discounted Cumulative Gain (NDCG) if lists are not empty.
        if tool_hub_genes_ranked and gt_hub_genes_set:
            k = len(tool_hub_genes_ranked)
            # Calculate DCG by summing relevance scores discounted by rank.
            dcg = sum((1 / np.log2(i + 2)) for i, gene in enumerate(tool_hub_genes_ranked) if gene in gt_hub_genes_set)
            # Calculate IDCG (ideal DCG) for normalization.
            idcg = sum((1 / np.log2(i + 2)) for i in range(min(k, len(gt_hub_genes_set))))
            # Calculate final NDCG score.
            ndcg_score = dcg / idcg if idcg > 0 else 0.0
        dataset_scores["hub_gene_ndcg"] = ndcg_score

        # --- Task 8: Analogous System Discovery ---
        print("\n   SCORING TASK 8: 'Analogous System Discovery'")
        # Get analogous systems data safely.
        gt_systems_data = ground_truth_data.get("analogous_systems", {})
        tool_systems_data = tool_output_data.get("analogous_systems", {})
        gt_systems = gt_systems_data.get("systems", []) if isinstance(gt_systems_data, dict) else gt_systems_data
        tool_systems = tool_systems_data.get("systems", []) if isinstance(tool_systems_data, dict) else tool_systems_data
        # Create sets for Jaccard calculation.
        gt_systems_set = {sys.lower().strip() for sys in gt_systems if sys}
        tool_systems_set = {sys.lower().strip() for sys in tool_systems if sys}
        # Calculate Jaccard similarity.
        dataset_scores["analogous_systems_jaccard"] = len(gt_systems_set.intersection(tool_systems_set)) / len(gt_systems_set.union(tool_systems_set)) if gt_systems_set.union(tool_systems_set) else 1.0
        # Calculate semantic similarity.
        dataset_scores["analogous_systems_semantic"] = np.mean(np.max(cosine_similarity(SEMANTIC_MODEL.encode(gt_systems), SEMANTIC_MODEL.encode(tool_systems)), axis=1)) if gt_systems and tool_systems else 0.0

        # --- Task 5: Biological Process Synthesis ---
        print("\n   SCORING TASK 5: 'Biological Process Synthesis'")
        # Get synthesis text, defaulting to empty string.
        gt_synthesis = ground_truth_data.get("biological_process_synthesis", {}).get("text", "")
        tool_synthesis = tool_output_data.get("biological_process_synthesis", {}).get("text", "")
        # Calculate cosine similarity between the two synthesis texts.
        synthesis_score = cosine_similarity(SEMANTIC_MODEL.encode([gt_synthesis]), SEMANTIC_MODEL.encode([tool_synthesis]))[0, 0] if gt_synthesis and tool_synthesis else 0.0
        dataset_scores["biological_synthesis_cosine"] = synthesis_score

        # --- Task 6: Hypothesis Generation ---
        print("\n   SCORING TASK 6: 'Hypothesis Generation'")
        # Get hypothesis statements safely.
        gt_hypotheses_data = ground_truth_data.get("hypotheses", {})
        tool_hypotheses_data = tool_output_data.get("hypotheses", {})
        gt_hypotheses = gt_hypotheses_data.get("statements", []) if isinstance(gt_hypotheses_data, dict) else gt_hypotheses_data
        tool_hypotheses = tool_hypotheses_data.get("statements", []) if isinstance(tool_hypotheses_data, dict) else tool_hypotheses_data
        # Create sets for Jaccard similarity.
        gt_hypotheses_set = {h.lower().strip() for h in gt_hypotheses if h}
        tool_hypotheses_set = {h.lower().strip() for h in tool_hypotheses if h}
        # Calculate Jaccard similarity.
        dataset_scores["hypotheses_jaccard"] = len(gt_hypotheses_set.intersection(tool_hypotheses_set)) / len(gt_hypotheses_set.union(tool_hypotheses_set)) if gt_hypotheses_set.union(tool_hypotheses_set) else 1.0
        # Calculate semantic similarity.
        dataset_scores["hypotheses_semantic"] = np.mean(np.max(cosine_similarity(SEMANTIC_MODEL.encode(gt_hypotheses), SEMANTIC_MODEL.encode(tool_hypotheses)), axis=1)) if gt_hypotheses and tool_hypotheses else 0.0

        # --- Task 7: Novel Insight Identification ---
        print("\n   SCORING TASK 7: 'Novel Insight Identification'")
        # Get novel insight statements safely.
        gt_insights_data = ground_truth_data.get("novel_insights", {})
        tool_insights_data = tool_output_data.get("novel_insights", {})
        gt_insights = gt_insights_data.get("statements", []) if isinstance(gt_insights_data, dict) else gt_insights_data
        tool_insights = tool_insights_data.get("statements", []) if isinstance(tool_insights_data, dict) else tool_insights_data
        # Create sets for Jaccard similarity.
        gt_insights_set = {i.lower().strip() for i in gt_insights if i}
        tool_insights_set = {i.lower().strip() for i in tool_insights if i}
        # Calculate Jaccard similarity.
        dataset_scores["novel_insights_jaccard"] = len(gt_insights_set.intersection(tool_insights_set)) / len(gt_insights_set.union(tool_insights_set)) if gt_insights_set.union(tool_insights_set) else 1.0
        # Calculate semantic similarity.
        dataset_scores["novel_insights_semantic"] = np.mean(np.max(cosine_similarity(SEMANTIC_MODEL.encode(gt_insights), SEMANTIC_MODEL.encode(tool_insights)), axis=1)) if gt_insights and tool_insights else 0.0

        # --- Task 4: Regulatory Network Edge Discovery ---
        print("\n   SCORING TASK 4: 'Regulatory Network Edge Discovery'")
        # Get regulatory edge data safely.
        gt_edges_data = ground_truth_data.get("regulatory_network_edges", {})
        tool_edges_data = tool_output_data.get("regulatory_network_edges", {})
        gt_edge_list = gt_edges_data.get("edges", []) if isinstance(gt_edges_data, dict) else gt_edges_data
        tool_edge_list = tool_edges_data.get("edges", []) if isinstance(tool_edges_data, dict) else tool_edges_data

        # Define a helper function to format an edge into a consistent string representation.
        def format_edge(edge):
            if isinstance(edge, dict) and 'source' in edge and 'target' in edge:
                return f"{edge['source'].upper().strip()} -> {edge['target'].upper().strip()}"
            return None
        
        # Create a set of normalized ground truth edges.
        gt_edges_normalized = {format_edge(edge) for edge in gt_edge_list if format_edge(edge)}
        # Create a list of normalized tool-provided edges (order matters for MRR).
        tool_edges_normalized = [format_edge(edge) for edge in tool_edge_list if format_edge(edge)]
        # Initialize Mean Reciprocal Rank (MRR) score.
        mrr_score = 0.0
        # Calculate MRR if lists are not empty.
        if gt_edges_normalized and tool_edges_normalized:
            # Calculate reciprocal rank for each ground truth edge.
            reciprocal_ranks = [1 / (tool_edges_normalized.index(edge) + 1) if edge in tool_edges_normalized else 0 for edge in gt_edges_normalized]
            # Calculate the mean of the reciprocal ranks.
            if reciprocal_ranks:
                mrr_score = np.mean(reciprocal_ranks)
        dataset_scores["regulatory_network_mrr"] = mrr_score

        # --- Task 11: Hub Gene Annotation ---
        print("\n   SCORING TASK 11: 'Hub Gene Annotation'")
        # Get gene annotation data safely.
        gt_annotation_data = ground_truth_data.get("hub_gene_annotation", {})
        tool_annotation_data = tool_output_data.get("hub_gene_annotation", {})
        # Define the categories to be scored.
        annotation_categories = ["drug_targets", "kinases", "biomarkers"]
        # Initialize a list to store F1 scores for each category.
        f1_scores = []
        # Loop through each annotation category.
        for category in annotation_categories:
            # Create sets of genes for the current category from both ground truth and tool.
            gt_genes = {gene.upper().strip() for gene in gt_annotation_data.get(category, []) if gene}
            tool_genes = {gene.upper().strip() for gene in tool_annotation_data.get(category, []) if gene}
            # Calculate true positives, precision, recall, and F1 score.
            true_positives = len(gt_genes.intersection(tool_genes))
            precision = true_positives / len(tool_genes) if len(tool_genes) > 0 else 0
            recall = true_positives / len(gt_genes) if len(gt_genes) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            # Append the calculated F1 score to the list.
            f1_scores.append(f1)
        # Calculate the average F1 score across all categories.
        dataset_scores["hub_gene_annotation_f1"] = np.mean(f1_scores) if f1_scores else 0.0

        # --- Task 3: Enrichment Categorization ---
        print("\n   SCORING TASK 3: 'Enrichment Categorization'")
        # Get enrichment categorization data safely.
        gt_cat_data = ground_truth_data.get("enrichment_categorization", {})
        tool_cat_data = tool_output_data.get("enrichment_categorization", {})
        gt_categories = gt_cat_data.get("categories", []) if isinstance(gt_cat_data, dict) else gt_cat_data
        tool_categories_nested = tool_cat_data.get("categories", []) if isinstance(tool_cat_data, dict) else tool_cat_data
        # Flatten the potentially nested structure of tool-provided categories.
        tool_categories_flat = []
        if isinstance(tool_categories_nested, list):
            for component in tool_categories_nested:
                if isinstance(component, dict) and "categories" in component:
                    tool_categories_flat.extend(component["categories"])
        # Initialize list to store scores for the best matching categories.
        best_match_scores = []
        composite_jaccard_score_cat = 0.0
        # Proceed if both ground truth and tool provided categories.
        if gt_categories and tool_categories_flat:
            # For each ground truth category...
            for gt_cat in gt_categories:
                if not isinstance(gt_cat, dict) or "terms" not in gt_cat: continue
                gt_terms_set = {term.lower().strip() for term in gt_cat.get("terms", [])}
                max_jaccard_for_gt_cat = 0.0
                # ...find the best matching tool category based on Jaccard similarity of terms.
                for tool_cat in tool_categories_flat:
                    if not isinstance(tool_cat, dict) or "terms" not in tool_cat: continue
                    tool_terms_set = {term.lower().strip() for term in tool_cat.get("terms", [])}
                    intersection = len(gt_terms_set.intersection(tool_terms_set))
                    union = len(gt_terms_set.union(tool_terms_set))
                    current_jaccard = intersection / union if union > 0 else 0.0
                    if current_jaccard > max_jaccard_for_gt_cat:
                        max_jaccard_for_gt_cat = current_jaccard
                # Add the best match score to the list.
                best_match_scores.append(max_jaccard_for_gt_cat)
            # Calculate the average of the best match scores.
            if best_match_scores:
                composite_jaccard_score_cat = np.mean(best_match_scores)
        dataset_scores["enrichment_categorization_jaccard"] = composite_jaccard_score_cat

        # --- Task 10: System Model Reconstruction ---
        print("\n   SCORING TASK 10: 'System Model Reconstruction'")
        # Get system model data safely.
        gt_model_data = ground_truth_data.get("integrated_system_nodes", {})
        tool_model_data = tool_output_data.get("integrated_system_nodes", {})
        gt_modules = gt_model_data.get("modules", []) if isinstance(gt_model_data, dict) else gt_model_data
        tool_modules = tool_model_data.get("modules", []) if isinstance(tool_model_data, dict) else tool_model_data
        # Logic is similar to categorization: find best matching module based on Jaccard similarity of genes.
        best_match_scores_model = []
        composite_jaccard_score_model = 0.0
        if gt_modules and tool_modules:
            for gt_mod in gt_modules:
                if not isinstance(gt_mod, dict) or "genes" not in gt_mod: continue
                gt_genes_set = {gene.upper().strip() for gene in gt_mod.get("genes", [])}
                max_jaccard_for_gt_mod = 0.0
                for tool_mod in tool_modules:
                    if not isinstance(tool_mod, dict) or "genes" not in tool_mod: continue
                    tool_genes_set = {gene.upper().strip() for gene in tool_mod.get("genes", [])}
                    intersection = len(gt_genes_set.intersection(tool_genes_set))
                    union = len(gt_genes_set.union(tool_genes_set))
                    current_jaccard = intersection / union if union > 0 else 0.0
                    if current_jaccard > max_jaccard_for_gt_mod:
                        max_jaccard_for_gt_mod = current_jaccard
                best_match_scores_model.append(max_jaccard_for_gt_mod)
            if best_match_scores_model:
                composite_jaccard_score_model = np.mean(best_match_scores_model)
        dataset_scores["system_model_jaccard"] = composite_jaccard_score_model

        # --- Task 9: Publication Title Generation ---
        print("\n   SCORING TASK 9: 'Publication Title Generation'")
        # Get publication titles safely.
        gt_title = ground_truth_data.get("publication_title", "")
        tool_title = tool_output_data.get("publication_title", "")
        title_score = 0.0
        # If both titles exist, calculate cosine similarity.
        if gt_title and tool_title:
            print(f"      - GT Title: {gt_title}")
            print(f"      - Tool Title: {tool_title}")
            gt_embedding = SEMANTIC_MODEL.encode([gt_title])
            tool_embedding = SEMANTIC_MODEL.encode([tool_title])
            title_score = cosine_similarity(gt_embedding, tool_embedding)[0, 0]
        dataset_scores["publication_title_cosine"] = title_score
        print(f"      - Cosine Similarity: {title_score:.4f}")

        # --- Task 12: Component-Level Summarization ---
        print("\n   SCORING TASK 12: 'Component-Level Summarization'")
        # Get component summary data safely.
        gt_comp_data = ground_truth_data.get("component_summaries", {})
        tool_comp_data = tool_output_data.get("component_summaries", {})
        gt_summaries_list = gt_comp_data.get("summaries", []) if isinstance(gt_comp_data, dict) else gt_comp_data
        tool_summaries_list = tool_comp_data.get("summaries", []) if isinstance(tool_comp_data, dict) else tool_comp_data
        
        # Create dictionaries mapping component name to summary text for easy lookup.
        gt_summary_map = {item.get("component"): item.get("summary", "") for item in gt_summaries_list if isinstance(item, dict)}
        tool_summary_map = {item.get("component"): item.get("summary", "") for item in tool_summaries_list if isinstance(item, dict)}
        
        # Initialize list to store scores for matched components.
        summary_scores = []
        composite_summary_score = 0.0
        if gt_summary_map and tool_summary_map:
            print("\n      --- Data for Component Summary Calculation ---")
            # Iterate through ground truth components.
            for component, gt_summary in gt_summary_map.items():
                # Find the matching tool summary by component name.
                tool_summary = tool_summary_map.get(component)
                # If both summaries exist, calculate cosine similarity.
                if gt_summary and tool_summary:
                    gt_embedding = SEMANTIC_MODEL.encode([gt_summary])
                    tool_embedding = SEMANTIC_MODEL.encode([tool_summary])
                    score = cosine_similarity(gt_embedding, tool_embedding)[0, 0]
                    summary_scores.append(score)
                    print(f"      - Matched Component '{component}': Score = {score:.4f}")
                else:
                    print(f"      - No matching tool summary found for GT component '{component}'.")
            
            # Calculate the average score if any components were matched.
            if summary_scores:
                composite_summary_score = np.mean(summary_scores)
        
        dataset_scores["component_summaries_cosine"] = composite_summary_score
        print(f"      ------------------------------------")
        print(f"      - Final Composite Cosine Score: {composite_summary_score:.4f}")

        # Append the completed scores for the dataset to the main results list.
        benchmark_results.append(dataset_scores)
        # Print a status message for the completed dataset.
        print(f"\n   >>> STATUS for [{dataset_id}]: SCORING COMPLETE <<<")
        # Print a separator line.
        print("=" * 70)
    
    # Print a summary header for the current tool.
    print(f"\n--- Overall Benchmark Summary for Tool: {tool_name} ---")
    if benchmark_results:
        # Define and print a formatted header for the results table.
        header = (f"{'Dataset':<10} | {'Enr. Jac':<10} | {'Enr. Sem':<10} | {'Hub NDCG':<10} | "
                  f"{'Sys. Jac':<10} | {'Sys. Sem':<10} | {'Synth. Cos':<12} | "
                  f"{'Hyp. Jac':<10} | {'Hyp. Sem':<10} | {'Nov. Jac':<10} | {'Nov. Sem':<10} | "
                  f"{'Net. MRR':<10} | {'Anno. F1':<10} | {'Cat. Jac':<10} | {'Mod. Jac':<10} | "
                  f"{'Title Cos':<11} | {'Comp. Cos':<11}")
        print(header)
        print("-" * len(header))

        # Loop through and print the formatted scores for each dataset.
        for res in benchmark_results:
            line = (f"{res.get('dataset', ''):<10} | "
                    f"{res.get('enrichment_fidelity_jaccard', 0):<10.4f} | "
                    f"{res.get('enrichment_fidelity_semantic', 0):<10.4f} | "
                    f"{res.get('hub_gene_ndcg', 0):<10.4f} | "
                    f"{res.get('analogous_systems_jaccard', 0):<10.4f} | "
                    f"{res.get('analogous_systems_semantic', 0):<10.4f} | "
                    f"{res.get('biological_synthesis_cosine', 0):<12.4f} | "
                    f"{res.get('hypotheses_jaccard', 0):<10.4f} | "
                    f"{res.get('hypotheses_semantic', 0):<10.4f} | "
                    f"{res.get('novel_insights_jaccard', 0):<10.4f} | "
                    f"{res.get('novel_insights_semantic', 0):<10.4f} | "
                    f"{res.get('regulatory_network_mrr', 0):<10.4f} | "
                    f"{res.get('hub_gene_annotation_f1', 0):<10.4f} | "
                    f"{res.get('enrichment_categorization_jaccard', 0):<10.4f} | "
                    f"{res.get('system_model_jaccard', 0):<10.4f} | "
                    f"{res.get('publication_title_cosine', 0):<11.4f} | "
                    f"{res.get('component_summaries_cosine', 0):<11.4f}")
            print(line)
        print("-" * len(header))

        # Print a header for the average scores.
        print(f"\n--- Average Scores Across All Datasets for Tool: {tool_name} ---")
        # Calculate and print the mean for each metric across all datasets.
        print(f"Enrichment Fidelity (Jaccard):          {np.mean([r.get('enrichment_fidelity_jaccard', 0) for r in benchmark_results]):.4f}")
        print(f"Enrichment Fidelity (Semantic):         {np.mean([r.get('enrichment_fidelity_semantic', 0) for r in benchmark_results]):.4f}")
        print(f"Hub Gene Identification (NDCG):         {np.mean([r.get('hub_gene_ndcg', 0) for r in benchmark_results]):.4f}")
        print(f"Analogous Systems (Jaccard):            {np.mean([r.get('analogous_systems_jaccard', 0) for r in benchmark_results]):.4f}")
        print(f"Analogous Systems (Semantic):           {np.mean([r.get('analogous_systems_semantic', 0) for r in benchmark_results]):.4f}")
        print(f"Biological Synthesis (Cosine):          {np.mean([r.get('biological_synthesis_cosine', 0) for r in benchmark_results]):.4f}")
        print(f"Hypothesis Generation (Jaccard):        {np.mean([r.get('hypotheses_jaccard', 0) for r in benchmark_results]):.4f}")
        print(f"Hypothesis Generation (Semantic):       {np.mean([r.get('hypotheses_semantic', 0) for r in benchmark_results]):.4f}")
        print(f"Novel Insight ID (Jaccard):             {np.mean([r.get('novel_insights_jaccard', 0) for r in benchmark_results]):.4f}")
        print(f"Novel Insight ID (Semantic):            {np.mean([r.get('novel_insights_semantic', 0) for r in benchmark_results]):.4f}")
        print(f"Regulatory Network (MRR):               {np.mean([r.get('regulatory_network_mrr', 0) for r in benchmark_results]):.4f}")
        print(f"Hub Gene Annotation (Avg. F1):          {np.mean([r.get('hub_gene_annotation_f1', 0) for r in benchmark_results]):.4f}")
        print(f"Enrichment Categorization (Comp. Jac):  {np.mean([r.get('enrichment_categorization_jaccard', 0) for r in benchmark_results]):.4f}")
        print(f"System Model Reconstruction (Comp. Jac):{np.mean([r.get('system_model_jaccard', 0) for r in benchmark_results]):.4f}")
        print(f"Publication Title (Cosine):             {np.mean([r.get('publication_title_cosine', 0) for r in benchmark_results]):.4f}")
        print(f"Component Summaries (Comp. Cos):        {np.mean([r.get('component_summaries_cosine', 0) for r in benchmark_results]):.4f}")
    
    # Define the output CSV filename for the per-dataset results.
    output_csv_file = f"{tool_name}_benchmark_results.csv"
    if benchmark_results:
        print(f"\n--- Saving detailed per-dataset results to {output_csv_file} ---")
        # Get the headers from the keys of the first result dictionary.
        header = benchmark_results[0].keys()
        try:
            # Open the CSV file in write mode.
            with open(output_csv_file, 'w', newline='') as csvfile:
                # Create a DictWriter to write dictionaries to CSV.
                writer = csv.DictWriter(csvfile, fieldnames=header)
                # Write the header row.
                writer.writeheader()
                # Write all the result rows.
                writer.writerows(benchmark_results)
            print(f"   [SUCCESS] Results successfully saved.")
        except Exception as e:
            print(f"   [ERROR] Could not write to CSV file. Error: {e}")
    else:
        print("\n--- No results were generated to save. ---")

    # Define the output CSV filename for the average scores.
    output_summary_csv_file = f"{tool_name}_average_scores.csv"
    if benchmark_results:
        print(f"\n--- Saving average scores to {output_summary_csv_file} ---")
        # Initialize a dictionary to hold the average scores.
        average_scores = {}
        # Get all metric keys, excluding 'dataset'.
        metric_keys = [key for key in benchmark_results[0].keys() if key != 'dataset']
        # For each metric, calculate the mean score across all datasets.
        for key in metric_keys:
            scores = [res.get(key, 0) for res in benchmark_results]
            average_scores[key] = np.mean(scores)
        
        try:
            # Open the summary CSV file in write mode.
            with open(output_summary_csv_file, 'w', newline='') as csvfile:
                # Create a DictWriter.
                writer = csv.DictWriter(csvfile, fieldnames=average_scores.keys())
                # Write the header row.
                writer.writeheader()
                # Write the single row of average scores.
                writer.writerow(average_scores)
            print(f"   [SUCCESS] Average scores successfully saved.")
        except Exception as e:
            print(f"   [ERROR] Could not write to summary CSV file. Error: {e}")
    else:
        print("\n--- No average scores to save. ---")

# Print a final message indicating the end of the entire script.
print("\n--- [END] ODB Final Benchmark Script ---")
