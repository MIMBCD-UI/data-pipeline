#!/usr/bin/env python

"""
main.py: Optimized for handling large datasets with batch processing and improved logging.

This script initializes logging, sets up paths for input/output directories, 
and runs the data processing pipeline by invoking the `process_directory` function 
from the `processing.processor` module. It handles DICOM files and logs the results efficiently.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.7.1"  # Incremented version after improvements
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import logging
import os
import gc
import psutil  # Added for memory monitoring
from pathlib import Path
from datetime import datetime
from processing.processor import process_directory

# Define batch size for large dataset processing
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))  # Default batch size is 100, can be set via environment variable

# Define constant for mapping file name
MAPPING_FN = "mapping.csv"

# Define paths for input/output directories
ROOT_DIR = Path(__file__).resolve().parents[2]
SOURCE_FOLDER = ROOT_DIR / "dicom-images-breast" / "known" / "raw"
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

def monitor_memory():
  """
  Monitor and log current memory usage.
  """
  process = psutil.Process(os.getpid())
  memory_info = process.memory_info()
  logging.info(f"Memory usage: RSS={memory_info.rss / (1024 * 1024)} MB, VMS={memory_info.vms / (1024 * 1024)} MB")

def main():
  """
  Main function for running the data processing pipeline.
  It processes DICOM files from the source folder and maps them to an output folder.
  Supports batch processing for large datasets.
  """
  logging.info("Starting the data processing pipeline...")
  logging.info(f"Source folder: {SOURCE_FOLDER}")
  logging.info(f"Output folder: {OUTPUT_FOLDER}")
  logging.info(f"Mapping file: {MAPPING_FILE}")
  logging.info(f"Batch size: {BATCH_SIZE}")

  # Ensure the output folder exists
  OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

  # Monitor initial memory usage
  monitor_memory()

  # Execute the processing pipeline in batches
  try:
    process_directory(SOURCE_FOLDER, OUTPUT_FOLDER, MAPPING_FILE, BATCH_SIZE)
    logging.info("Data processing pipeline completed successfully.")
  except Exception as e:
    logging.error(f"An error occurred during the data processing pipeline: {e}")
    raise
  finally:
    # Explicit garbage collection to free memory
    gc.collect()
    logging.info("Garbage collection completed.")
    monitor_memory()  # Log memory usage after garbage collection

if __name__ == "__main__":
  setup_logging(LOGS_FOLDER)  # Initialize logging
  main()                      # Run the main pipeline function

# End of file