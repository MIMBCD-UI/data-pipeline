#!/usr/bin/env python

"""
plot_birads_mg_frequency.py: Plot the frequency of patients for
each MG type (CCL, CCR, MLOL, MLOR) with BIRADS scores from 1 to 5.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.6.0"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import pandas as pd
import plotly.graph_objects as go
import os

# Define the file names
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_12042023.csv"
pbmf_web_file = "plot_birads_mg_frequency.html"

# Set up paths for data input and output
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
data_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "birads")
data_file = os.path.join(data_dir, apbpc_csv_file)

# Define the folder to save web files
dp_repo_folder = os.path.join(root_dir, "data-pipeline")
dp_web_folder = os.path.join(dp_repo_folder, "web")
dp_pbmf_file = os.path.join(dp_web_folder, pbmf_web_file)

# Load dataset
df = pd.read_csv(data_file)

# Define columns for each MG type
MG_COLUMNS = {
  'CCL': 'birads_ccl',
  'CCR': 'birads_ccr',
  'MLOL': 'birads_mlol',
  'MLOR': 'birads_mlor'
}

# Function to prepare data for plotting
def prepare_data(column_name, label):
    # Handle multiple entries in cells, convert to float then int, calculate the maximum BIRADS score
    modality_data = df[column_name].apply(
        lambda x: max(map(int, map(float, str(x).replace(';', ',').split(',')))) if pd.notna(x) else None)
    modality_data = modality_data.dropna()
    modality_data = modality_data[modality_data.isin([1, 2, 3, 4, 5])]
    return modality_data.value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)

# Prepare data for each MG type
mg_data = {mg: prepare_data(MG_COLUMNS[mg], mg) for mg in MG_COLUMNS}

# Create a grouped bar chart
fig = go.Figure()

colors = ['indianred', 'lightblue', 'violet', 'yellowgreen']
for i, (mg, data) in enumerate(mg_data.items()):
    fig.add_trace(go.Bar(name=mg, x=data.index, y=data.values, marker_color=colors[i]))

# Update layout for grouped bar chart
fig.update_layout(
    barmode='group',
    title="Frequency of BIRADS Scores by MG Type",
    xaxis_title="BIRADS Score",
    yaxis_title="Frequency",
    legend_title="MG Type"
)

# Write the figure
fig.write_html(dp_pbmf_file)

# End of file