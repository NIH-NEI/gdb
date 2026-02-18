# The Omics Discovery Bench (ODB)
*A Novel Benchmark Framework for Evaluating Higher-Order Reasoning in AI-driven Biological Interpretation*

------------
- Authors: Vijay Nagarajan PhD, Reiko Horai PhD
- Affiliation: Laboratory of Immunology, NEI/NIH
- Contact: nagarajanv@nih.gov
------------

## Introduction: A Benchmark for Scientific Reasoning

In complex scientific fields like bioinformatics, the true value of an AI tool is not just its accuracy, but its ability to perform higher-order reasoning—synthesizing data into coherent narratives, forming novel hypotheses, and constructing plausible models of biological systems. Standard NLP benchmarks often fail to capture this crucial dimension.

The **Omics Discovery Bench (ODB)** was developed to address this gap. ODB is an open-source benchmark framework that evaluates and ranks analytical tools on their ability to interpret high-throughput omics data. Our "Groundedness-First" philosophy prioritizes structured, verifiable, and data-driven reasoning over simple narrative fluency.

---

## Project Structure

To ensure clarity and reproducibility, the ODB project is organized into the following directories:

| Folder | Description |
| :--- | :--- |
| `groundtruth_data/` | Contains the curated ground truth data for the 8 diverse omics datasets used in the benchmark. This is the baseline against which all tools are evaluated. |
| `performance_scores/` | Includes the raw, quantitative performance scores for each tool across all 12 standardized tasks and 15+ metrics (e.g., NDCG, Jaccard Similarity). |
| `analysis_scripts/` | Provides the R or Python scripts used to process the raw outputs and calculate the final "Grounded Reasoning Score." |
| `results/` | Contains generated figures, plots, and other visual outputs from the analysis, such as the performance quadrant plot. |

---

## How The Benchmark Works

The ODB methodology evaluates tools against a curated ground truth derived from 8 diverse omics datasets. The final ranking is produced through a multi-step process designed to reward scientific rigor.

1.  **12 Standardized Tasks:** Each tool is assessed on a suite of tasks, ranging from high-fidelity data extraction (e.g., `Hub Gene Identification`) to high-level abstractive reasoning (e.g., `System Model Reconstruction`).
2.  **Quantitative Scoring:** Over 15 distinct metrics are calculated, including NDCG for ranking, Jaccard Similarity for set fidelity, and Cosine Similarity for semantic textual alignment.
3.  **"Groundedness-Weighted" Composite Score:** To generate a final ranking, we developed the "Grounded Reasoning Score." This composite score assigns higher weights to tasks that require structured, verifiable reasoning and are resistant to ungrounded hallucination (e.g., `System Model`, `Hub Gene Annotation`). Free-form narrative tasks, where fluent but ungrounded answers can score deceptively high, are weighted lower.

---

## Benchmark Results

We benchmarked 7 different analytical approaches, including our novel **I**ntelligent System for Omics Data **An**lysis and Discovery (IAN) and several general-purpose LLMs (Gemini, ChatGPT, Claude) with and without experimental context. The final ranking, based on our "Grounded Reasoning Score," demonstrates a clear performance hierarchy.

**Table 1:** Final tool ranking based on the "Grounded Reasoning Score."

| Rank | Tool | Final Grounded Score |
| :--- | :--- | :--- |
| **1** | IAN | 0.1689 |
| **2** | Claude (DEG + Exp) | 0.1592 |
| **3** | ChatGPT (DEG + Exp) | 0.1581 |
| **4** | Claude (DEG Only) | 0.1297 |
| **5** | Gemini (DEG + Exp) | 0.1240 |
| **6** | ChatGPT (DEG Only) | 0.1230 |
| **7** | Gemini (DEG Only) | 0.1109 |

While the ranked table provides the final verdict, the performance profile of each tool reveals a more nuanced story. The quadrant plot below visualizes the trade-off between pure factual recall ("Fidelity Score") and higher-order reasoning ("Discovery & Synthesis Score").

![A quadrant plot showing Fidelity Score on the X-axis and Discovery & Synthesis Score on the Y-axis.](results/ODB_OVERALL_PERFORMANCE_QUADRANT.png)
*__Figure 1:__ Performance profile of all benchmarked tools, averaged across 8 datasets. The plot highlights the unique analytical profile of the IAN framework.*

---

## Conclusion

The Omics Discovery Bench successfully distinguishes between different classes of AI-driven analysis. While context-aware generalist LLMs are powerful, they function primarily as high-fidelity information recall engines. The IAN framework, by contrast, demonstrates a superior capacity for grounded, structural reasoning. Its top-ranking performance on our "Grounded Reasoning Score" and its unique position in the performance quadrant confirm that its structured, multi-agent methodology represents a more rigorous and scientifically valuable approach for genuine biological discovery.

---
<p align="center">
  The Omics Discovery Bench (ODB) Project | 2026
  <br>Of course Google Gemini was my research and coding assistant<br>
</p>

