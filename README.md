# The Omics Discovery Bench (ODB)
*A Novel Benchmark Framework for Evaluating Higher-Order Reasoning in AI-driven Biological Interpretation*

------------
- **Authors**: Vijay Nagarajan PhD, Reiko Horai PhD
- **Affiliation**: Laboratory of Immunology, NEI/NIH
- **Contact**: nagarajanv@nih.gov
------------

## Introduction: A Benchmark for scientific reasoning

In complex scientific fields like bioinformatics, the true value of an AI tool is not just its accuracy, but its ability to perform higher-order reasoning—synthesizing data into coherent narratives, forming novel hypotheses, and constructing plausible models of biological systems. Standard Natural Language Processing benchmarks often fail to capture this crucial dimension.

The **Omics Discovery Bench (ODB)** was developed to address this gap. ODB is an open-source benchmark framework that evaluates and ranks analytical tools on their ability to interpret high-throughput omics data. Our "Groundedness-First" philosophy prioritizes structured, verifiable, and data-driven reasoning over simple narrative fluency.

---

## 🏆 Official Leaderboard

We benchmarked 7 different analytical approaches, including general-purpose LLMs and our novel **I**ntelligent System for Omics Data **An**alysis and Discovery (IAN).

**The final ranking, based on our "Grounded Reasoning Score," demonstrates a clear performance hierarchy, with the specialized IAN framework showing a distinct advantage in structured biological interpretation.**

<div align="center">

| Rank | Tool | Final Grounded Score |
| :---: | :--- | :---: |
| **🥇 1** | IAN | **0.1689** |
| **🥈 2** | Claude (DEG + Exp) | 0.1592 |
| **🥉 3** | ChatGPT (DEG + Exp) | 0.1581 |
| **4** | Claude (DEG Only) | 0.1297 |
| **5** | Gemini (DEG + Exp) | 0.1240 |
| **6** | ChatGPT (DEG Only) | 0.1230 |
| **7** | Gemini (DEG Only) | 0.1109 |

</div>

