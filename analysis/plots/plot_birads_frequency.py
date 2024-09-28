#!/usr/bin/env python

"""
plot_birads_frequency.py: Plot frequency of patients with MGs, US images, and MRIs for each BIRADS score,
handling multiple entries per cell by considering the highest BIRADS score and multiple delimiters.

This script reads a dataset of patients with BIRADS scores for mammography, ultrasound, and MRI modalities.
It then calculates the number of patients with different combinations of modalities and plots a stacked bar chart.

Key Functions:
- Load the dataset of patients with BIRADS scores for different modalities.
- Calculate the number of patients with different combinations of modalities.
- Plot a stacked bar chart showing the distribution of patients across different modality combinations.

Expected Usage:
- Run the script to generate a stacked bar chart of imaging modality combinations.
- Check the output figure to visualize the distribution of patients across different combinations.
- Update the script to customize the dataset or modify the plot as needed.

Customization & Flexibility:
- The script can be adapted to work with different datasets or modalities.
- Additional metadata or information can be included in the stacked bar chart.
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
- Stacked bar charts: https://en.wikipedia.org/wiki/Stacked_bar_chart
- Data visualization: https://en.wikipedia.org/wiki/Data_visualization
- Data analysis: https://en.wikipedia.org/wiki/Data_analysis

Example:
- Run the script to generate a stacked bar chart of imaging modality combinations.
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
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_17042023.csv"
pbf_web_file = "plot_birads_frequency.html"

# Set up paths for data input and output
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
data_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "birads")
data_file = os.path.join(data_dir, apbpc_csv_file)

# Define the folder to save web files
dp_repo_folder = os.path.join(root_dir, "data-pipeline")
dp_web_folder = os.path.join(dp_repo_folder, "web")
dp_pbf_file = os.path.join(dp_web_folder, pbf_web_file)

# Load dataset
df = pd.read_csv(data_file)

# Define columns for each modality related to BIRADS scoring
MG_COLUMNS = ['birads_ccl', 'birads_ccr', 'birads_mlol', 'birads_mlor']
US_COLUMNS = ['birads_usl', 'birads_usr']
MR_COLUMNS = ['birads_mril', 'birads_mrir']

# Function to prepare data for plotting
def prepare_data(columns, label):
  # Process each column to handle multiple entries and convert to maximum BIRADS score
  # Supports different delimiters for list values in cells
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

# Create a grouped bar chart
fig = go.Figure(data=[
  go.Bar(name='MG', x=mg_counts.index, y=mg_counts.values, marker_color='indianred', text=mg_counts.values, textposition='auto', textfont=dict(size=22)),
  go.Bar(name='US', x=us_counts.index, y=us_counts.values, marker_color='lightblue', text=us_counts.values, textposition='auto', textfont=dict(size=22)),
  go.Bar(name='MR', x=mr_counts.index, y=mr_counts.values, marker_color='#2F4F4F', text=mr_counts.values, textposition='auto', textfont=dict(size=22))
])

# Change the bar mode to group
fig.update_layout(
  barmode='group',
  title=dict(text="Frequency of BIRADS Scores by Medical Imaging Modality", font=dict(size=24)),
  xaxis=dict(title=dict(text="BIRADS Score", font=dict(size=20)), tickfont=dict(size=18)),
  yaxis=dict(title=dict(text="Frequency of Images", font=dict(size=20)), tickfont=dict(size=18)),
  legend=dict(title=dict(text="Modality", font=dict(size=28)), font=dict(size=24))
)

# Write the figure
fig.write_html(dp_pbf_file)

# End of file