#!/usr/bin/env python

"""
plot_birads_mg_frequency.py: Plot the frequency of patients for
each MG type (CCL, CCR, MLOL, MLOR) with BIRADS scores from 1 to 5.
This script reads a dataset of patients with BIRADS scores for mammography,
ultrasound, and MRI modalities. It then calculates the number of patients
with different combinations of modalities and plots a stacked bar chart.

Key Functions:
- Load the dataset of patients with BIRADS scores for different modalities.
- Calculate the number of patients with different combinations of modalities.
- Plot a stacked bar chart showing the distribution of patients across different modality combinations.

Expected Input:
- The script requires a dataset of patients with BIRADS scores for different modalities.
- The dataset should include columns for each modality (CCL, CCR, MLOL, MLOR) with BIRADS scores.
- The BIRADS scores should range from 1 to 5, with missing or invalid values handled appropriately.

Output:
- The script generates an interactive HTML file with the stacked bar chart.
- The chart shows the distribution of patients across different modality combinations.
- The chart can be viewed in a web browser or embedded in a web page.

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
- Check the output figure to visualize the distribution of patients across different combinations.
- Update the script to customize the dataset or modify the plot as needed.
- python plot_birads_mg_frequency.py
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