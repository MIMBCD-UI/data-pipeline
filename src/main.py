#!/usr/bin/env python

"""
main.py: Module for running the data processing pipeline.
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

import logging
import os
from datetime import datetime
from processor import process_directory

# Set up logging
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
source_folder = os.path.join(root_dir, "dicom-images-breast", "pipeline", "processed")
output_folder = os.path.join(root_dir, "dataset-multimodal-breast", "tests", "dicom")

# Define the folder to save logs
logs_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
logs_fs = f"log_{logs_timestamp}.log"
logs_folder = os.path.join(root_dir, "dicom-images-breast", "data", "logs")
logs_file = os.path.join(logs_folder, logs_fs)

# Create logs folder if it doesn't exist
if not os.path.exists(logs_folder):
  os.makedirs(logs_folder)

# Set up logging to write to the file and console
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(logs_file)
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add both handlers to the root logger
logging.root.addHandler(file_handler)
logging.root.addHandler(console_handler)
logging.root.setLevel(logging.INFO)

# Define the mapping file path
logging.info("Loading mapping file...")

# Load mapping file
mapping_file = os.path.join(root_dir, "dicom-images-breast", "data", "mapping", "mapping.csv")
logging.info(f"Mapping file loaded: {mapping_file}")

# Main function
def main():
  """
  Main function for running the data processing pipeline.
  """
  logging.info("Starting data processing pipeline...")
  logging.info(f"Source folder: {source_folder}")
  logging.info(f"Output folder: {output_folder}")
  logging.info(f"Mapping file: {mapping_file}")

  # Create output folder if it doesn't exist
  if not os.path.exists(output_folder):
    os.makedirs(output_folder)

  # Process DICOM files
  process_directory(source_folder, output_folder, mapping_file)
  logging.info("Data processing pipeline completed.")

if __name__ == "__main__":
  main()

# End of file