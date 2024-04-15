#!/usr/bin/env python

"""
plot_birads_mri_frequency.py: Plot the frequency of patients with MRI images per BIRADS category.
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
import re

# Define the file names
apbpc_csv_file = "anonymized_patients_birads_preliminary_curation_12042023.csv"
pbmf_web_file = "plot_birads_mri_frequency.html"

# Set up paths for data input and output
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
data_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "birads")
data_file = os.path.join(data_dir, apbpc_csv_file)

# Define the folder to save web files
dp_repo_folder = os.path.join(root_dir, "data-pipeline")
dp_web_folder = os.path.join(dp_repo_folder, "web")
dp_pbmf_file = os.path.join(dp_web_folder, pbmf_web_file)

# Read the dataset
df = pd.read_csv(data_file)

# Columns for MRI images
mri_columns = ['birads_mril', 'birads_mrir']

def clean_and_max_birads(value):
  """ Clean the data by handling multiple entries in a cell and take the maximum BIRADS value. """
  print(f"Original value: {value}")  # Debug print
  if pd.isna(value):
    return None
  try:
    values = re.split(',|;', str(value).strip())  # Strip whitespace and split
    max_value = max(int(float(x)) for x in values if x.strip())  # Convert to float first to avoid int conversion issues
    print(f"Processed values: {values}, Max: {max_value}")  # Debug print
    return max_value
  except ValueError as e:
    print(f"Error processing value '{value}': {e}")  # Debug print
    return None

# Note: Use this updated function and re-run your script.

# Apply cleaning and extraction functions
for column in mri_columns:
  df[f'max_{column}'] = df[column].apply(clean_and_max_birads)

print("Data after cleaning and taking max BIRADS value per column:")
print(df[[f'max_{col}' for col in mri_columns]].head())

# Prepare data for plotting
plot_data = pd.DataFrame({
  'BIRADS': pd.concat([df[f'max_{col}'] for col in mri_columns]).reset_index(drop=True)
})

print("Combined BIRADS data from all columns:")
print(plot_data.head())

# Drop NaN values
plot_data.dropna(inplace=True)

# Convert BIRADS to integer type
plot_data['BIRADS'] = plot_data['BIRADS'].astype(int)

# Count the frequency of each BIRADS category
plot_data = plot_data['BIRADS'].value_counts().reset_index()
plot_data.columns = ['BIRADS', 'Frequency']

print("Frequency of each BIRADS category:")
print(plot_data.head())

# Plot
fig = px.bar(plot_data, x='BIRADS', y='Frequency', title='Frequency of Patients with MRI per BIRADS Category',
             labels={'Frequency':'Number of Patients', 'BIRADS':'BIRADS Category'})

# Write the figure to an HTML file
fig.write_html(dp_pbmf_file)

# End of file