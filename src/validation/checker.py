#!/usr/bin/env python

"""
checker.py:

This script compares anonymized and non-anonymized DICOM files to identify matching files based on the `SOPInstanceUID` metadata.
It is optimized for large datasets by using batch processing, lazy loading of files, and memory management techniques.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "1.0.3"
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import csv
import logging
import warnings
import pydicom
import shutil
from urllib3.exceptions import NotOpenSSLWarning
from multiprocessing import Pool, cpu_count

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress warnings for clean output
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Define supported modalities
SUPPORTED_MODALITIES = ['US', 'MG', 'MRI']

# Mapping file name
mapping_fn = "mamo_patients_mapping_data.csv"

# Define paths
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
anonymized_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "unchecked")
checked_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "checked")
unsolvable_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "unsolvable")
non_anonymized_dir = os.path.join(root_dir, "dicom-images-breast", "known", "raw")
output_csv_file = os.path.join(root_dir, "dicom-images-breast", "data", "checking", mapping_fn)

BATCH_SIZE = 1000  # Define the size of each batch for processing large datasets

def is_supported_modality(dicom_file):
  """Check if the DICOM file is of a supported modality (US, MG, MRI)."""
  dicom_modality = dicom_file.get("Modality", "").upper()
  return dicom_modality in SUPPORTED_MODALITIES

def is_dicom_file(filepath):
  """Check if a file is a valid DICOM file by attempting to read it."""
  try:
    pydicom.dcmread(filepath, stop_before_pixels=True)
    return True
  except Exception as e:
    logging.warning(f"Not a DICOM file: {filepath} - {e}")
    return False

def index_non_anonymized_files(non_anonymized_files):
  """Index non-anonymized files by SOPInstanceUID for fast lookup."""
  sop_uid_index = {}
  for non_anonymized_file in non_anonymized_files:
    try:
      metadata = pydicom.dcmread(non_anonymized_file, stop_before_pixels=True)
      if hasattr(metadata, 'SOPInstanceUID'):
        sop_uid = metadata.SOPInstanceUID
        sop_uid_index[sop_uid] = non_anonymized_file
    except Exception as e:
      logging.warning(f"Failed to read non-anonymized file: {non_anonymized_file} - {e}")
  logging.info(f"Indexed {len(sop_uid_index)} non-anonymized files.")
  return sop_uid_index

def batch_process_dicom_files(anonymized_files_batch, sop_uid_index):
  """Process a batch of anonymized DICOM files and compare them with the indexed non-anonymized files."""
  for anonymized_filepath in anonymized_files_batch:
    if not is_dicom_file(anonymized_filepath):
      continue
    anonymized_dicom = pydicom.dcmread(anonymized_filepath)
    
    if not hasattr(anonymized_dicom, 'SOPInstanceUID'):
      logging.warning(f"SOPInstanceUID not found in anonymized DICOM file: {anonymized_filepath}")
      move_to_unsolvable(anonymized_filepath)
      continue
    
    if not is_supported_modality(anonymized_dicom):
      logging.info(f"Skipping unsupported modality for file: {anonymized_filepath}")
      continue

    anonymized_sop_uid = anonymized_dicom.SOPInstanceUID
    match_filepath = sop_uid_index.get(anonymized_sop_uid)

    if match_filepath:
      move_to_checked(anonymized_filepath)
    else:
      move_to_unsolvable(anonymized_filepath)

def compare_dicom_files_in_batches(anonymized_path, non_anonymized_path):
  """Compare anonymized and non-anonymized DICOM files in batches to handle large datasets efficiently."""
  anonymized_files = get_all_files(anonymized_path)
  non_anonymized_files = get_all_files(non_anonymized_path)

  # Index non-anonymized files by SOPInstanceUID for fast lookup
  sop_uid_index = index_non_anonymized_files(non_anonymized_files)
  
  # Use multiprocessing to process batches in parallel
  num_batches = len(anonymized_files) // BATCH_SIZE + 1
  pool = Pool(cpu_count())

  for i in range(num_batches):
    batch = anonymized_files[i * BATCH_SIZE: (i + 1) * BATCH_SIZE]
    pool.apply_async(batch_process_dicom_files, args=(batch, sop_uid_index))

  pool.close()
  pool.join()
  logging.info("All batches processed.")

def get_all_files(directory):
  """Get all files recursively from a directory."""
  file_list = []
  for root, _, files in os.walk(directory):
    for file in files:
      file_list.append(os.path.join(root, file))
  return file_list

def move_to_checked(filepath):
  """Move the file to the 'checked' directory."""
  filename = os.path.basename(filepath)
  dest_path = os.path.join(checked_dir, filename)
  move_file(filepath, dest_path)
  logging.info(f"File {filename} moved to checked directory.")

def move_to_unsolvable(filepath):
  """Move the file to the 'unsolvable' directory."""
  filename = os.path.basename(filepath)
  dest_path = os.path.join(unsolvable_dir, filename)
  move_file(filepath, dest_path)
  logging.info(f"File {filename} moved to unsolvable directory.")

def move_file(src, dest):
  """Move a file from src to dest."""
  if os.path.exists(src):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.move(src, dest)
    logging.info(f"File moved to {dest}")
  else:
    logging.warning(f"File not found: {src}")

if __name__ == '__main__':
  compare_dicom_files_in_batches(anonymized_dir, non_anonymized_dir)
  logging.info("Comparison complete!")

# End of file