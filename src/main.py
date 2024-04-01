#!/usr/bin/env python

"""
main.py: Module for running the data processing pipeline.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.5.0"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import logging
import os
from datetime import datetime
from processor import process_directory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define source, output, and mapping file paths
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# source_folder = os.path.join(root_dir, "dicom-images-breast", "known", "raw")
# output_folder = os.path.join(root_dir, "dataset-multimodal-breast", "tests", "dicom")
source_folder = os.path.join(root_dir, "dicom-images-breast", "tests", "testing_data-pipeline_t002")
output_folder = os.path.join(root_dir, "dataset-multimodal-breast", "tests", "test002")

# Add timestamp to mapping file name
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
mapping_fn = f"mapping_{timestamp}.csv"
mapping_file = os.path.join(root_dir, "dicom-images-breast", "data", "mapping", mapping_fn)

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

# Run main function if script is called directly from the command line
if __name__ == "__main__":
  main()
