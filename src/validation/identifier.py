#!/usr/bin/env python

"""
identifier.py:

This script processes DICOM files located in the "checking" folder by extracting the SOP Instance UID
from each DICOM file. It then searches the "raw" folder and its subfolders to find a matching SOP Instance UID.
If a match is found, it reads the Real Patient ID from the matching file in the "raw" folder and compares
it to the Anonymized Patient ID in the "mamo_patients_mapping_data.csv" file. If a matching Anonymized Patient ID is found,
the script renames the DICOM file in the "checking" folder by replacing the Patient ID part of the filename
with the Anonymized Patient ID, and then moves the file to the "identified" folder. If no match is found, the DICOM file
is moved to the "unsolvable" folder. Optimized for large datasets with parallel processing and efficient file handling.

Key Functions:
- Load a CSV file containing patient mapping data.
- Load SOP Instance UIDs from the raw DICOM folder.
- Extract the Patient ID from DICOM metadata.
- Move files between folders based on processing results.
- Rename DICOM files with anonymized Patient IDs.

Expected Input:
- DICOM files in the "checking" folder and DICOM files in the "raw" folder.
- A CSV file containing mappings from Real Patient IDs to Anonymized Patient IDs.

Output:
- The script renames and moves DICOM files to the "identified" folder if a match is found.
- The script moves DICOM files to the "unsolvable" folder if no match is found.

Intended Use Case:
- This script is useful for identifying and renaming DICOM files with anonymized Patient IDs.
- It can be used to validate the anonymization process and ensure that the correct files are anonymized.

Customization & Flexibility:
- The script can be extended to handle additional metadata fields or file formats.
- It can be adapted to process other types of medical imaging data or metadata.
- The script can be integrated into a larger data curation pipeline for multimodal breast imaging data.

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
__version__ = "0.4.4"  # Version updated to reflect optimizations for file handling
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import csv
import logging
import pydicom
import shutil
import warnings
from urllib3.exceptions import NotOpenSSLWarning
from multiprocessing import Pool, cpu_count

# Configure detailed logging for debugging and tracking progress
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress irrelevant warnings (e.g., SSL warnings from urllib3)
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Constants for batch size and parallel processing
BATCH_SIZE = 500  # Reduced batch size to limit the number of open files
NUM_WORKERS = max(1, cpu_count() // 2)  # Reduce the number of workers to control open files

# Define key directories and paths holistically (cross-platform handling)
mapping_fn = "mamo_patients_mapping_data.csv"
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Directory paths for checking, raw, identified, and unsolvable files
checking_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "checking")
identified_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "identified")
unsolvable_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "unsolvable")
raw_dir = os.path.join(root_dir, "dicom-images-breast", "known", "raw")
mapping_csv = os.path.join(root_dir, "dicom-images-breast", "data", "mapping", mapping_fn)

# Ensure directories for identified and unsolvable files exist
os.makedirs(identified_dir, exist_ok=True)
os.makedirs(unsolvable_dir, exist_ok=True)

def normalize_string(s):
  """
  Normalize string by stripping whitespace, converting to lowercase,
  and removing special characters for consistent comparison.

  Args:
    s (str): The string to normalize.

  Returns:
    str: The normalized string.
  """
  return s.strip().lower().replace('\u200b', '')

def load_mapping(csv_file):
  """
  Load the mapping of real_patient_id to anonymized_patient_id from a CSV file.
  
  Args:
    csv_file (str): Path to the mapping CSV file.
  
  Returns:
    dict: A dictionary mapping real_patient_id to anonymized_patient_id.
  """
  logging.info(f"Loading mapping from {csv_file}")
  mapping = {}
  try:
    with open(csv_file, mode='r') as file:
      reader = csv.reader(file)
      next(reader)  # Skip the header row
      for row in reader:
        if len(row) >= 2:
          real_id = normalize_string(row[0])
          anonymized_id = normalize_string(row[1])
          mapping[real_id] = anonymized_id
      logging.info(f"Loaded {len(mapping)} mappings.")
  except Exception as e:
    logging.error(f"Failed to load mapping from {csv_file}: {e}")
  return mapping

def load_sop_instance_uid_map(raw_path):
  """
  Load SOP Instance UIDs from the raw directory into a dictionary for fast lookups.

  Args:
    raw_path (str): Path to the raw DICOM folder.

  Returns:
    dict: A dictionary mapping SOP Instance UIDs to file paths.
  """
  logging.info("Loading SOP Instance UIDs from raw directory...")
  sop_map = {}
  try:
    for root, _, files in os.walk(raw_path):
      for file in files:
        file_path = os.path.join(root, file)
        if is_dicom_file(file_path):
          sop_instance_uid = get_sop_instance_uid(file_path)
          if sop_instance_uid:
            sop_map[sop_instance_uid] = file_path
    logging.info(f"Loaded {len(sop_map)} SOP Instance UIDs from raw directory.")
  except Exception as e:
    logging.error(f"Error loading SOP Instance UIDs from raw directory: {e}")
  return sop_map

def is_dicom_file(filepath):
  """
  Check if a file is a valid DICOM file by attempting to read its metadata.

  Args:
    filepath (str): Path to the file.

  Returns:
    bool: True if the file is a valid DICOM file, False otherwise.
  """
  try:
    pydicom.dcmread(filepath, stop_before_pixels=True)
    return True
  except Exception as e:
    logging.warning(f"File {filepath} is not a valid DICOM file: {e}")
    return False

def get_sop_instance_uid(dicom_file):
  """
  Extract the SOP Instance UID from DICOM metadata.

  Args:
    dicom_file (str): Path to the DICOM file.

  Returns:
    str: SOP Instance UID if found, None otherwise.
  """
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    return dicom_data.get("SOPInstanceUID", None)
  except Exception as e:
    logging.warning(f"Failed to read SOP Instance UID from {dicom_file}: {e}")
    return None

def get_patient_id(dicom_file):
  """
  Extract the Patient ID from DICOM metadata.

  Args:
    dicom_file (str): Path to the DICOM file.

  Returns:
    str: Normalized Patient ID if found, "Unknown" otherwise.
  """
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    return normalize_string(dicom_data.get("PatientID", "Unknown"))
  except Exception as e:
    logging.warning(f"Failed to read Patient ID from {dicom_file}: {e}")
    return None

def move_file(src_path, dest_path):
  """
  Move a file from src_path to dest_path, creating directories if needed.

  Args:
    src_path (str): The source file path.
    dest_path (str): The destination file path.
  """
  if os.path.exists(src_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    try:
      shutil.move(src_path, dest_path)
      logging.info(f"File moved to {dest_path}")
    except Exception as e:
      logging.error(f"Failed to move file from {src_path} to {dest_path}: {e}")
  else:
    logging.warning(f"File not found: {src_path}")

def rename_file(file_name, new_patient_id):
  """
  Rename a file by replacing the Patient ID part of the filename with a new anonymized ID.

  Args:
    file_name (str): The original filename.
    new_patient_id (str): The new anonymized patient ID.

  Returns:
    str: The updated filename with the anonymized ID.
  """
  parts = file_name.split('_')
  if len(parts) > 0:
    parts[0] = new_patient_id  # Replace the first part with the anonymized_patient_id
  return '_'.join(parts)

def process_file(file, checking_file_path, sop_map, identified_path, unsolvable_path, mapping):
  """
  Process a single DICOM file, checking for matches and updating the patient ID as necessary.

  Args:
    file (str): Filename to process.
    checking_file_path (str): Path to the file in the checking folder.
    sop_map (dict): SOP Instance UID map.
    identified_path (str): Path to the identified folder.
    unsolvable_path (str): Path to the unsolvable folder.
    mapping (dict): Mapping of real_patient_id to anonymized_patient_id.
  """
  if not is_dicom_file(checking_file_path):
    move_file(checking_file_path, os.path.join(unsolvable_path, file))
    return

  sop_instance_uid_checking = get_sop_instance_uid(checking_file_path)
  if not sop_instance_uid_checking:
    move_file(checking_file_path, os.path.join(unsolvable_path, file))
    return

  raw_file_path = sop_map.get(sop_instance_uid_checking)

  if raw_file_path:
    real_patient_id = get_patient_id(raw_file_path)
    anonymized_patient_id = mapping.get(real_patient_id)

    if anonymized_patient_id:
      new_file_name = rename_file(file, anonymized_patient_id)
      identified_file_path = os.path.join(identified_path, new_file_name)
      move_file(checking_file_path, identified_file_path)
    else:
      move_file(checking_file_path, os.path.join(unsolvable_path, file))
  else:
    move_file(checking_file_path, os.path.join(unsolvable_path, file))

def batch_process_files(files_batch, sop_map, identified_path, unsolvable_path, mapping):
  """
  Process a batch of DICOM files.

  Args:
    files_batch (list): A batch of files to process.
    sop_map (dict): SOP Instance UID map.
    identified_path (str): Path to the identified folder.
    unsolvable_path (str): Path to the unsolvable folder.
    mapping (dict): Mapping of real_patient_id to anonymized_patient_id.
  """
  for file in files_batch:
    checking_file_path = os.path.join(checking_dir, file)
    process_file(file, checking_file_path, sop_map, identified_path, unsolvable_path, mapping)

def process_checking_files_in_batches(checking_path, sop_map, identified_path, unsolvable_path, mapping):
  """
  Process DICOM files in batches using parallel processing.

  Args:
    checking_path (str): Path to the checking folder.
    sop_map (dict): SOP Instance UID map.
    identified_path (str): Path to the identified folder.
    unsolvable_path (str): Path to the unsolvable folder.
    mapping (dict): Mapping of real_patient_id to anonymized_patient_id.
  """
  all_files = [file for file in os.listdir(checking_path) if os.path.isfile(os.path.join(checking_path, file))]
  total_files = len(all_files)
  logging.info(f"Total DICOM files to process: {total_files}")

  for i in range(0, total_files, BATCH_SIZE):
    batch = all_files[i:i + BATCH_SIZE]
    logging.info(f"Processing batch {i // BATCH_SIZE + 1} with {len(batch)} files.")
    
    # Use multiprocessing for parallel processing with file batches
    with Pool(processes=NUM_WORKERS, maxtasksperchild=100) as pool:
      pool.apply_async(batch_process_files, (batch, sop_map, identified_dir, unsolvable_dir, mapping))

if __name__ == '__main__':
  logging.info("Starting identifier processing...")
  mapping = load_mapping(mapping_csv)
  sop_map = load_sop_instance_uid_map(raw_dir)
  logging.info("Mapping and SOP Instance UIDs loaded!")
  process_checking_files_in_batches(checking_dir, sop_map, identified_dir, unsolvable_dir, mapping)
  logging.info("Identifier processing complete!")

# End of file