#!/usr/bin/env python

"""
heatmap_modalities.py: Plot the frequency of patients with different combinations of imaging modalities using a heatmap.
This script reads a dataset of patients with BIRADS scores for mammography, ultrasound, and MRI modalities.
It then calculates the number of patients with different combinations of modalities and plots a heatmap.

Key Functions:
- Load the dataset of patients with BIRADS scores for different modalities.
- Calculate the number of patients with different combinations of modalities.
- Plot a heatmap showing the frequency of patients with different imaging modality combinations.

Expected Usage:
- Run the script to generate a heatmap of imaging modality combinations.
- Check the output figure to visualize the frequency of patients across different combinations.
- Update the script to customize the dataset or modify the plot as needed.

Customization & Flexibility:
- The script can be adapted to work with different datasets or modalities.
- Additional metadata or information can be included in the heatmap.
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
- It is designed to visualize the distribution of imaging modalities for patients.
- The script can be integrated into a larger data processing or analysis workflow.

References:
- Plotly library: https://plotly.com/python/
- Heatmaps: https://en.wikipedia.org/wiki/Heat_map
- Data visualization: https://en.wikipedia.org/wiki/Data_visualization
- Data analysis: https://en.wikipedia.org/wiki/Data_analysis

Example:
- Run the script to generate a heatmap of imaging modality combinations.
- Check the output figure to visualize the frequency of patients across different combinations.
- Update the script to customize the dataset or modify the plot as needed.
- python heatmap_modalities.py
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
import plotly.express as px

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define the file names
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_12042023.csv"
heatmap_web_file = "heatmap_modalities.html"

# Define the folder to read data
dmb_repo_folder = os.path.join(root_dir, "dataset-multimodal-breast")
dmb_data_folder = os.path.join(dmb_repo_folder, "data")
dmb_birads_folder = os.path.join(dmb_data_folder, "birads")
dmb_birads_file = os.path.join(dmb_birads_folder, apbpc_csv_file)

# Define the folder to save web files
dp_repo_folder = os.path.join(root_dir, "data-pipeline")
dp_web_folder = os.path.join(dp_repo_folder, "web")
dp_heatmap_file = os.path.join(dp_web_folder, heatmap_web_file)

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

# Prepare data for the heatmap
heatmap_data = combination_counts.pivot_table(index='Combination', values='Number of Patients', aggfunc='sum').fillna(0)

# Create the heatmap
fig = px.imshow(
  heatmap_data.values.reshape(-1, 1),
  labels=dict(x="Imaging Modality Combination", y="Combination", color="Number of Patients"),
  x=['Patients'],
  y=combination_counts['Combination'],
  color_continuous_scale='Viridis'
)

# Update layout
fig.update_layout(
  title='Frequency of Patients with Different Imaging Modality Combinations',
  xaxis_title='',
  yaxis_title='Combination',
  coloraxis_colorbar=dict(title="Number of Patients")
)

# Save the plot as an HTML file
fig.write_html(dp_heatmap_file)
logging.info("Heatmap displayed successfully.")

# End of file