#!/usr/bin/env python

"""
plot_birads_mri_side_by_side.py: Plot the frequency of patients with MRI images per BIRADS category, displayed side-by-side.
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
pbms_web_file = "plot_birads_mri_side_by_side.html"

# Set up paths for data input and output
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
data_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "birads")
data_file = os.path.join(data_dir, apbpc_csv_file)

# Define the folder to save web files
dp_repo_folder = os.path.join(root_dir, "data-pipeline")
dp_web_folder = os.path.join(dp_repo_folder, "web")
dp_pbms_file = os.path.join(dp_web_folder, pbms_web_file)

# Read the dataset
df = pd.read_csv(data_file)
print("Initial data:", df.head())

# Columns for MRI images
mri_columns = ['birads_mril', 'birads_mrir']

# Function to clean and find max BIRADS
def clean_and_max_birads(value):
  if pd.isna(value):
      return None
  try:
    numbers = re.split(r'[\s,;]+', str(value).strip())
    valid_numbers = [int(float(x)) for x in numbers if re.match(r'^\d+\.?\d*$', x)]
    return max(valid_numbers) if valid_numbers else None
  except ValueError as e:
    print(f"Error processing value '{value}': {e}")
    return None

# Apply cleaning function
for column in mri_columns:
  df[f'max_{column}'] = df[column].apply(clean_and_max_birads)
  print(f"Processed data in {column}:", df[f'max_{column}'].head())

# Prepare data for plotting
plot_data = pd.DataFrame({
  'BIRADS': pd.concat([df[f'max_{col}'] for col in mri_columns], ignore_index=True),
  'MRI Type': pd.concat([pd.Series([col]*len(df)) for col in mri_columns], ignore_index=True)
})
print("Combined BIRADS data from all columns:", plot_data.head())

# Drop NaN values
plot_data.dropna(inplace=True)
print("Data after dropping NaNs:", plot_data.head())

# Convert BIRADS to integer type
plot_data['BIRADS'] = plot_data['BIRADS'].astype(int)

# Group and count
plot_data = plot_data.groupby(['BIRADS', 'MRI Type']).size().reset_index(name='Counts')
print("Frequency of each BIRADS category:", plot_data)

# Plot
fig = px.bar(plot_data, x='BIRADS', y='Counts', color='MRI Type', barmode='group',
             title='Number of MRI Observations per BIRADS Category',
             labels={'Counts':'Number of Observations', 'BIRADS':'BIRADS Category'})

# Save the plot as an HTML file
fig.write_html(dp_pbms_file)  # Save the plot as an HTML file

# End of file