* DEG - Differentially Expressed Genes
* Exp - Experimental Design
* IAN - The IAN benchmarked here used Gemini 2.5 as the LLM, along with DEG, Exp and the novel data augmentation framework as described in the [manuscript](https://www.biorxiv.org/content/10.1101/2025.03.06.640921v1.full#ref-21).
  
While the ranked table provides the final verdict, the performance profile of each tool reveals a more nuanced story. The quadrant plot below visualizes the trade-off between pure factual recall ("Fidelity Score") and higher-order reasoning ("Discovery & Synthesis Score").

<div align="center">
  <img src="results/ODB_DISCOVERY_VS_FIDELITY_QUADRANT.png" alt="A quadrant plot showing Fidelity Score on the X-axis and Discovery & Synthesis Score on the Y-axis." width="70%">
</div>

*__Figure 1:__ Performance profile of all benchmarked tools, averaged across 8 datasets. The plot highlights the unique analytical profile of the IAN framework, which excels in Discovery & Synthesis.*

---

## How the Benchmark Works

The ODB methodology evaluates tools against the curated ground truth. The final ranking is produced through a multi-step process designed to reward scientific rigor.

1.  **12 Standardized Tasks:** Each tool is assessed on a suite of tasks, ranging from high-fidelity data extraction (e.g., `Hub Gene Identification`) to high-level abstractive reasoning (e.g., `System Model Reconstruction`).
2.  **Quantitative Scoring:** Over 15 distinct metrics are calculated, including NDCG (Normalized Discounted Cumulative Gain) for ranking, Jaccard Similarity for set fidelity, and Cosine Similarity for semantic textual alignment.
3.  **"Groundedness-Weighted" Composite Score:** To generate a final ranking, we developed the "Grounded Reasoning Score." This composite score assigns higher weights to tasks that require structured, verifiable reasoning and are resistant to ungrounded hallucination (e.g., `System Model`, `Hub Gene Annotation`). Free-form narrative tasks, where fluent but ungrounded answers can score deceptively high, are weighted lower.

---

## Ground Truth Datasets

The benchmark is built upon 8 diverse, publicly available human omics datasets. The ground truth for each was manually curated from the corresponding peer-reviewed publication. Full details can be found in the linked manuscripts and the JSON files within the `groundtruth_data/` directory.

<div align="center">

| ID | Phenotype | Tissue / Cell Type | Source Publication (PMID) |
|:---|:---|:---|:---|
| **BC** | Breast Cancer | Breast Tissue | [31423162](https://pubmed.ncbi.nlm.nih.gov/31423162/) |
| **HCM**| Hypertrophic Cardiomyopathy | Heart Tissue | [34225646](https://pubmed.ncbi.nlm.nih.gov/34225646/) |
| **PD1**| Early Rheumatoid Arthritis | CD4⁺ T Cells | [36801909](https://pubmed.ncbi.nlm.nih.gov/36801909/) |
| **BP** | Bullous Pemphigoid | PBMCs | [40736520](https://pubmed.ncbi.nlm.nih.gov/40736520/) |
| **MN** | Membranous Nephropathy | Glomeruli | [37876929](https://pubmed.ncbi.nlm.nih.gov/37876929/) |
| **GC** | Gastric Cancer | Gastric Tissue | [38041130](https://pubmed.ncbi.nlm.nih.gov/38041130/) |
| **UV** | Uveitis | Whole Blood | [33503442](https://pubmed.ncbi.nlm.nih.gov/33503442/) |
| **PAD**| Peripheral Arterial Disease | PBMCs | [22409835](https://pubmed.ncbi.nlm.nih.gov/22409835/) |

</div>

---

## How to Contribute Your Tool

We welcome and encourage submissions from the community. If you have a tool you would like to benchmark against ODB, please follow these steps:

1.  **Generate Outputs:** For each of the 8 datasets, run your tool using the provided input data (DEG lists and experimental design text).
2.  **Format Your Results:** Your tool must produce one `odb_tool_output.json` file for each of the 8 datasets. The JSON file must strictly adhere to the structure and field names of the standardized output format.
3.  **Consult the Template:** For a definitive example of the required JSON structure, please see the output file for the Breast Cancer (BC) dataset here: **[odb_tool_output.json template](https://github.com/NIH-NEI/odb/blob/main/results/tools_outputs/chatgpt_gex_exp/BC/odb_tool_output.json)**.
4.  **Organize and Submit:** Please organize your 8 output files into a directory structure named after your tool, as shown below, and contact us via email to coordinate the transfer. We will run the performance evaluation and add your tool to the official leaderboard.

    ```
    your_tool_name/
    ├── BC/
    │   └── odb_tool_output.json
    ├── BP/
    │   └── odb_tool_output.json
    ├── GC/
    │   └── odb_tool_output.json
    ├── HCM/
    │   └── odb_tool_output.json
    ├── MN/
    │   └── odb_tool_output.json
    ├── PAD/
    │   └── odb_tool_output.json
    ├── PD1/
    │   └── odb_tool_output.json
    └── UV/
        └── odb_tool_output.json
    ```

---

## Project Structure

To ensure clarity and reproducibility, the ODB project is organized into the following directories:

<div align="center">

| Folder | Description |
| :--- | :--- |
| `groundtruth_data/` | Contains the curated ground truth data for the 8 diverse omics datasets used in the benchmark. |
| `results/tools_outputs/` | Contains the raw JSON outputs from each benchmarked tool, organized by tool name and dataset ID. |
| `analysis_scripts/` | Provides the Python scripts used to process the raw JSON outputs and calculate the final scores. |
| `results/figures/` | Contains generated figures and IAN's original analysis results for all 8 datasets. |

</div>

---

## Conclusion

The Omics Discovery Bench successfully distinguishes between different classes of AI-driven analysis. While context-aware generalist LLMs are powerful, they function primarily as high-fidelity information recall engines. The IAN framework, by contrast, demonstrates a superior capacity for grounded, structural reasoning. Its top-ranking performance on our "Grounded Reasoning Score" and its unique position in the performance quadrant confirm that its structured, multi-agent methodology represents a more rigorous and scientifically valuable approach for genuine biological discovery.

---

<p align="center">
  The Omics Discovery Bench (ODB) Project | 2026
  <br>
  (P.S. Gemini was my research and coding assistant for this project!)
</p>
