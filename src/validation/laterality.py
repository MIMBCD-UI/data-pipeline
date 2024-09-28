#!/usr/bin/env python

"""
laterality.py:

This script processes DICOM files by checking for the "Modality" and "Laterality" DICOM tags. It ensures that medical imaging data 
is correctly linked and organized, particularly in the context of anonymization, for both US (ultrasound) and MG (mammography) modalities.

This version is optimized for massive datasets through batch processing, parallel processing, and optimized I/O operations.

Key Functions:
- Process a directory of DICOM files in batches using the `process_directory` function.
- Extract metadata from DICOM files and check for the "Modality" and "Laterality" tags.
- Organize DICOM files based on the "Modality" and "Laterality" tags for further analysis.

Expected Input:
- A directory containing DICOM files to be processed.
- An output directory to save organized DICOM files.
- A batch size for processing a specified number of files at a time.

Output:
- Organized DICOM files saved in the output directory based on the "Modality" and "Laterality" tags.
- Log files with detailed information on the processing steps and results.

Intended Use Case:
- This script is designed for processing large datasets of DICOM files efficiently.
- It can be used to organize and prepare medical imaging data for research or analysis.
- The script is optimized for handling memory-intensive tasks and monitoring resource usage.

Customization & Flexibility:
- The batch size can be adjusted based on the available system resources.
- Additional logging configurations or output formats can be added for specific use cases.
- The script can be extended to support other types of medical imaging data or metadata.

Performance & Compatibility:
- The script is designed for performance and efficiency when processing large datasets.
- It uses multiprocessing to parallelize the file processing and optimize resource utilization.

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
__version__ = "0.4.3"
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import logging
import pydicom
import shutil
import warnings
from multiprocessing import Pool, cpu_count
from urllib3.exceptions import NotOpenSSLWarning

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress specific warnings
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
warnings.simplefilter("ignore")  # Suppress all warnings for clean output

# Define paths for DICOM processing
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
verifying_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "verifying")
incongruities_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "incongruities")
unsolvable_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "unsolvable")

BATCH_SIZE = 500  # Define the size of each batch for processing
NUM_WORKERS = max(1, cpu_count() - 1)  # Use available CPU cores, leaving one for system processes

# Logging paths for debugging
logging.info(f"Verifying directory: {verifying_dir}")
logging.info(f"Incongruities directory: {incongruities_dir}")
logging.info(f"Unsolvable directory: {unsolvable_dir}")

def is_dicom_file(filepath):
  """Check if the given file is a valid DICOM file."""
  try:
    pydicom.dcmread(filepath, stop_before_pixels=True)
    return True
  except (pydicom.errors.InvalidDicomError, Exception):
    return False

def get_dicom_tag(dicom_file, tag):
  """Extract a specified DICOM tag from the DICOM metadata."""
  try:
    dicom_data = pydicom.dcmread(dicom_file, stop_before_pixels=True)
    return dicom_data.get(tag, "")
  except Exception as e:
    logging.warning(f"Error reading {tag} from {dicom_file}: {e}")
    return ""

def move_file(filepath, folder, laterality=None):
  """Move a file to a specified folder, renaming it if necessary."""
  filename = os.path.basename(filepath)
  if laterality:
    filename = rename_file(filename, laterality)
  dest_path = os.path.join(folder, filename)
  
  if os.path.exists(filepath):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.move(filepath, dest_path)
    logging.debug(f"Moved file to {dest_path}")
  else:
    logging.warning(f"File not found: {filepath}")

def rename_file(filename, laterality):
  """Rename the file by inserting the laterality if not already present."""
  parts = filename.split('_')
  if laterality not in parts:
    parts.insert(2, laterality.strip('_'))
    return '_'.join(parts)
  return filename

def process_dicom_file(dicom_file_path):
  """Process a single DICOM file for laterality and modality."""
  if not is_dicom_file(dicom_file_path):
    logging.debug(f"Skipping non-DICOM file: {dicom_file_path}")
    return

  modality = get_dicom_tag(dicom_file_path, "Modality")
  if modality not in ["US", "MG"]:
    logging.debug(f"Unsupported modality {modality} for file {dicom_file_path}")
    return

  laterality = get_dicom_tag(dicom_file_path, "ImageLaterality")
  if laterality in ["L", "R"]:
    move_file(dicom_file_path, incongruities_dir, laterality)
  else:
    move_file(dicom_file_path, unsolvable_dir, laterality="_NA_")

def batch_process(files_batch):
  """Process a batch of DICOM files in parallel."""
  for dicom_file_path in files_batch:
    process_dicom_file(dicom_file_path)

def process_dicom_files(directory):
  """Process DICOM files in batches, with optional parallel processing."""
  all_files = []
  for root, _, files in os.walk(directory):
    all_files.extend([os.path.join(root, file) for file in files])

  total_files = len(all_files)
  logging.info(f"Total DICOM files to process: {total_files}")

  # Process in batches
  for i in range(0, total_files, BATCH_SIZE):
    batch = all_files[i:i + BATCH_SIZE]
    logging.info(f"Processing batch {i // BATCH_SIZE + 1} with {len(batch)} files.")
    
    with Pool(processes=NUM_WORKERS) as pool:
      pool.map(batch_process, [batch])

if __name__ == '__main__':
  logging.info("Starting DICOM file processing...")
  process_dicom_files(verifying_dir)
  logging.info("Processing complete!")

# End of file