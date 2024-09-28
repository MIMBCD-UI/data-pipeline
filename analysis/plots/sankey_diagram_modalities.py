#!/usr/bin/env python

"""
sankey_diagram_modalities.py: Plot a Sankey diagram showing the flow of patients through different imaging modalities.

This script reads a dataset of patients with BIRADS scores for mammography, ultrasound, and MRI modalities.
It then calculates the number of patients with different combinations of modalities and plots a Sankey diagram.

Key Functions:
- Load the dataset of patients with BIRADS scores for different modalities.
- Calculate the number of patients with different combinations of modalities.
- Plot a Sankey diagram showing the flow of patients through different imaging modalities.

Expected Usage:
- Run the script to generate a Sankey diagram of imaging modality combinations.
- Check the output figure to visualize the flow of patients through different modalities.
- Update the script to customize the dataset or modify the plot as needed.

Customization & Flexibility:
- The script can be adapted to work with different datasets or modalities.
- Additional metadata or information can be included in the Sankey diagram.
- The plot style, colors, and labels can be customized based on requirements.

Performance & Compatibility:
- The script is optimized for performance when handling large datasets.
- It uses the Plotly library to create interactive and visually appealing plots.
- The script is compatible with Python 3.6+ and common data science libraries.

Best Practices & Maintenance:
- The script follows best practices for data visualization and analysis.
- It provides a clear and informative representation of imaging modality data.
- The script is well-documented and can be easily maintained or extended.

Notes:
- This script is part of a data analysis pipeline for multimodal breast imaging data.
- It is designed to visualize the flow of patients through different imaging modalities.
- The script can be integrated into a larger data processing or analysis workflow.

References:
- Plotly library: https://plotly.com/python/
- Sankey diagrams: https://en.wikipedia.org/wiki/Sankey_diagram
- Data visualization: https://en.wikipedia.org/wiki/Data_visualization
- Data analysis: https://en.wikipedia.org/wiki/Data_analysis
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
import plotly.io as pio

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define the file names
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_12042023.csv"
sankey_png_file = "sankey_diagram_modalities.png"

# Define the folder to read data
dmb_repo_folder = os.path.join(root_dir, "dataset-multimodal-breast")
dmb_data_folder = os.path.join(dmb_repo_folder, "data")
dmb_birads_folder = os.path.join(dmb_data_folder, "birads")
dmb_birads_file = os.path.join(dmb_birads_folder, apbpc_csv_file)

# Define the folder to save the PNG file
dp_repo_folder = os.path.join(root_dir, "data-pipeline")
dp_fig_folder = os.path.join(dp_repo_folder, "figures")
dp_sankey_file = os.path.join(dp_fig_folder, sankey_png_file)

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

# Create a new column for modality combination
df['modality_combination'] = df.apply(
  lambda row: '_'.join([mod for mod in ['MG', 'US', 'MR'] if row[mod]]), axis=1)

# Count the number of patients for each combination
combination_counts = df['modality_combination'].value_counts().reset_index()
combination_counts.columns = ['Combination', 'Number of Patients']

# Define the mapping from abbreviations to full names
abbreviation_to_full = {
  'MG': 'Mammogram',
  'US': 'Ultrasound',
  'MR': 'MRI'
}

# Prepare data for the Sankey diagram
label_list = ['Mammogram', 'Ultrasound', 'MRI']
source = []
target = []
value = []

# Add source, target, and value for each combination
for _, combo in combination_counts.iterrows():
  modalities = combo['Combination'].split('_')
  for j in range(len(modalities)):
    for k in range(j + 1, len(modalities)):
      source.append(label_list.index(abbreviation_to_full[modalities[j]]))
      target.append(label_list.index(abbreviation_to_full[modalities[k]]))
      value.append(combo['Number of Patients'])

# Create the Sankey diagram
fig = go.Figure(go.Sankey(
  node=dict(
    pad=15,
    thickness=20,
    line=dict(color="black", width=0.5),
    label=label_list,
    hovertemplate='%{label}',  # Ensure that the label is displayed in hover
  ),
  link=dict(
    source=source,
    target=target,
    value=value,
    hovertemplate='Value: %{value}',  # Display the value in hover
  )
))

# Update layout
fig.update_layout(
  title_text="Sankey Diagram of Imaging Modality Combinations",
  font=dict(size=14),  # Increase the font size for better readability
  annotations=[
    dict(
      x=0.1,
      y=1.05,
      xref='paper',
      yref='paper',
      text="Mammogram",
      showarrow=False,
      font=dict(size=14)
    ),
    dict(
      x=0.5,
      y=1.05,
      xref='paper',
      yref='paper',
      text="Ultrasound",
      showarrow=False,
      font=dict(size=14)
    ),
    dict(
      x=0.9,
      y=1.05,
      xref='paper',
      yref='paper',
      text="MRI",
      showarrow=False,
      font=dict(size=14)
    )
  ]
)

# Save the plot as a PNG file
pio.write_image(fig, dp_sankey_file, format='png', width=1200, height=800, scale=2)
logging.info("Sankey diagram saved successfully to {}".format(dp_sankey_file))

# End of file