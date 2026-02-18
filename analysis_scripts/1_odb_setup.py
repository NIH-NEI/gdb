# -----------------------------------------------------------------------------
# Script: 1_odb_setup.py
# Author: Vijayaraj Nagarajan PhD
# Assistant: Google Gemini
#
# Objective:
# This script builds the complete directory structure and ground truth files for
# the ODB benchmark. It reads from source CSVs containing metadata and gene
# lists, and uses curated Python dictionaries to generate the required input
# files (`input_genes.txt`) and comprehensive ground truth (`ground_truth.json`)
# for each of the 8 benchmark datasets.
#
# Inputs:
#   - `benchmark-gene-extraction-reference.csv`: Metadata for each dataset (ID, PMID, Phenotype).
#   - `benchmark-gene-extraction-degs.csv`: Differentially expressed genes for each dataset, in wide format.
#   - `benchmark-hub-genes-reference.csv`: Curated hub genes for each dataset.
#
# Outputs:
#   - Creates the `ODB/datasets/` directory structure.
#   - For each dataset ID (e.g., 'BC', 'PAD'), it generates:
#     - `ODB/datasets/<ID>/input_genes.txt`: The list of DEGs for the tool to analyze.
#     - `ODB/datasets/<ID>/ground_truth.json`: The consolidated ground truth file for all 12 benchmark tasks.
# -----------------------------------------------------------------------------

import os
import pandas as pd
import json

# This block contains the final, corrected data for all 8 benchmark manuscripts.

# Defines the ground truth ranked hub genes for each manuscript identified by PMID.
RANKED_HUB_GENES_GROUND_TRUTH = {
    "31423162": ["PLK1", "TOP2A", "CDC20", "CDK1", "BUB1B", "AURKA", "CCNB1", "TPX2", "KIF2C", "CXCL8", "BIRC5", "CCNA2", "NCAPG", "NDC80"],
    "22409835": ["PTGS2", "FOS", "JUN", "MMP1", "MMP3", "EGR1", "DUSP1", "ZFP36"], # PAD
    "34225646": ["MYH7", "MYBPC3", "TNNT2", "MYL2", "JAK2", "MS4A7", "C1R", "MBP"],
    "36801909": ["PDCD1", "CXCL13", "MAF", "TIGIT", "IL21", "POU2AF1", "CD200", "GZMK", "SLAMF6", "CD84", "LAIR2", "ITM2C", "IL10", "CTLA4", "CCR7", "ICOS", "FAS", "CD40LG", "CXCR5"],
    "40736520": ["SLPI", "CAMP", "PSTPIP2", "ANXA3", "BZRAP1", "RAB27A", "TMEM237", "SAMSN1", "SCNM1", "PDK4", "SKAP2"],
    "37876929": ["ALB", "AIF1", "CSF1R", "FCGR2B", "FCER1G", "CYBB", "FCGR2A", "CSF1", "ORM1", "COLEC12", "HBA2", "CHGA", "HBA1", "OR51E2"],
    "38041130": ["COL1A1", "TIMP1", "SPP1", "COL1A2", "ITGA5", "HEPH", "MAOA", "PRDM16", "FOXA2", "C9orf152"],
    "33503442": ["IRF1", "ICAM1", "UTY", "TYK2", "IL15RA", "IL15", "MEF2A", "GSK3A", "IL10RB", "MEF2B", "MEF2D", "LINC00278"]
}

# Defines the ground truth narrative enrichment terms for each manuscript.
NARRATIVE_ENRICHMENT_GROUND_TRUTH = {
    "31423162": ["Cell cycle", "p53 signaling pathway", "Oocyte meiosis", "cell division", "mitotic nuclear division"],
    "22409835": ["inflammatory response", "cytokine-cytokine receptor interaction", "MAPK signaling pathway", "Toll-like receptor signaling pathway", "apoptosis", "signal transduction"], # PAD
    "34225646": ["Hypertrophic cardiomyopathy", "Cardiac muscle contraction", "Adrenergic signaling in cardiomyocytes"],
    "36801909": ["Th1 and Th2 cell differentiation", "T cell receptor signaling pathway", "chemokine signaling pathway"],
    "40736520": ["leukocyte transendothelial migration", "neutrophil degranulation", "MyD88-dependent signaling pathway"],
    "37876929": ["B cell activation", "NF-kappa B signaling pathway", "TNF signaling pathway", "Toll-like receptor signaling pathway"],
    "38041130": ["PI3K-Akt signaling pathway", "Focal adhesion", "ECM-receptor interaction"],
    "33503442": ["interferon-gamma-mediated signaling pathway", "antigen processing and presentation", "response to virus"]
}

