#!/usr/bin/env python

"""
plot_birads_us_frequency.py: Plot the frequency of patients with
ultrasound images per BIRADS category.
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
import plotly.express as px
import os
import re  # Make sure to import the regular expressions library

# Define the file names
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_12042023.csv"
pbuf_web_file = "plot_birads_us_frequency.html"

# Set up paths for data input and output
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
data_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "birads")
data_file = os.path.join(data_dir, apbpc_csv_file)

# Define the folder to save web files
dp_repo_folder = os.path.join(root_dir, "data-pipeline")
dp_web_folder = os.path.join(dp_repo_folder, "web")
dp_pbuf_file = os.path.join(dp_web_folder, pbuf_web_file)

# Read the dataset
df = pd.read_csv(data_file)

# Columns for US images
us_columns = ['birads_usl', 'birads_usr']

def clean_and_max_birads(value):
  """ Clean the data by handling multiple entries in a cell and take the maximum BIRADS value. """
  if pd.isna(value):
    return None
  try:
    return max(int(x) for x in re.split(',|;', str(value)))  # Use regex to split on comma or semicolon
  except ValueError:
    return None

def count_us_images(value):
  """ Count the number of US images reported in a single cell assuming comma or semicolon separated entries. """
  if pd.isna(value):
    return 0
  return len(re.split(',|;', str(value)))

# Apply cleaning and extraction functions
for column in us_columns:
  df[f'max_{column}'] = df[column].apply(clean_and_max_birads)
  df[f'count_{column}'] = df[column].apply(count_us_images)

# Prepare data for plotting
plot_data = pd.DataFrame({
  'BIRADS': pd.concat([df[f'max_{col}'].reset_index(drop=True) for col in us_columns]),
  'US Type': pd.concat([pd.Series([col]*len(df)).reset_index(drop=True) for col in us_columns]),
  'Counts': pd.concat([df[f'count_{col}'].reset_index(drop=True) for col in us_columns])
})

# Drop NaN values
plot_data.dropna(subset=['BIRADS'], inplace=True)

# Convert BIRADS to integer type
plot_data['BIRADS'] = plot_data['BIRADS'].astype(int)

# Group by BIRADS category and US type for plotting
plot_data = plot_data.groupby(['BIRADS', 'US Type']).sum().reset_index()

# Create the plot
fig = px.bar(plot_data, x='BIRADS', y='Counts', color='US Type', barmode='group',
             title='Number of US Images per BIRADS Category',
             labels={'Counts':'Number of US Images', 'BIRADS':'BIRADS Category'},
             category_orders={"US Type": ["birads_usl", "birads_usr"]})  # This ensures USL and USR are side-by-side

# Write the figure
fig.write_html(dp_pbuf_file)

# End of file