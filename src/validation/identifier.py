#!/usr/bin/env python

"""
identifier.py:

This script processes DICOM files located in the "checking" folder by extracting the SOP Instance UID
from each DICOM file. It then searches the "raw" folder and its subfolders to find a matching SOP Instance UID.
If a match is found, it reads the Real Patient ID from the matching file in the "raw" folder and compares
it to the Anonymized Patient ID in the "mapping.csv" file. If a matching Anonymized Patient ID is found,
the script renames the DICOM file in the "checking" folder by replacing the Patient ID part of the filename
with the Anonymized Patient ID, and then moves the file to the "identified" folder. If no match is found, the DICOM file
is moved to the "unsolvable" folder.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.3.9"
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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress warnings
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Mapping file name
mapping_fn = "mamo_patients_mapping_data.csv"

# Define file and directory paths
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
checking_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "checking")
identified_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "identified")
unsolvable_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "unsolvable")
raw_dir = os.path.join(root_dir, "dicom-images-breast", "tests", "test001")
mapping_csv = os.path.join(root_dir, "dicom-images-breast", "data", "mapping", mapping_fn)

# Ensure necessary directories exist
os.makedirs(unsolvable_dir, exist_ok=True)
os.makedirs(identified_dir, exist_ok=True)

# Debugging output for paths
logging.info(f"Checking directory: {checking_dir}")
logging.info(f"Identified directory: {identified_dir}")
logging.info(f"Raw directory: {raw_dir}")
logging.info(f"Mapping CSV: {mapping_csv}")

def normalize_string(s):
  """Normalize string by stripping whitespace, lowering case, and removing special characters."""
  return s.strip().lower().replace('\u200b', '')

def load_mapping(csv_file):
  """Load mapping of real_patient_id to anonymized_patient_id from CSV."""
  logging.info(f"Loading mapping from {csv_file}")
  mapping = {}
  try:
    with open(csv_file, mode='r') as file:
      reader = csv.reader(file)
      header = next(reader)  # Skip header
      if len(header) < 2:
        logging.error(f"Invalid CSV header: {header}. Expected at least 2 columns.")
        return {}
      for row in reader:
        if len(row) < 2:
          logging.warning(f"Invalid row in CSV: {row}. Expected at least 2 values.")
          continue
        real_id = normalize_string(row[0])
        anonymized_id = normalize_string(row[1])
        mapping[real_id] = anonymized_id
      logging.info(f"Loaded {len(mapping)} mappings.")
  except Exception as e:
    logging.error(f"Failed to load mapping from {csv_file}: {e}")
  return mapping

def load_sop_instance_uid_map(raw_path):
  """Load SOP Instance UIDs from the raw directory into a dictionary for quick lookups."""
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
  """Check if a file is a DICOM file by attempting to read it."""
  try:
    pydicom.dcmread(filepath, stop_before_pixels=True)
    return True
  except Exception as e:
    logging.warning(f"File {filepath} is not a DICOM file: {e}")
    return False

def get_sop_instance_uid(dicom_file):
  """Extract the SOP Instance UID from DICOM metadata."""
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    return dicom_data.get("SOPInstanceUID", None)
  except Exception as e:
    logging.warning(f"Failed to read SOP Instance UID from {dicom_file}: {e}")
    return None

def get_patient_id(dicom_file):
  """Extract the Patient ID from DICOM metadata."""
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    patient_id = normalize_string(dicom_data.get("PatientID", "Unknown"))
    logging.info(f"Extracted Patient ID (repr): {repr(patient_id)} from file: {dicom_file}")
    return patient_id
  except Exception as e:
    logging.warning(f"Failed to read Patient ID from {dicom_file}: {e}")
    return None

def move_file(src_path, dest_path):
  """Move the file from src_path to dest_path."""
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
  """Rename the file with the new patient ID."""
  parts = file_name.split('_')
  if len(parts) > 0:
    parts[0] = new_patient_id  # Replace the first part (anonymized_patient_id)
  else:
    logging.warning(f"File name {file_name} has unexpected format.")
  return '_'.join(parts)

def process_file(file, checking_file_path, sop_map, identified_path, unsolvable_path, mapping):
  """Process an individual file to match SOP Instance UID and update patient ID."""
  if not is_dicom_file(checking_file_path):
    logging.warning(f"File {checking_file_path} is not a valid DICOM file. Moving to unsolvable...")
    move_file(checking_file_path, os.path.join(unsolvable_path, file))
    return

  sop_instance_uid_checking = get_sop_instance_uid(checking_file_path)
  if sop_instance_uid_checking is None:
    logging.warning(f"No SOP Instance UID found for {checking_file_path}. Moving to unsolvable...")
    move_file(checking_file_path, os.path.join(unsolvable_path, file))
    return

  logging.info(f"Searching for matching SOP Instance UID: {sop_instance_uid_checking}")
  raw_file_path = sop_map.get(sop_instance_uid_checking)

  if raw_file_path:
    logging.info(f"Match found for SOP Instance UID: {sop_instance_uid_checking}")
    real_patient_id = get_patient_id(raw_file_path)

    if real_patient_id is None:
      logging.warning(f"Real Patient ID not found in {raw_file_path}. Moving to unsolvable...")
      move_file(checking_file_path, os.path.join(unsolvable_path, file))
      return

    anonymized_patient_id = mapping.get(real_patient_id)
    if anonymized_patient_id is None:
      logging.warning(f"No mapping found for Real Patient ID '{real_patient_id}'. Moving to unsolvable...")
      logging.info(f"Available mapping keys (first 5): {list(mapping.keys())[:5]}")
      move_file(checking_file_path, os.path.join(unsolvable_path, file))
      return

    # Rename and move the file
    new_file_name = rename_file(file, anonymized_patient_id)
    identified_file_path = os.path.join(identified_path, new_file_name)
    try:
      move_file(checking_file_path, identified_file_path)
    except Exception as e:
      logging.error(f"Failed to move file to identified folder: {e}. Moving to unsolvable...")
      move_file(checking_file_path, os.path.join(unsolvable_path, file))
  else:
    logging.info(f"No matching SOP Instance UID found for {checking_file_path}. Moving to unsolvable...")
    move_file(checking_file_path, os.path.join(unsolvable_path, file))

def process_checking_files(checking_path, sop_map, identified_path, unsolvable_path, mapping):
  """Process files in the checking directory and find matching SOP Instance UIDs."""
  logging.info(f"Processing DICOM files in checking directory: {checking_path}")
  for root, _, files in os.walk(checking_path):
    for file in files:
      checking_file_path = os.path.join(root, file)
      process_file(file, checking_file_path, sop_map, identified_path, unsolvable_path, mapping)

if __name__ == '__main__':
  logging.info("Starting identifier processing...")
  mapping = load_mapping(mapping_csv)
  sop_map = load_sop_instance_uid_map(raw_dir)
  logging.info("Mapping and SOP Instance UIDs loaded!")
  process_checking_files(checking_dir, sop_map, identified_dir, unsolvable_dir, mapping)
  logging.info("Identifier processing complete!")

# End of file