# Defines the ground truth for how enrichment terms are categorized into broader themes.
ENRICHMENT_CATEGORIZATION_GROUND_TRUTH = {
    "31423162": [{"category_name": "Cell Proliferation and Regulation", "terms": ["Cell cycle", "p53 signaling pathway", "Oocyte meiosis", "cell division", "mitotic nuclear division", "DNA replication"]}],
    "22409835": [{"category_name": "Inflammatory and Immune Signaling", "terms": ["inflammatory response", "cytokine-cytokine receptor interaction", "MAPK signaling pathway", "Toll-like receptor signaling pathway"]}, {"category_name": "Matrix Remodeling", "terms": ["extracellular matrix organization"]}], # PAD
    "34225646": [{"category_name": "Cardiac Function and Disease", "terms": ["Hypertrophic cardiomyopathy", "Cardiac muscle contraction", "Adrenergic signaling in cardiomyocytes", "Arrhythmogenic right ventricular cardiomyopathy"]}],
    "36801909": [{"category_name": "T-Cell Biology", "terms": ["Th1 and Th2 cell differentiation", "T cell receptor signaling pathway"]}, {"category_name": "Immune Signaling", "terms": ["chemokine signaling pathway", "cytokine-cytokine receptor interaction"]}],
    "40736520": [{"category_name": "Leukocyte and Neutrophil Function", "terms": ["leukocyte transendothelial migration", "neutrophil degranulation"]}, {"category_name": "Innate Immune Signaling", "terms": ["MyD88-dependent signaling pathway", "Toll-like receptor signaling pathway"]}],
    "37876929": [{"category_name": "Adaptive and Innate Immunity", "terms": ["B cell activation", "Toll-like receptor signaling pathway", "Fc gamma R-mediated phagocytosis"]}, {"category_name": "Inflammatory Signaling", "terms": ["NF-kappa B signaling pathway", "TNF signaling pathway"]}],
    "38041130": [{"category_name": "Cancer Progression and Signaling", "terms": ["PI3K-Akt signaling pathway", "Proteoglycans in cancer"]}, {"category_name": "Cell Adhesion and ECM", "terms": ["Focal adhesion", "ECM-receptor interaction"]}],
    "33503442": [{"category_name": "Interferon Response", "terms": ["interferon-gamma-mediated signaling pathway", "response to interferon-gamma"]}, {"category_name": "Antigen Presentation", "terms": ["antigen processing and presentation"]}, {"category_name": "Viral Defense", "terms": ["response to virus", "defense response to virus"]}]
}

# Defines the ground truth for regulatory interactions (e.g., TF-target pairs).
REGULATORY_NETWORK_GROUND_TRUTH = {
    "31423162": [],
    "22409835": [{"source": "FOS", "target": "MMP1"}, {"source": "JUN", "target": "MMP1"}, {"source": "FOS", "target": "MMP3"}, {"source": "JUN", "target": "MMP3"}], # PAD
    "34225646": [],
    "36801909": [{"source": "MAF", "target": "CXCL13"}, {"source": "MAF", "target": "CXCR5"}],
    "40736520": [],
    "37876929": [],
    "38041130": [],
    "33503442": [{"source": "IRF1", "target": "GBP1"}, {"source": "IRF1", "target": "STAT1"}, {"source": "IRF1", "target": "ICAM1"}]
}

