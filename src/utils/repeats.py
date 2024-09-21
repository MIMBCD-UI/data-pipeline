#!/usr/bin/env python

"""
repeats.py:

This script processes a CSV file and identifies rows where the 'anonymized_patient_id' or 'real_patient_id' columns contain repeated values.
The script then prints these rows for further analysis.

Intended Use Case:
- This script is useful for identifying duplicate entries in either the 'anonymized_patient_id' or 'real_patient_id' columns of a CSV file, 
  which can be critical for data cleaning, validation, or analysis tasks.

Expected Input:
- A CSV file containing the data to be analyzed.

"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.2.4"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import logging
import pandas as pd
import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress warnings
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Mapping file name
mapping_fn = "mamo_patients_mapping_data.csv"

# Define paths
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
mapping_csv = os.path.join(root_dir, "data-images-breast", "data", "mapping", mapping_fn)

# Debugging output for paths
logging.info(f"Mapping CSV: {mapping_csv}")

# Define the column names you want to check for repeats
columns_to_check = ['anonymized_patient_id', 'real_patient_id']  # List of columns to check

def find_repeats(csv_file, columns):
  """Find and print rows in the CSV where the specified columns have repeated values."""
  logging.info(f"Loading data from {csv_file}")
  try:
    df = pd.read_csv(csv_file)
    
    for column in columns:
      logging.info(f"Counting occurrences of values in column: {column}")
      value_counts = df[column].value_counts()
      
      logging.info(f"Filtering repeated values in column: {column}")
      repeated_values = value_counts[value_counts > 1].index
      
      if repeated_values.empty:
        logging.info(f"No repeated values found in column: {column}")
      else:
        logging.info(f"Printing rows with repeated values in column: {column}")
        repeated_rows = df[df[column].isin(repeated_values)]
        print(f"\nRepeated rows in column '{column}':\n")
        print(repeated_rows)
        
  except Exception as e:
    logging.error(f"An error occurred: {e}")

if __name__ == '__main__':
  logging.info("Starting repeat detection...")
  find_repeats(mapping_csv, columns_to_check)
  logging.info("Repeat detection complete!")

# End of file