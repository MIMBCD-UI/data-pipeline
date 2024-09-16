#!/usr/bin/env python

"""
main.py: Module for running the data processing pipeline.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.6.2"
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
from config.logging_config import setup_logging

# Mapping file name
mapping_fn = "mapping.csv"

# Define paths
# root_dir = Path(__file__).resolve().parents[2]
# source_folder = root_dir / "dicom-images-breast" / "known" / "raw"
# output_folder = root_dir / "dataset-multimodal-breast" / "data" / "curation" / "verifying"
# logs_folder = root_dir / "dicom-images-breast" / "data" / "logs" / "toprocess"
# mapping_file = root_dir / "dicom-images-breast" / "data" / "mapping" / mapping_fn

# Define paths (currently used in this script)
root_dir = Path(__file__).resolve().parents[2]
source_folder = root_dir / "dicom-images-breast" / "tests" / "test001"
output_folder = root_dir / "dataset-multimodal-breast" / "data" / "curation" / "unchecked"
logs_folder = root_dir / "dicom-images-breast" / "data" / "logs" / "toprocess"
mapping_file = root_dir / "dicom-images-breast" / "data" / "mapping" / mapping_fn

def setup_logging(logs_folder: Path):
  """
  Set up logging configuration.
  """
  logs_folder.mkdir(parents=True, exist_ok=True)
  logs_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
  log_file = logs_folder / f"log_{logs_timestamp}.log"

  logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
      logging.FileHandler(log_file),
      logging.StreamHandler()
    ]
  )
  logging.info(f"Logging to {log_file}")

def main():
  """
  Main function for running the data processing pipeline.
  """
  logging.info("Starting data processing pipeline...")
  logging.info(f"Source folder: {source_folder}")
  logging.info(f"Output folder: {output_folder}")
  logging.info(f"Mapping file: {mapping_file}")

  # Create output folder if it doesn't exist
  output_folder.mkdir(parents=True, exist_ok=True)

  # Process DICOM files
  try:
    process_directory(source_folder, output_folder, mapping_file)
    logging.info("Data processing pipeline completed.")
  except Exception as e:
    logging.error(f"An error occurred during processing: {e}")
    raise

if __name__ == "__main__":
  setup_logging(logs_folder)
  main()

# End of file