# Defines the ground truth abstract-level summary of the biological findings.
BIOLOGICAL_SYNTHESIS_GROUND_TRUTH = {
    "31423162": "To identify prognostic biomarkers for breast cancer, this study performed a bioinformatic analysis of differentially expressed genes (DEGs). The analysis identified 14 key hub genes, including PLK1 and TOP2A, which were significantly enriched in cell cycle-related pathways like the 'p53 signaling pathway' and 'Oocyte meiosis'. The authors conclude that these genes are not only central to the disease's progression but also serve as crucial potential biomarkers and therapeutic targets.",
    "22409835": "To identify the earliest molecular events in Peripheral Artery Disease (PAD), this study performed gene expression profiling on human popliteal arteries. The analysis revealed a distinct inflammatory signature in early PAD, characterized by the significant upregulation of key hub genes including PTGS2 (COX-2), FOS, JUN, and matrix metalloproteinases MMP1 and MMP3. These genes are involved in critical pathways such as MAPK and Toll-like receptor signaling. The authors conclude that inflammatory processes and matrix degradation are initiated very early in the development of PAD, and the identified genes represent key players and potential therapeutic targets.", # PAD
    "34225646": "To overcome challenges in diagnosing Hypertrophic Cardiomyopathy (HCM), this work performed an integrative multi-cohort, multi-platform analysis to identify a robust disease signature. From an initial set of DEGs, the authors established an eight-gene biomarker panel, including key cardiac structural genes like MYH7 and MYBPC3, which can accurately distinguish HCM from control samples. This signature was correlated with clinical markers, demonstrating its power and potential for reproducible clinical application.",
    "36801909": "To characterize the function of pathogenic T cells in early rheumatoid arthritis (RA), this study analyzed the gene expression of synovial PD-1+ T cells. The analysis revealed a specific gene signature indicating these cells are highly pro-inflammatory, producing factors like CXCL13 under the regulation of the transcription factor MAF. The authors conclude that these cells are a major driver of disease pathogenesis by promoting B-cell recruitment and the formation of ectopic lymphoid structures in the synovium.",
    "40736520": "In the first study of its kind, the transcriptomic profile of PBMCs from Bullous Pemphigoid (BP) patients was investigated to identify key molecular signatures. The analysis of DEGs showed a primary enrichment in pathways associated with 'leukocyte transendothelial migration' and 'neutrophil degranulation'. The authors conclude that key upregulated genes within these pathways, such as SLPI and CAMP, represent potential diagnostic biomarkers and therapeutic targets for BP.",
    "37876929": "To explore the underlying immune mechanisms of Membranous Nephropathy (MN), this study employed a comprehensive bioinformatic analysis of public datasets. The results indicated that the pathogenesis is closely related to immune cell infiltration, particularly B-cell activation, and the activation of key inflammatory signaling cascades, such as the 'NF-kappa B signaling pathway' and the 'TNF signaling pathway'. These findings highlight the central role of both adaptive and innate immunity in MN.",
    "38041130": "To identify more reliable prognostic biomarkers for Gastric Cancer (GC), this study analyzed public microarray data to construct a prognostic gene signature. A 10-gene signature was identified and validated, which includes key extracellular matrix genes like COL1A1, TIMP1, and SPP1, and is strongly associated with poor patient prognosis. These genes were enriched in the 'PI3K-Akt signaling pathway' and 'focal adhesion', marking them as crucial targets for future therapeutic strategies.",
    "33503442": "To identify a unifying molecular signature in non-infectious uveitis across different etiologies, this work analyzed whole-blood transcriptomes from a large patient cohort. The analysis revealed a prominent and consistent interferon-gamma (IFN-γ) driven, Th1-type signature, with IRF1 identified as a key upstream regulator. The authors conclude that IFN-γ signaling is a central, unifying feature of the disease process and a primary driver of the associated inflammation."
}

# Defines the ground truth for forward-looking or testable hypotheses from each paper.
HYPOTHESIS_GROUND_TRUTH = {
    "31423162": ["The results of the present study suggested that the identified hub genes and pathways may play crucial roles in the progression of breast cancer.", "The present study identified a number of DEGs and hub genes which may serve as prognostic biomarkers and potential therapeutic targets for breast cancer.", "Further investigation is required to confirm the roles of these genes in breast cancer."],
    "22409835": ["These results suggest that inflammatory processes are initiated early in the development of PAD, before the formation of complex atherosclerotic lesions.", "The identified genes may represent novel targets for therapeutic intervention aimed at preventing the progression of the disease.", "It is plausible that the upregulation of MMPs contributes directly to the plaque instability observed in later stages of PAD.", "Further studies are needed to validate these gene expression changes at the protein level and in a larger patient cohort."], # PAD
    "34225646": ["This suggests that JAK2-mediated inflammation may play an important role in the pathophysiology of HCM.", "Our work provides a promising tool for future clinical application and a valuable resource for the research community.", "The underlying mechanisms by which these genes contribute to HCM pathogenesis warrant further investigation."],
    "36801909": ["Our study suggests that synovial PD-1+ T cells in early RA are a major source of CXCL13 and possess a specific gene signature that may be involved in the formation of ectopic lymphoid structures.", "These findings implicate MAF as a key pathogenic transcription factor in early RA.", "Furthermore, targeting the CXCL13–CXCR5 axis could be a potential therapeutic strategy for early RA.", "Further studies are warranted to fully elucidate the function of these cells and their related molecules."],
    "40736520": ["These DEGs may be involved in the pathogenesis of BP and could be used as potential diagnostic biomarkers and therapeutic targets.", "Further studies are needed to clarify the exact roles of these DEGs in the pathogenesis of BP, which may provide new insights for the development of novel therapeutic strategies."],
    "37876929": ["The pathogenesis of MN may be closely related to immune cell infiltration, especially B-cell activation, and the activation of NF-kappa B and TNF signaling pathways.", "These identified hub genes could serve as potential therapeutic targets for MN.", "Further experimental studies are required to validate the functions of these genes."],
    "38041130": ["The results suggested that COL1A1, TIMP1, and SPP1 may serve as prognostic biomarkers and therapeutic targets for GC.", "This signature could be used to guide personalized treatment strategies for patients with GC.", "Future studies should focus on validating the biological functions of these genes in GC."],
    "33503442": ["The data suggest that IFN-γ is a central and unifying feature of the disease process.", "Targeting the IFN-γ pathway may therefore represent a valid therapeutic approach for a broad spectrum of uveitis patients.", "Further studies are needed to determine the cellular source of the IFN-γ signature and its upstream regulation."]
}

