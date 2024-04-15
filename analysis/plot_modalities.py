#!/usr/bin/env python

"""
plot_modalities.py: Plot the number of patients per imaging modality.
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
import time
import logging
import pandas as pd
import plotly.express as px

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define the file names
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_12042023.csv"
pm_web_file = "plot_modalities.html"

# Define the folder to read data
dmb_repo_folder = os.path.join(root_dir, "dataset-multimodal-breast")
dmb_data_folder = os.path.join(dmb_repo_folder, "data")
dmb_birads_folder = os.path.join(dmb_data_folder, "birads")
dmb_birads_file = os.path.join(dmb_birads_folder, apbpc_csv_file)

# Define the folder to save web files
dp_repo_folder = os.path.join(root_dir, "data-pipeline")
dp_web_folder = os.path.join(dp_repo_folder, "web")
dp_pm_file = os.path.join(dp_web_folder, pm_web_file)

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

# Clean data: Convert non-numeric entries to NaN and count only numeric entries
# for col in MG_COLUMNS + US_COLUMNS + MR_COLUMNS:
#   df[col] = pd.to_numeric(df[col], errors='coerce')

# Count non-empty valid entries for each modality per patient
df['MG_count'] = df[MG_COLUMNS].notna().sum(axis=1)
df['US_count'] = df[US_COLUMNS].notna().sum(axis=1)
df['MR_count'] = df[MR_COLUMNS].notna().sum(axis=1)

# Determine number of patients per modality
modality_counts = {
  'Mammogram': (df['MG_count'] > 0).sum(),
  'Ultrasound': (df['US_count'] > 0).sum(),
  'MRI': (df['MR_count'] > 0).sum()
}

# Prepare data for plotting
modality_df = pd.DataFrame(list(modality_counts.items()), columns=['Modality', 'Number of Patients'])

fig = px.bar(modality_df, x='Modality', y='Number of Patients', title='Number of Patients per Imaging Modality')
fig.write_html(dp_pm_file)
logging.info("Plot displayed successfully.")

# End of File