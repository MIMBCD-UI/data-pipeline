#!/usr/bin/env python

"""
main.py: Module for running the data processing pipeline.

This script initializes logging, sets up paths for input/output directories, 
and runs the data processing pipeline by invoking the `process_directory` function 
from the `processing.processor` module.

It processes DICOM files and logs the results into a specific directory.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.6.4"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import logging
from pathlib import Path
from datetime import datetime
from processing.processor import process_directory

# Define constant for mapping file name
MAPPING_FN = "mapping.csv"

# Define paths for input/output directories
# ROOT_DIR = Path(__file__).resolve().parents[2]
# SOURCE_FOLDER = ROOT_DIR / "dicom-images-breast" / "known" / "raw"
# OUTPUT_FOLDER = ROOT_DIR / "dataset-multimodal-breast" / "data" / "curation" / "unexplored"
# LOGS_FOLDER = ROOT_DIR / "dicom-images-breast" / "data" / "logs" / "toprocess"
# MAPPING_FILE = ROOT_DIR / "dicom-images-breast" / "data" / "mapping" / MAPPING_FN

# Define paths for testing input/output directories
ROOT_DIR = Path(__file__).resolve().parents[2]
SOURCE_FOLDER = ROOT_DIR / "dicom-images-breast" / "tests" / "test001"
OUTPUT_FOLDER = ROOT_DIR / "dataset-multimodal-breast" / "data" / "curation" / "unexplored"
LOGS_FOLDER = ROOT_DIR / "dicom-images-breast" / "data" / "logs" / "toprocess"
MAPPING_FILE = ROOT_DIR / "dicom-images-breast" / "data" / "mapping" / MAPPING_FN

def setup_logging(logs_folder: Path):
  """
  Set up logging configuration to log both to a file and the console.

  Args:
    logs_folder (Path): The directory where log files will be saved.
  """
  # Create the logs folder if it doesn't exist
  logs_folder.mkdir(parents=True, exist_ok=True)

  # Define log file with a timestamp
  logs_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
  log_file = logs_folder / f"log_{logs_timestamp}.log"

  # Set up logging configuration
  logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
      logging.FileHandler(log_file),  # Log to file
      logging.StreamHandler()         # Log to console
    ]
  )
  logging.info(f"Logging initialized. Log file: {log_file}")

def main():
  """
  Main function for running the data processing pipeline.
  It processes DICOM files from the source folder and maps them to an output folder.
  """
  logging.info("Starting the data processing pipeline...")
  logging.info(f"Source folder: {SOURCE_FOLDER}")
  logging.info(f"Output folder: {OUTPUT_FOLDER}")
  logging.info(f"Mapping file: {MAPPING_FILE}")

  # Ensure the output folder exists
  OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

  # Execute the processing pipeline
  try:
    process_directory(SOURCE_FOLDER, OUTPUT_FOLDER, MAPPING_FILE)
    logging.info("Data processing pipeline completed successfully.")
  except Exception as e:
    logging.error(f"An error occurred during the data processing pipeline: {e}")
    raise

if __name__ == "__main__":
  setup_logging(LOGS_FOLDER)  # Initialize logging
  main()                      # Run the main pipeline function

# End of file