# Defines the ground truth for insights the authors claimed as novel.
NOVEL_INSIGHTS_GROUND_TRUTH = {
    "31423162": ["To the best of our knowledge, the potential roles of hub genes such as BUB1B, KIF2C, NCAPG, NDC80 and TPX2 have not yet been fully elucidated in breast cancer, providing a new direction for future research."],
    "22409835": ["To our knowledge, this is one of the first studies to use gene expression profiling to characterize early-stage, histologically-defined PAD in human arteries.", "Our study provides new insights into the molecular basis of early atherosclerotic disease by identifying a robust inflammatory gene signature prior to advanced lesion formation."], # PAD
    "34225646": ["To our knowledge, this is the first study to conduct a comprehensive multi-cohort, multi-platform integrative analysis to establish a robust diagnostic signature for HCM.", "This provides new insight into the potential involvement of inflammation in HCM pathophysiology.", "We also identified two less characterized genes (MS4A7 and C1R) whose roles in HCM have not been well described."],
    "36801909": ["Our study is the first to characterize the gene signature of PD-1+ T cells in the synovial fluid of treatment-naïve early RA patients.", "These findings implicate MAF as a key pathogenic transcription factor in early RA, a role that was previously unclear."],
    "40736520": ["To our knowledge, this is the first study to investigate the DEGs in the PBMCs of BP patients, providing a novel transcriptomic landscape of the disease.", "The results indicated that the DEGs were primarily enriched in pathways related to 'leukocyte transendothelial migration' and 'neutrophil degranulation', a connection which has not been widely reported in PBMC studies."],
    "37876929": ["Through this analysis, we identified 14 potential hub genes... especially CSF1R, AIF1, and CYBB, which have not been extensively studied in the context of MN and represent novel targets.", "Our findings provide new insights into the molecular mechanisms of MN."],
    "38041130": ["In the present study, a novel 10-gene signature was identified and validated for predicting the prognosis of patients with GC.", "To the best of our knowledge, the prognostic value of HEPH, PRDM16, and C9orf152 in GC has not been previously reported."],
    "33503442": ["Our work is novel in that it identifies a prominent IFN-γ driven, Th1-type signature as a unifying feature across a large cohort of patients with different underlying etiologies of non-infectious uveitis.", "The data suggest that IFN-γ is a central and unifying feature of the disease process, a concept that provides new insight into its pathogenesis."]
}

# Defines the ground truth for other diseases or systems compared to in the paper.
ANALOGOUS_SYSTEMS_GROUND_TRUTH = {
    "31423162": ["Ovarian cancer", "Lung cancer", "Prostate cancer"],
    "22409835": ["Atherosclerosis", "Coronary artery disease (CAD)", "Abdominal aortic aneurysm (AAA)"], # PAD
    "34225646": ["Dilated cardiomyopathy", "Arrhythmogenic right ventricular cardiomyopathy", "Heart Failure"],
    "36801909": ["Systemic lupus erythematosus (SLE)", "Sjögren's syndrome", "Cancer immunotherapy", "Chronic viral infections"],
    "40736520": ["Pemphigus vulgaris", "Dermatitis herpetiformis", "Cicatricial pemphigoid"],
    "37876929": ["Lupus nephritis", "Focal segmental glomerulosclerosis (FSGS)", "IgA nephropathy"],
    "38041130": ["Colorectal cancer", "Hepatocellular carcinoma", "Esophageal cancer"],
    "33503442": ["Sarcoidosis", "Behçet's disease", "Vogt-Koyanagi-Harada (VKH) disease", "Ankylosing spondylitis", "Multiple sclerosis"]
}

