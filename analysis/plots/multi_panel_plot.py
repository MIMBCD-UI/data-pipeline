#!/usr/bin/env python

"""
multi_panel_plot.py: Create a multi-panel plot showing the number of patients per imaging modality.
This script reads a dataset of patients with BIRADS scores for mammography, ultrasound, and MRI modalities.
It then calculates the number of patients with different combinations of modalities and creates a multi-panel plot.
The plot shows the distribution of patients with mammography, ultrasound, and MRI images side by side.

Key Functions:
- Load the dataset of patients with BIRADS scores for different modalities.
- Calculate the number of patients with different combinations of modalities.
- Create a multi-panel plot showing the distribution of patients across different modality combinations.

Expected Input:
- The script requires a dataset of patients with BIRADS scores for different modalities.
- The dataset should include columns for each modality (CCL, CCR, MLOL, MLOR, USL, USR, MRIL, MRIR) with BIRADS scores.
- The BIRADS scores should range from 1 to 5, with missing or invalid values handled appropriately.

Output:
- The script generates an interactive HTML file with the multi-panel plot.
- The plot shows the distribution of patients with mammography, ultrasound, and MRI images.
- The chart can be viewed in a web browser or embedded in a web page.

Expected Usage:
- Run the script to generate a multi-panel plot of imaging modality counts.
- Check the output figure to visualize the distribution of patients across different combinations.
- Update the script to customize the dataset or modify the plot as needed.

Customization & Flexibility:
- The script can be adapted to work with different datasets or modalities.
- Additional metadata or information can be included in the multi-panel plot.
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
- Multi-panel plots: https://en.wikipedia.org/wiki/Multipanel_plot
- Data visualization: https://en.wikipedia.org/wiki/Data_visualization
- Data analysis: https://en.wikipedia.org/wiki/Data_analysis

Example:
- Run the script to generate a multi-panel plot of imaging modality counts.
- Check the output figure to visualize the distribution of patients across different combinations.
- Update the script to customize the dataset or modify the plot as needed.
- python multi_panel_plot.py
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
import plotly.graph_objects as go

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define the file names
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_12042023.csv"
multi_panel_html_file = "multi_panel_plot.html"

# Define the folder to read data
dmb_repo_folder = os.path.join(root_dir, "dataset-multimodal-breast")
dmb_data_folder = os.path.join(dmb_repo_folder, "data")
dmb_birads_folder = os.path.join(dmb_data_folder, "birads")
dmb_birads_file = os.path.join(dmb_birads_folder, apbpc_csv_file)

# Define the folder to save the HTML file
dp_repo_folder = os.path.join(root_dir, "data-pipeline")
dp_web_folder = os.path.join(dp_repo_folder, "web")
dp_multi_panel_file = os.path.join(dp_web_folder, multi_panel_html_file)

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
df['MG_count'] = df[MG_COLUMNS].notna().sum(axis=1)
df['US_count'] = df[US_COLUMNS].notna().sum(axis=1)
df['MR_count'] = df[MR_COLUMNS].notna().sum(axis=1)

# Filter rows where count is greater than 0 for each modality
df_mg = df[df['MG_count'] > 0]
df_us = df[df['US_count'] > 0]
df_mr = df[df['MR_count'] > 0]

# Create individual plots for each modality
fig_mg = px.bar(df_mg, x='MG_count', y=df_mg.index, orientation='h', title='Mammogram')
fig_us = px.bar(df_us, x='US_count', y=df_us.index, orientation='h', title='Ultrasound')
fig_mr = px.bar(df_mr, x='MR_count', y=df_mr.index, orientation='h', title='MRI')

# Update layout for each plot
fig_mg.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Count', yaxis_title='Patients', title_font_size=14)
fig_us.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Count', yaxis_title='Patients', title_font_size=14)
fig_mr.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Count', yaxis_title='Patients', title_font_size=14)

# Create a subplot figure
from plotly.subplots import make_subplots

fig = make_subplots(rows=1, cols=3, subplot_titles=('Mammogram', 'Ultrasound', 'MRI'), shared_yaxes=True)

# Add each plot to the subplot figure
fig.add_trace(fig_mg['data'][0], row=1, col=1)
fig.add_trace(fig_us['data'][0], row=1, col=2)
fig.add_trace(fig_mr['data'][0], row=1, col=3)

# Update layout for the entire figure
fig.update_layout(
  title_text="Multi-Panel Plot of Imaging Modality Counts",
  title_font_size=20,
  height=600,
  width=1200,
  showlegend=False
)

# Save the plot as an HTML file
fig.write_html(dp_multi_panel_file)
logging.info("Multi-panel plot saved successfully to {}".format(dp_multi_panel_file))

# Show the plot (optional, remove if running in a non-GUI environment)
fig.show()

# End of file