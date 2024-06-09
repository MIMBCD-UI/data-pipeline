#!/usr/bin/env python

"""
stacked_bar_chart.py: Plot the number of patients per imaging modality.
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
import plotly.graph_objects as go

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define the file names
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_12042023.csv"
pm_web_file = "stacked_bar_chart.html"

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

# Count non-empty valid entries for each modality per patient
df['MG'] = df[MG_COLUMNS].notna().any(axis=1)
df['US'] = df[US_COLUMNS].notna().any(axis=1)
df['MR'] = df[MR_COLUMNS].notna().any(axis=1)

# Create a new column for modality combination
df['modality_combination'] = df.apply(
  lambda row: '_'.join([mod for mod in ['MG', 'US', 'MR'] if row[mod]]), axis=1)

# Count the number of patients for each combination
combination_counts = df['modality_combination'].value_counts().reset_index()
combination_counts.columns = ['Combination', 'Number of Patients']

# Define the order of combinations for the stacked bar chart
combination_order = ['MG', 'US', 'MR', 'MG_US', 'MG_MR', 'US_MR', 'MG_US_MR']

# Prepare data for plotting
plot_data = combination_counts.set_index('Combination').reindex(combination_order).fillna(0)

# Create the stacked bar chart
fig = go.Figure()

for combination in combination_order:
  fig.add_trace(go.Bar(
    x=['Patients'],
    y=[plot_data.loc[combination, 'Number of Patients']],
    name=combination,
    text=[plot_data.loc[combination, 'Number of Patients']],
    textposition='auto'
  ))

# Update layout
fig.update_layout(
  barmode='stack',
  title='Number of Patients per Imaging Modality Combination',
  xaxis_title='',
  yaxis_title='Number of Patients',
  legend_title='Modality Combination'
)

# Save the plot as an HTML file
fig.write_html(dp_pm_file)
logging.info("Plot displayed successfully.")

# End of file