# Defines the ground truth titles for each publication.
PUBLICATION_TITLE_GROUND_TRUTH = {
    "31423162": "Identification of hub genes and key pathways associated with breast cancer",
    "22409835": "Identification of early molecular changes in human peripheral artery disease", # PAD
    "34225646": "An integrated multi-omics approach to identify a robust diagnostic gene signature for hypertrophic cardiomyopathy",
    "36801909": "Gene signature of programmed cell death-1+ T cells in the synovial fluid of early rheumatoid arthritis",
    "40736520": "Identification of differentially expressed genes and signaling pathways in bullous pemphigoid by integrated bioinformatics analysis",
    "37876929": "Identification of key genes and immune cell infiltration in membranous nephropathy by multiple bioinformatic analysis",
    "38041130": "Identification and validation of a novel 10-gene signature for predicting the prognosis of patients with gastric cancer",
    "33503442": "Whole-Blood Transcriptome Analysis of Non-infectious Uveitis Reveals a Coordinated Network of Core Pathways and Key Regulatory Genes"
}

# Defines the ground truth for gene modules and their associated phenotypes.
INTEGRATED_SYSTEM_NODES_GROUND_TRUTH = {
    "31423162": [{"module_name": "Core Mitotic Spindle & Cell Cycle Hub", "associated_phenotype": "Cell Proliferation and Mitotic Progression", "genes": ["PLK1", "TOP2A", "CDC20", "CDK1", "BUB1B", "CCNA2", "BIRC5", "AURKA", "TPX2", "NDC80", "NCAPG", "KIF2C"]}],
    "22409835": [{"module_name": "Inflammatory Signaling Hub", "associated_phenotype": "Pro-inflammatory signaling cascade", "genes": ["PTGS2", "FOS", "JUN", "EGR1", "DUSP1", "ZFP36"]}, {"module_name": "Matrix Degradation Module", "associated_phenotype": "Extracellular matrix remodeling", "genes": ["MMP1", "MMP3"]}], # PAD
    "34225646": [{"module_name": "Cardiac Contraction & Structure Module", "associated_phenotype": "Hypertrophic Cardiomyopathy Pathogenesis", "genes": ["MYH7", "MYBPC3", "TNNT2", "MYL2"]}, {"module_name": "Inflammatory & Immune Cell Signature", "associated_phenotype": "Cardiac Inflammation", "genes": ["JAK2", "C1R", "MS4A7", "MBP"]}],
    "36801909": [{"module_name": "Pro-inflammatory T-Cell Effector Module", "associated_phenotype": "B-Cell Recruitment & Ectopic Lymphoid Structure Formation", "genes": ["PDCD1", "MAF", "CXCL13", "CXCR5", "IL21", "POU2AF1", "TIGIT"]}],
    "40736520": [{"module_name": "Neutrophil & Leukocyte Activation Module", "associated_phenotype": "Neutrophil Degranulation and Migration", "genes": ["SLPI", "CAMP", "ANXA3", "RAB27A", "PSTPIP2", "FCGR3B", "S100A8"]}],
    "37876929": [{"module_name": "Immune Infiltration & Phagocytosis Hub", "associated_phenotype": "Immune Cell Activity in Glomeruli", "genes": ["CSF1R", "AIF1", "FCGR2B", "CYBB", "FCER1G", "FCGR3A", "TYROBP"]}, {"module_name": "Plasma Protein Module", "associated_phenotype": "Proteinuria", "genes": ["ALB", "ORM1", "APOA1"]}],
    "38041130": [{"module_name": "ECM Remodeling & Focal Adhesion Cluster", "associated_phenotype": "Tumor Microenvironment & Metastasis", "genes": ["COL1A1", "TIMP1", "SPP1", "COL1A2", "ITGA5", "THBS2", "SERPINE1"]}],
    "33503442": [{"module_name": "Core IFN-γ Signature Module", "associated_phenotype": "Interferon-Gamma Response and Inflammation", "genes": ["IRF1", "STAT1", "TYK2", "ICAM1", "GBP1", "CXCL9"]}]
}

