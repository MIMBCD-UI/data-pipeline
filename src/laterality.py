#!/usr/bin/env python

"""
laterality.py:

This script processes DICOM files by converting anonymized patient IDs to their corresponding real patient IDs, extracting specific metadata (such as laterality and instance number), and then renaming and moving the files accordingly. It is designed to ensure that medical imaging data is correctly linked and organized, particularly in the context of anonymization, making it useful for research projects like the MIMBCD-UI initiative.

Key Functions:
- Load mappings between anonymized and real patient IDs from a CSV file.
- Validate and extract metadata (e.g., laterality, instance number) from DICOM files.
- Rename files based on extracted metadata and move them to the appropriate directory.

Intended Use Case:
- This script is essential in environments where it is necessary to maintain connections between anonymized and non-anonymized medical imaging data, ensuring proper file management and data integrity within research projects like the MIMBCD-UI initiative.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.2.3"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago", "Catarina Barata", "Jacinto C. Nascimento", "Diogo Araújo"]

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

# Define paths
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
non_anonymized_dir = os.path.join(root_dir, "dicom-images-breast", "known", "raw")
checking_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "checking")
checked_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "checked")
mapping_csv = os.path.join(root_dir, "dataset-multimodal-breast", "data", "inconsistencies", mapping_fn)

# Debugging output for paths
logging.info(f"Mapping CSV: {mapping_csv}")
logging.info(f"Non-anonymized directory: {non_anonymized_dir}")
logging.info(f"Checking directory: {checking_dir}")
logging.info(f"Checked directory: {checked_dir}")

def load_mapping(csv_file):
  """Load mapping of anonymized_patient_id to real_patient_id from CSV."""
  logging.info(f"Loading mapping from {csv_file}")
  mapping = {}
  with open(csv_file, mode='r') as file:
    reader = csv.reader(file)
    logging.info(f"Header: {next(reader)}")
    next(reader)  # Skip header
    logging.info(f"Reading mapping data...")
    for row in reader:
      logging.info(f"Row: {row}")
      real_id, anonymized_id = row
      logging.info(f"Real ID: {real_id}, Anonymized ID: {anonymized_id}")
      mapping[anonymized_id] = real_id
      logging.info(f"Mapping: {mapping}")
  return mapping

def is_dicom_file(filepath):
  """Check if a file is a DICOM file by attempting to read it."""
  logging.info(f"Checking if file {filepath} is a DICOM file")
  try:
    logging.info(f"Reading DICOM file {filepath}")
    pydicom.dcmread(filepath)
    logging.info(f"File {filepath} is a DICOM file")
    return True
  except Exception:
    logging.info(f"File {filepath} is not a DICOM file")
    return False

def get_laterality(dicom_file):
  """Extract laterality from DICOM metadata."""
  logging.info(f"Getting laterality from DICOM file {dicom_file}")
  try:
    logging.info(f"Reading DICOM file {dicom_file}")
    dicom_data = pydicom.dcmread(dicom_file)
    logging.info(f"Reading DICOM file {dicom_file} metadata")
    return dicom_data.get("ImageLaterality", "Unknown")
  except Exception as e:
    logging.warning(f"Failed to read DICOM file {dicom_file}: {e}")
    return "Unknown"

def get_instance_number(dicom_file):
  """Extract instance number from DICOM metadata."""
  logging.info(f"Getting instance number from DICOM file {dicom_file}")
  try:
    logging.info(f"Reading DICOM file {dicom_file}")
    dicom_data = pydicom.dcmread(dicom_file)
    logging.info(f"Reading DICOM file {dicom_file} metadata")
    return dicom_data.get("InstanceNumber", None)
  except Exception as e:
    logging.warning(f"Failed to read DICOM file {dicom_file}: {e}")
    return None

def check_patient_id(dicom_file, anonymized_id):
  """Check if the Patient ID inside the DICOM file matches the anonymized ID."""
  logging.info(f"Checking Patient ID in DICOM file {dicom_file}")
  try:
    logging.info(f"Reading DICOM file {dicom_file}")
    dicom_data = pydicom.dcmread(dicom_file)
    logging.info(f"Reading DICOM file {dicom_file} metadata")
    dicom_patient_id = dicom_data.get("PatientID", "Unknown")
    logging.info(f"Patient ID in DICOM file {dicom_file}: {dicom_patient_id}")
    if dicom_patient_id != anonymized_id:
      logging.warning(f"Patient ID mismatch: file {dicom_file} has Patient ID {dicom_patient_id}, expected {anonymized_id}")
  except Exception as e:
    logging.warning(f"Failed to read DICOM file {dicom_file}: {e}")

def find_real_patient_dicom(search_path):
  """Find all DICOM files in the search directory."""
  logging.info(f"Finding DICOM files in {search_path}")
  dicom_files = []
  for root, _, files in os.walk(search_path):
    logging.info(f"Checking directory {root}")
    for file in files:
      logging.info(f"Checking file {file}")
      filepath = os.path.join(root, file)
      logging.info(f"Checking if {filepath} is a DICOM file")
      if is_dicom_file(filepath):
        logging.info(f"Found DICOM file {filepath}")
        dicom_files.append(filepath)
        logging.info(f"Found {len(dicom_files)} DICOM files")
  return dicom_files

def process_dicom(process_path, mapping):
  """Process DICOM files in process_path, map to real_patient_id, and extract laterality."""
  logging.info(f"Processing DICOM files in {process_path}")
  for root, _, files in os.walk(process_path):
    logging.info(f"Checking directory {root}")
    for file in files:
      logging.info(f"Checking file {file}")
      if "_US_" in file:
        logging.info(f"Processing file {file}")
        anonymized_id = file.split('_')[0]
        logging.info(f"Anonymized ID: {anonymized_id}")
        real_patient_id = mapping.get(anonymized_id)
        logging.info(f"Real Patient ID: {real_patient_id}")
        dicom_file_path = os.path.join(root, file)
        logging.info(f"DICOM file path: {dicom_file_path}")
        
        # Check patient ID in the DICOM file
        logging.info(f"Checking Patient ID in DICOM file {dicom_file_path}")
        check_patient_id(dicom_file_path, anonymized_id)
        logging.info(f"Checking Patient ID complete")
        
        if real_patient_id:
          logging.info(f"Real Patient ID found: {real_patient_id}")
          dicom_files = find_real_patient_dicom(non_anonymized_dir)
          logging.info(f"Found {len(dicom_files)} DICOM files for real patient ID {real_patient_id}")
          for dicom_file in dicom_files:
            logging.info(f"Checking DICOM file {dicom_file}")
            # Compare instance numbers
            instance_number_1 = get_instance_number(dicom_file_path)
            instance_number_2 = get_instance_number(dicom_file)
            logging.info(f"Instance number 1: {instance_number_1}, Instance number 2: {instance_number_2}")
            if instance_number_1 is None or instance_number_2 is None or instance_number_1 != instance_number_2:
              logging.warning(f"Instance number mismatch: {instance_number_1} vs {instance_number_2}")
              continue
            
            logging.info(f"Instance numbers match: {instance_number_1} vs {instance_number_2}")
            laterality = get_laterality(dicom_file)
            if laterality == "Unknown":
              logging.warning(f"Laterality is unknown for DICOM file {dicom_file}")
              continue
            
            logging.info(f"Laterality: {laterality}")
            new_file_name = rename_file(file, laterality)
            logging.info(f"New file name: {new_file_name}")
            move_file(dicom_file_path, os.path.join(checked_dir, new_file_name))
            logging.info(f"Moved and renamed file {file} to {new_file_name}")

def rename_file(file_name, laterality):
  """Rename the file based on the laterality."""
  logging.info(f"Renaming file {file_name} with laterality {laterality}")
  parts = file_name.split('_')
  logging.info(f"Parts: {parts}")
  parts.insert(2, laterality)
  logging.info(f"Parts done: {parts}")
  return '_'.join(parts)

def move_file(src_path, dest_path):
  """Move the file from src_path to dest_path."""
  logging.info(f"Moving file {src_path} to {dest_path}")
  if os.path.exists(src_path):
    logging.info(f"File found: {src_path}")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    logging.info(f"Moving file {src_path} to {dest_path}")
    shutil.move(src_path, dest_path)
    logging.info(f"File moved to {dest_path}")
  else:
    logging.warning(f"File not found: {src_path}")

if __name__ == '__main__':
  logging.info("Starting processing...")
  mapping = load_mapping(mapping_csv)
  logging.info("Mapping loaded!")
  process_dicom(checking_dir, mapping)
  logging.info("Processing complete!")

# End of file