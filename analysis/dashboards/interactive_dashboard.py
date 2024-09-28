#!/usr/bin/env python

"""
interactive_dashboard.py: Create an interactive dashboard to explore the frequency
distribution of BIRADS scores across different imaging modalities.
This script reads a dataset of patients with BIRADS scores for mammography,
ultrasound, and MRI modalities. It then calculates the number of patients with
different combinations of modalities and creates an interactive dashboard.
The dashboard allows users to explore the distribution of BIRADS scores for
each modality and their combinations.

Key Functions:
- Load the dataset of patients with BIRADS scores for different modalities.
- Calculate the number of patients with different combinations of modalities.
- Create an interactive dashboard to explore the distribution of BIRADS scores.

Expected Usage:
- Run the script to generate an interactive dashboard.
- Open the dashboard in a web browser to explore the data interactively.
- Update the script to customize the dataset or modify the dashboard as needed.

Customization & Flexibility:
- The script can be adapted to work with different datasets or modalities.
- Additional metadata or information can be included in the dashboard.
- The dashboard layout, style, and interactivity can be customized based on requirements.

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
- Dash library: https://dash.plotly.com/
- Data visualization: https://en.wikipedia.org/wiki/Data_visualization
- Data analysis: https://en.wikipedia.org/wiki/Data_analysis

Example:
- Run the script to generate an interactive dashboard of BIRADS score distributions.
- Open the dashboard in a web browser to explore the data interactively.
- Update the script to customize the dataset or modify the dashboard as needed.
- python interactive_dashboard.py
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
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define the file names
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_12042023.csv"

# Define the folder to read data
dmb_repo_folder = os.path.join(root_dir, "dataset-multimodal-breast")
dmb_data_folder = os.path.join(dmb_repo_folder, "data")
dmb_birads_folder = os.path.join(dmb_data_folder, "birads")
dmb_birads_file = os.path.join(dmb_birads_folder, apbpc_csv_file)

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

# Function to prepare data for plotting
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

# Create a DataFrame for the charts
radar_df = pd.DataFrame({
  'BIRADS Score': [1, 2, 3, 4, 5],
  'Mammogram': mg_counts.values,
  'Ultrasound': us_counts.values,
  'MRI': mr_counts.values
})

# Initialize the Dash app
app = Dash(__name__)

app.layout = html.Div([
  html.H1("BIRADS Scores Distribution Dashboard"),
  dcc.Markdown("""
  **Overview:** This dashboard provides an interactive way to explore the frequency distribution of BIRADS scores across different imaging modalities (Mammogram, Ultrasound, MRI). Use the dropdown menu to select a modality and view the corresponding data in various charts and tables.
  """),
  dcc.Dropdown(
    id='modality-dropdown',
    options=[
      {'label': 'Mammogram', 'value': 'Mammogram'},
      {'label': 'Ultrasound', 'value': 'Ultrasound'},
      {'label': 'MRI', 'value': 'MRI'}
    ],
    value='Mammogram',
    clearable=False
  ),
  html.Br(),
  html.Div([
    html.Label("Select BIRADS Score Range:"),
    dcc.RangeSlider(
      id='score-range-slider',
      min=1,
      max=5,
      step=1,
      marks={i: str(i) for i in range(1, 6)},
      value=[1, 5]
    )
  ]),
  html.Br(),
  dcc.Graph(id='radar-chart'),
  html.Br(),
  dcc.Graph(id='bar-chart'),
  html.Br(),
  dcc.Graph(id='histogram-chart'),
  html.Br(),
  dash_table.DataTable(
    id='summary-table',
    columns=[{"name": i, "id": i} for i in radar_df.columns],
    data=radar_df.to_dict('records'),
    style_table={'overflowX': 'auto'},
    style_cell={'textAlign': 'center'}
  )
])

@app.callback(
  [Output('radar-chart', 'figure'),
   Output('bar-chart', 'figure'),
   Output('histogram-chart', 'figure'),
   Output('summary-table', 'data')],
  [Input('modality-dropdown', 'value'),
   Input('score-range-slider', 'value')]
)
def update_dashboard(modality, score_range):
  # Filter data based on selected score range
  filtered_df = radar_df[(radar_df['BIRADS Score'] >= score_range[0]) & 
                         (radar_df['BIRADS Score'] <= score_range[1])]
  
  # Ensure filtered_df is not empty to prevent errors
  if filtered_df.empty:
    filtered_df = pd.DataFrame({
      'BIRADS Score': [1, 2, 3, 4, 5],
      'Mammogram': [0, 0, 0, 0, 0],
      'Ultrasound': [0, 0, 0, 0, 0],
      'MRI': [0, 0, 0, 0, 0]
    })

  # Update radar chart
  radar_fig = go.Figure()
  radar_fig.add_trace(go.Scatterpolar(
    r=filtered_df[modality],
    theta=filtered_df['BIRADS Score'].astype(str),
    fill='toself',
    name=modality
  ))
  radar_fig.update_layout(
    title=f'Frequency Distribution of BIRADS Scores for {modality}',
    polar=dict(
      radialaxis=dict(visible=True, range=[0, max(mg_counts.max(), us_counts.max(), mr_counts.max())]),
      angularaxis=dict(direction='clockwise', type='category', tickmode='array', tickvals=['1', '2', '3', '4', '5'])
    ),
    showlegend=True
  )
  
  # Update bar chart
  bar_fig = px.bar(filtered_df, x='BIRADS Score', y=modality, title=f'Bar Chart of BIRADS Scores for {modality}')
  bar_fig.update_layout(
    xaxis_title='BIRADS Score',
    yaxis_title='Count'
  )
  
  # Update histogram
  histogram_col_map = {
    'Mammogram': MG_COLUMNS,
    'Ultrasound': US_COLUMNS,
    'MRI': MR_COLUMNS
  }
  
  hist_columns = histogram_col_map[modality]
  hist_df = df[hist_columns].stack().reset_index(name='BIRADS Score')
  hist_df = hist_df[hist_df['BIRADS Score'].astype(int).isin(range(score_range[0], score_range[1] + 1))]
  
  hist_fig = px.histogram(hist_df, x='BIRADS Score', nbins=5, title=f'Histogram of BIRADS Scores for {modality}')
  hist_fig.update_layout(
    xaxis_title='BIRADS Score',
    yaxis_title='Count'
  )

  # Update summary table
  table_data = filtered_df.to_dict('records')

  return radar_fig, bar_fig, hist_fig, table_data

# Run the app
if __name__ == '__main__':
  app.run_server(debug=True)

# End of file