# Defines ground truth annotations for hub genes (drug targets, kinases, biomarkers).
HUB_GENE_ANNOTATION_GROUND_TRUTH = {
    "31423162": {"drug_targets": ["PLK1", "TOP2A", "CDK1", "AURKA", "BIRC5"], "kinases": ["PLK1", "CDK1", "AURKA"], "biomarkers": ["TOP2A", "CXCL8", "CCNB1"]},
    "22409835": {"drug_targets": ["PTGS2", "JUN", "MMP1", "MMP3"], "kinases": ["JUN"], "biomarkers": ["PTGS2", "MMP1", "MMP3", "FOS"]}, # PAD
    "34225646": {"drug_targets": ["MYH7", "JAK2"], "kinases": ["JAK2"], "biomarkers": ["MYH7", "TNNT2"]},
    "36801909": {"drug_targets": ["PDCD1", "CTLA4", "ICOS", "CD40LG", "FAS"], "kinases": [], "biomarkers": ["CXCL13", "IL21", "TIGIT"]},
    "40736520": {"drug_targets": [], "kinases": ["PDK4"], "biomarkers": ["SLPI", "CAMP"]},
    "37876929": {"drug_targets": ["CSF1R", "CYBB"], "kinases": ["CSF1R"], "biomarkers": ["ALB", "AIF1"]},
    "38041130": {"drug_targets": [], "kinases": [], "biomarkers": ["TIMP1", "SPP1", "COL1A1"]},
    "33503442": {"drug_targets": ["TYK2", "GSK3A", "ICAM1"], "kinases": ["TYK2", "GSK3A"], "biomarkers": ["ICAM1", "IRF1"]}
}

# Defines ground truth summaries for individual analysis components (e.g., GO, KEGG).
COMPONENT_SUMMARIZATION_GROUND_TRUTH = {
    "31423162": [{"component": "KEGG", "summary": "The KEGG analysis indicated that the DEGs were mainly enriched in ‘Cell cycle’, ‘p53 signaling pathway’ and ‘Oocyte meiosis’."}, {"component": "GO", "summary": "Gene Ontology analysis revealed that the DEGs were primarily enriched in functions such as ‘cell division’ and other processes related to the cell cycle."}, {"component": "STRING", "summary": "The PPI network analysis identified a core module of highly interconnected hub genes, including PLK1, CDK1, and TOP2A, confirming their central role in the processes highlighted by pathway analysis."}],
    "22409835": [{"component": "GO", "summary": "Gene Ontology analysis revealed that the most significantly enriched biological process was 'inflammatory response', with other key terms including 'signal transduction', 'apoptosis', and 'cell proliferation'."}, {"component": "KEGG", "summary": "KEGG pathway analysis highlighted several key inflammatory pathways, including the 'MAPK signaling pathway', 'Toll-like receptor signaling pathway', and 'cytokine-cytokine receptor interaction'."}], # PAD
    "34225646": [{"component": "GO", "summary": "Functional enrichment analysis of the 8-gene signature revealed a strong association with cardiac muscle function, including GO terms like ‘cardiac muscle contraction’ and KEGG pathways like ‘Hypertrophic cardiomyopathy’."}],
    "36801909": [{"component": "KEGG", "summary": "Pathway analysis of the PD-1+ T cell signature revealed enrichment in pathways critical for T-cell function, such as 'Th1 and Th2 cell differentiation' and the 'T cell receptor signaling pathway'."}],
    "40736520": [{"component": "Reactome", "summary": "Pathway analysis using Reactome indicated that the DEGs were primarily enriched in pathways related to 'leukocyte transendothelial migration' and innate immunity."}, {"component": "GO", "summary": "GO analysis confirmed the role of neutrophils, showing enrichment in terms like 'neutrophil degranulation'."}],
    "37876929": [{"component": "KEGG", "summary": "KEGG analysis highlighted the 'NF-kappa B signaling pathway' and 'Toll-like receptor signaling pathway' as key dysregulated pathways."}, {"component": "GO", "summary": "GO analysis confirmed the importance of immune processes, showing enrichment in 'B cell activation' and other terms related to adaptive immunity."}, {"component": "STRING", "summary": "The PPI network of DEGs revealed a significant module related to immune cell activity, with hub genes like AIF1 and CSF1R being central to this cluster."}],
    "38041130": [{"component": "KEGG", "summary": "KEGG analysis of the prognostic signature genes revealed significant enrichment in the 'PI3K-Akt signaling pathway', 'Focal adhesion', and 'ECM-receptor interaction'."}],
    "33503442": [{"component": "GO", "summary": "Functional enrichment analysis of the top DEGs revealed a highly significant over-representation of GO terms related to the 'interferon-gamma-mediated signaling pathway', 'antigen processing and presentation', and 'response to virus'."}]
}

