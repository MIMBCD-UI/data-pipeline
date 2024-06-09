#!/usr/bin/env python

"""
venn_diagram_modalities.py: Plot a Venn diagram of patients with different combinations of imaging modalities.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.6.0"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import logging
import pandas as pd
from matplotlib_venn import venn3
import matplotlib.pyplot as plt

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define the file names
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_12042023.csv"
venn_diagram_file = "venn_diagram_modalities.png"

# Define the folder to read data
dmb_repo_folder = os.path.join(root_dir, "dataset-multimodal-breast")
dmb_data_folder = os.path.join(dmb_repo_folder, "data")
dmb_birads_folder = os.path.join(dmb_data_folder, "birads")
dmb_birads_file = os.path.join(dmb_birads_folder, apbpc_csv_file)

# Define the folder to save the Venn diagram
dp_repo_folder = os.path.join(root_dir, "data-pipeline")
dp_fig_folder = os.path.join(dp_repo_folder, "figures")
dp_venn_file = os.path.join(dp_fig_folder, venn_diagram_file)

# Ensure the output directory exists
os.makedirs(dp_fig_folder, exist_ok=True)

# Load your dataset
try:
  df = pd.read_csv(dmb_birads_file)
  logging.info("Data loaded successfully from {}".format(dmb_birads_file))
except Exception as e:
  logging.error(f"Failed to load data: {e}")
  raise SystemExit(e)

# Define columns for each modality
MG_COLUMNS = ['birads_ccl', 'birads_ccr', 'birads_mlol', 'birads_mlor']
US_COLUMNS = ['birads_usl', 'birads_usr']
MR_COLUMNS = ['birads_mril', 'birads_mrir']

# Count non-empty valid entries for each modality per patient
df['MG'] = df[MG_COLUMNS].notna().any(axis=1)
df['US'] = df[US_COLUMNS].notna().any(axis=1)
df['MR'] = df[MR_COLUMNS].notna().any(axis=1)

# Calculate the counts for the Venn diagram
mg_only = df['MG'] & ~df['US'] & ~df['MR']
us_only = ~df['MG'] & df['US'] & ~df['MR']
mr_only = ~df['MG'] & ~df['US'] & df['MR']
mg_us = df['MG'] & df['US'] & ~df['MR']
mg_mr = df['MG'] & ~df['US'] & df['MR']
us_mr = ~df['MG'] & df['US'] & df['MR']
mg_us_mr = df['MG'] & df['US'] & df['MR']

# Prepare the counts for the Venn diagram
venn_counts = {
  '100': mg_only.sum(),
  '010': us_only.sum(),
  '001': mr_only.sum(),
  '110': mg_us.sum(),
  '101': mg_mr.sum(),
  '011': us_mr.sum(),
  '111': mg_us_mr.sum()
}

# Plot the Venn diagram
plt.figure(figsize=(10, 10))
venn = venn3(subsets=venn_counts, set_labels=('Mammogram', 'Ultrasound', 'MRI'))

# Update layout and save the plot
plt.title('Venn Diagram of Imaging Modality Combinations')
plt.savefig(dp_venn_file)
logging.info("Venn diagram saved successfully to {}".format(dp_venn_file))

# Show the plot (optional, remove if running in a non-GUI environment)
plt.show()

# End of file