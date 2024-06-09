#!/usr/bin/env python

"""
radar_chart.py: Plot a radar chart showing the frequency distribution of BIRADS scores across different imaging modalities.
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
import plotly.graph_objects as go

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define the file names
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_12042023.csv"
radar_chart_html_file = "radar_chart.html"

# Define the folder to read data
dmb_repo_folder = os.path.join(root_dir, "dataset-multimodal-breast")
dmb_data_folder = os.path.join(dmb_repo_folder, "data")
dmb_birads_folder = os.path.join(dmb_data_folder, "birads")
dmb_birads_file = os.path.join(dmb_birads_folder, apbpc_csv_file)

# Define the folder to save the HTML file
dp_repo_folder = os.path.join(root_dir, "data-pipeline")
dp_web_folder = os.path.join(dp_repo_folder, "web")
dp_radar_chart_file = os.path.join(dp_web_folder, radar_chart_html_file)

# Load your dataset
try:
  df = pd.read_csv(dmb_birads_file)
  logging.info("Data loaded successfully from {}".format(dmb_birads_file))
except Exception as e:
  logging.error(f"Failed to load data: {e}")
  raise SystemExit(e)

# Define columns for each modality related to BIRADS scoring
MG_COLUMNS = ['birads_ccl', 'birads_ccr', 'birads_mlol', 'birads_mlor']
US_COLUMNS = ['birads_usl', 'birads_usr']
MR_COLUMNS = ['birads_mril', 'birads_mrir']

# Function to prepare data for radar chart
def prepare_data(columns, label):
  # Process each column to handle multiple entries and convert to maximum BIRADS score
  modality_data = df[columns].apply(lambda col: col.apply(
    lambda x: max(map(int, map(float, str(x).replace(';', ',').split(',')))) if pd.notna(x) else None))
  modality_data = modality_data.stack().reset_index(name=label)
  # Filter non-null and valid BIRADS scores (1 to 5)
  modality_data = modality_data[modality_data[label].isin([1, 2, 3, 4, 5])]
  # Count occurrences
  return modality_data.groupby(label).size().reindex([1, 2, 3, 4, 5], fill_value=0)

# Prepare data for each modality
mg_counts = prepare_data(MG_COLUMNS, 'BIRADS_MG')
us_counts = prepare_data(US_COLUMNS, 'BIRADS_US')
mr_counts = prepare_data(MR_COLUMNS, 'BIRADS_MR')

# Create a DataFrame for the radar chart
radar_df = pd.DataFrame({
  'BIRADS Score': ['1', '2', '3', '4', '5'],
  'Mammogram': mg_counts.values,
  'Ultrasound': us_counts.values,
  'MRI': mr_counts.values
})

# Create the radar chart
fig = go.Figure()

fig.add_trace(go.Scatterpolar(
  r=radar_df['Mammogram'],
  theta=radar_df['BIRADS Score'],
  fill='toself',
  name='Mammogram'
))

fig.add_trace(go.Scatterpolar(
  r=radar_df['Ultrasound'],
  theta=radar_df['BIRADS Score'],
  fill='toself',
  name='Ultrasound'
))

fig.add_trace(go.Scatterpolar(
  r=radar_df['MRI'],
  theta=radar_df['BIRADS Score'],
  fill='toself',
  name='MRI'
))

# Update layout with custom angles
fig.update_layout(
  title='Frequency Distribution of BIRADS Scores by Modality',
  polar=dict(
    radialaxis=dict(visible=True, range=[0, max(mg_counts.max(), us_counts.max(), mr_counts.max())]),
    angularaxis=dict(direction='clockwise', type='category', tickmode='array', tickvals=['1', '2', '3', '4', '5'])
  ),
  showlegend=True
)

# Save the plot as an HTML file
fig.write_html(dp_radar_chart_file)
logging.info("Radar chart saved successfully to {}".format(dp_radar_chart_file))

# Show the plot (optional, remove if running in a non-GUI environment)
fig.show()

# End of file