# Define file paths for the input CSVs.
reference_file = 'benchmark-gene-extraction-reference.csv'
degs_file = 'benchmark-gene-extraction-degs.csv'

# Load the source CSVs into pandas DataFrames within a try-except block for error handling.
try:
    # Print status message indicating the start of data loading.
    print("Loading data from CSV files...")
    # Load the reference metadata CSV into a DataFrame.
    df_reference = pd.read_csv(reference_file)
    # Print a header for displaying the first few rows of the reference data.
    print("\n--- Reference Data Head ---")
    # Display the first 2 rows of the reference DataFrame.
    print(df_reference.head(2))

    # Load the differentially expressed genes (DEGs) CSV into a DataFrame.
    df_degs = pd.read_csv(degs_file)
    # Print a header for displaying the DEGs data.
    print("\n--- DEGs Data Head (wide format) ---")
    # Display the first 2 rows of the DEGs DataFrame.
    print(df_degs.head(2))

    # Load the hub genes CSV into a DataFrame.
    df_hubgenes = pd.read_csv('benchmark-hub-genes-reference.csv') # Corrected filename assumed
    # Print a header for displaying the hub genes data.
    print("\n--- Hub Genes Data Head (wide format) ---")
    # Display the first 2 rows of the hub genes DataFrame.
    print(df_hubgenes.head(2))

    # Print a success message for data loading.
    print("\nData loaded successfully.")
# Catch the error if a file is not found.
except FileNotFoundError as e:
    # Print an error message indicating which file is missing.
    print(f"\nError: Could not find file {e.filename}. Please ensure all three CSV files are in the same directory as the script.")
    # Terminate the script.
    exit()

# Set up the main 'ODB/datasets' folder.
base_dir = "ODB"
# Join the base directory with 'datasets' to create the full path.
datasets_dir = os.path.join(base_dir, "datasets")
# Create the directory if it doesn't already exist.
os.makedirs(datasets_dir, exist_ok=True)
# Print a confirmation message.
print(f"\nBase directory '{datasets_dir}' is ready.")

