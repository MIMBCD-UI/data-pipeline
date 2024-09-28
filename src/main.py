#!/usr/bin/env python

"""
main.py: Optimized for handling large datasets with batch processing, enhanced logging, and memory monitoring.

This script initializes logging, sets up paths for input/output directories,
and runs the data processing pipeline by invoking the `process_directory` function
from the `processing.processor` module. It handles DICOM files and logs the results efficiently.

Improvements:
- Added memory monitoring before and after batch processing.
- Implemented explicit garbage collection to optimize memory usage for large datasets.
- Enhanced logging to trace each step in detail.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.7.3"  # Updated version after improvements
__status__ = "Development"
__credits__ = ["Carlos Santiago", "Catarina Barata", "Jacinto C. Nascimento", "Diogo Araújo"]

import logging
import os
import gc
import psutil  # For memory monitoring
from pathlib import Path
from datetime import datetime
from processing.processor import process_directory  # Import the main processing function

# Define constants for batch size and mapping file
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))  # Default batch size of 100, adjustable via environment variable

# Generate a timestamp for the mapping file name (e.g., "mapping_20240914_104530.csv")
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
MAPPING_FN = f"mapping_{timestamp}.csv"  # Timestamped file name

# Define root and folder paths for input/output/logging
ROOT_DIR = Path(__file__).resolve().parents[2]
SOURCE_FOLDER = ROOT_DIR / "dicom-images-breast" / "known" / "raw"
OUTPUT_FOLDER = ROOT_DIR / "dataset-multimodal-breast" / "data" / "curation" / "unexplored"
LOGS_FOLDER = ROOT_DIR / "dicom-images-breast" / "data" / "logs" / "toprocess"
MAPPING_FILE = ROOT_DIR / "dicom-images-breast" / "data" / "mapping" / MAPPING_FN

def setup_logging(logs_folder: Path):
  """
  Set up logging to log both to a file and the console.
  
  Args:
    logs_folder (Path): Directory where log files will be saved.
  
  Detailed logging configuration that saves logs to both the console and a timestamped file.
  """
  # Create logs folder if it doesn't exist
  logs_folder.mkdir(parents=True, exist_ok=True)

  # Create log file with timestamp to differentiate logs for each run
  logs_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
  log_file = logs_folder / f"log_{logs_timestamp}.log"

  # Set up logging configuration
  logging.basicConfig(
    level=logging.INFO,  # Log level set to INFO to capture general runtime events
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
      logging.FileHandler(log_file),  # Log messages to file
      logging.StreamHandler()         # Log messages to console
    ]
  )

  # Log that the logging system has been initialized
  logging.info(f"Logging initialized. Log file created at: {log_file}")

def monitor_memory(stage: str):
  """
  Monitor and log current memory usage at different stages of execution.
  
  Args:
    stage (str): Descriptive label of the current stage of the program for logging.
  
  Logs memory usage in both Resident Set Size (RSS) and Virtual Memory Size (VMS).
  """
  process = psutil.Process(os.getpid())  # Get the current process ID
  memory_info = process.memory_info()  # Get memory usage info
  logging.info(f"[{stage}] Memory usage: RSS={memory_info.rss / (1024 * 1024):.2f} MB, VMS={memory_info.vms / (1024 * 1024):.2f} MB")

def main():
  """
  Main function for running the data processing pipeline.
  
  Processes DICOM files in batches, monitors memory usage before and after processing,
  and ensures proper logging and error handling throughout the pipeline.
  """
  logging.info("Starting the data processing pipeline...")

  # Log folder paths
  logging.info(f"Source folder: {SOURCE_FOLDER}")
  logging.info(f"Output folder: {OUTPUT_FOLDER}")
  logging.info(f"Mapping file: {MAPPING_FILE}")
  logging.info(f"Batch size set to: {BATCH_SIZE}")

  # Ensure the output directory exists
  OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

  # Monitor memory usage at the start of processing
  monitor_memory("Initial")

  # Execute the processing pipeline in batches, with error handling
  try:
    # Process the directory using the defined batch size and mapping file
    logging.info("Starting batch processing...")
    process_directory(SOURCE_FOLDER, OUTPUT_FOLDER, MAPPING_FILE, BATCH_SIZE)
    logging.info("Batch processing completed successfully.")
  except Exception as e:
    # Log any exceptions encountered during processing
    logging.error(f"An error occurred during the data processing pipeline: {e}")
    raise
  finally:
    # Perform explicit garbage collection to free memory after processing
    logging.info("Initiating garbage collection...")
    gc.collect()
    logging.info("Garbage collection complete.")

    # Monitor memory usage after processing and garbage collection
    monitor_memory("Post-GC")

if __name__ == "__main__":
  # Set up logging before starting the main process
  setup_logging(LOGS_FOLDER)

  # Run the main function that starts the data processing pipeline
  main()

# End of file