# Loop through each row in the reference DataFrame to process each dataset.
for index, row in df_reference.iterrows():
    # Get the dataset ID from the current row.
    dataset_id = row['ID']
    # Get the PubMed ID (PMID) and cast it to an integer.
    pmid = int(row['PMID'])
    # Get the phenotype from the current row.
    phenotype = row['Phenotype']
    # Convert the PMID to a string for use as a dictionary key and column header.
    pmid_as_string = str(pmid)

    # Print a status message for the current dataset being processed.
    print(f"\n--- Processing Dataset: {dataset_id} (PMID: {pmid}) ---")

    # Create the specific subdirectory for this dataset within the 'datasets' directory.
    dataset_path = os.path.join(datasets_dir, dataset_id)
    # Create the subdirectory, ignoring errors if it already exists.
    os.makedirs(dataset_path, exist_ok=True)
    # Print a confirmation message for the created directory.
    print(f"  -> Created/verified directory: {dataset_path}")

    # Create the path for the 'input_genes.txt' file.
    input_genes_path = os.path.join(dataset_path, "input_genes.txt")
    # Check if the current PMID exists as a column in the DEGs DataFrame.
    if pmid_as_string in df_degs.columns:
        # Extract the list of DEGs for the current PMID, dropping any NaN values and converting to strings.
        current_degs = df_degs[pmid_as_string].dropna().astype(str).tolist()
        # Print the number of DEGs found and the first 5 for verification.
        print(f"  -> Found {len(current_degs)} DEGs. First 5: {current_degs[:5]}")
        
        # Open the 'input_genes.txt' file in write mode.
        with open(input_genes_path, 'w') as f:
            # Write each gene to the file on a new line.
            for gene in current_degs:
                f.write(f"{gene}\n")
        # Print a confirmation message that the file was generated.
        print(f"     -> Generated '{input_genes_path}'.")
    # If the PMID column is not found in the DEGs file.
    else:
        # Print a warning message.
        print(f"  -> WARNING: PMID {pmid} not found in DEGs file. Skipping input_genes.txt.")

    # Define the path for the 'ground_truth.json' file.
    ground_truth_path = os.path.join(dataset_path, "ground_truth.json")

    # Retrieve all curated ground truth data for the current PMID using .get() to avoid errors if a key is missing.
    ranked_hub_genes = RANKED_HUB_GENES_GROUND_TRUTH.get(pmid_as_string, [])
    narrative_terms = NARRATIVE_ENRICHMENT_GROUND_TRUTH.get(pmid_as_string, [])
    enrichment_categories = ENRICHMENT_CATEGORIZATION_GROUND_TRUTH.get(pmid_as_string, [])
    regulatory_edges = REGULATORY_NETWORK_GROUND_TRUTH.get(pmid_as_string, [])
    synthesis_text = BIOLOGICAL_SYNTHESIS_GROUND_TRUTH.get(pmid_as_string, "")
    hypotheses = HYPOTHESIS_GROUND_TRUTH.get(pmid_as_string, [])
    novel_insights = NOVEL_INSIGHTS_GROUND_TRUTH.get(pmid_as_string, [])
    analogous_systems = ANALOGOUS_SYSTEMS_GROUND_TRUTH.get(pmid_as_string, [])
    publication_title = PUBLICATION_TITLE_GROUND_TRUTH.get(pmid_as_string, "")
    system_nodes = INTEGRATED_SYSTEM_NODES_GROUND_TRUTH.get(pmid_as_string, [])
    hub_annotations = HUB_GENE_ANNOTATION_GROUND_TRUTH.get(pmid_as_string, {})
    component_summaries = COMPONENT_SUMMARIZATION_GROUND_TRUTH.get(pmid_as_string, [])
    
    # Print a status message indicating data assembly and show the first 5 hub genes.
    print(f"  -> Assembled all ground truth data. Ranked Hub Genes (first 5): {ranked_hub_genes[:5]}")

    # Structure the ground truth data into a dictionary for JSON export.
    ground_truth_data = {
        "pmid": str(pmid),
        "phenotype": phenotype,
        "publication_title": publication_title,
        "biological_process_synthesis": {
            "description": "Ground truth text for the main biological story.",
            "text": synthesis_text
        },
        "hub_genes_ranked": {
            "description": "Ranked list of hub genes as emphasized in the publication.",
            "genes": ranked_hub_genes
        },
        "enriched_pathways": {
            "description": "Key pathways/terms explicitly mentioned and discussed in the publication.",
            "terms": narrative_terms
        },
        "enrichment_categorization": {
             "description": "High-level functional themes used in the paper to group enrichment results.",
             "categories": enrichment_categories
        },
        "regulatory_network_edges": {
             "description": "List of directed TF->Target gene pairs mentioned in the publication.",
             "edges": regulatory_edges
        },
        "integrated_system_nodes": {
            "description": "Key gene modules identified in the author's overall system model.",
            "modules": system_nodes
        },
        "hypotheses": {
            "description": "Forward-looking or novel hypotheses from the paper.",
            "statements": hypotheses
        },
        "novel_insights": {
            "description": "Statements explicitly marked as novel or unexpected in the paper.",
            "statements": novel_insights
        },
        "analogous_systems": {
            "description": "Other diseases or phenotypes the paper compares its findings to.",
            "systems": analogous_systems
        },
        "hub_gene_annotation": {
            "description": "Classification of hub genes based on external database queries.",
            "drug_targets": hub_annotations.get("drug_targets", []),
            "kinases": hub_annotations.get("kinases", []),
            "biomarkers": hub_annotations.get("biomarkers", [])
        },
        "component_summaries": {
            "description": "Curated summaries of individual analysis components (KEGG, GO, etc.).",
            "summaries": component_summaries
        }
    }

    # Open the 'ground_truth.json' file in write mode.
    with open(ground_truth_path, 'w') as f:
        # Write the dictionary to the JSON file with an indent of 4 for readability.
        json.dump(ground_truth_data, f, indent=4)
    # Print a confirmation message that the file was generated.
    print(f"     -> Generated '{ground_truth_path}'.")

# Print a final message indicating the script has completed.
print("\n--- ODB setup complete. All tasks have been integrated and updated. ---")
