#!/usr/bin/env python

"""
laterality.py:

WARNING: This script is designed to process DICOM files specifically for the US (ultrasound) modality. 
It checks for the "_US_" pattern in the filenames and will only process files that match this pattern. 
If you intend to process other modalities, you will need to modify the script accordingly.

This script processes DICOM files by mapping anonymized patient IDs to their corresponding real patient IDs, 
extracting specific metadata (such as laterality and instance number), and then renaming and moving the files accordingly. 
It ensures that medical imaging data is correctly linked and organized, particularly in the context of anonymization, 
making it essential for research projects like the MIMBCD-UI initiative.

Key Functions:
- Load mappings between anonymized and real patient IDs from a CSV file.
- Validate and extract metadata (e.g., laterality, instance number) from DICOM files.
- Rename files based on extracted metadata and move them to the appropriate directory.

Intended Use Case:
- This script is crucial in environments where maintaining connections between anonymized and non-anonymized 
  medical imaging data is necessary, ensuring proper file management and data integrity within research projects like the MIMBCD-UI initiative.

Expected Input:
- DICOM files in a specific directory structure with filenames that include the anonymized patient ID.
- A CSV file containing mappings from anonymized patient IDs to real patient IDs.

"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.2.4"
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
  try:
    with open(csv_file, mode='r') as file:
      reader = csv.reader(file)
      next(reader)  # Skip header
      logging.info("Reading mapping data...")
      for row in reader:
        if len(row) < 2:
          logging.warning(f"Invalid row in CSV: {row}")
          continue
        real_id, anonymized_id = row
        mapping[anonymized_id] = real_id
  except Exception as e:
    logging.error(f"Failed to load mapping from {csv_file}: {e}")
  return mapping

def is_dicom_file(filepath):
  """Check if a file is a DICOM file by attempting to read it."""
  try:
    pydicom.dcmread(filepath)
    return True
  except Exception as e:
    logging.warning(f"File {filepath} is not a DICOM file: {e}")
    return False

def get_laterality(dicom_file):
  """Extract laterality from DICOM metadata."""
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    return dicom_data.get("ImageLaterality", "Unknown")
  except Exception as e:
    logging.warning(f"Failed to read laterality from {dicom_file}: {e}")
    return "Unknown"

def get_instance_number(dicom_file):
  """Extract instance number from DICOM metadata."""
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    return dicom_data.get("InstanceNumber", None)
  except Exception as e:
    logging.warning(f"Failed to read instance number from {dicom_file}: {e}")
    return None

def check_patient_id(dicom_file, anonymized_id):
  """Check if the Patient ID inside the DICOM file matches the anonymized ID."""
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    dicom_patient_id = dicom_data.get("PatientID", "Unknown")
    if dicom_patient_id != anonymized_id:
      logging.warning(f"Patient ID mismatch in {dicom_file}: found {dicom_patient_id}, expected {anonymized_id}")
  except Exception as e:
    logging.warning(f"Failed to read Patient ID from {dicom_file}: {e}")

def find_real_patient_dicom(search_path):
  """Find all DICOM files in the search directory."""
  dicom_files = []
  for root, _, files in os.walk(search_path):
    for file in files:
      filepath = os.path.join(root, file)
      if is_dicom_file(filepath):
        dicom_files.append(filepath)
  return dicom_files

def process_dicom(process_path, mapping):
  """Process DICOM files in process_path, map to real_patient_id, and extract laterality."""
  logging.info(f"Processing DICOM files in directory: {process_path}")
  for root, _, files in os.walk(process_path):
    for file in files:
      if "_US_" in file:
        logging.info(f"Found file matching pattern: {file}")
        anonymized_id = file.split('_')[0]
        real_patient_id = mapping.get(anonymized_id)
        dicom_file_path = os.path.join(root, file)
        
        # Check patient ID in the DICOM file
        check_patient_id(dicom_file_path, anonymized_id)
        
        if real_patient_id:
          dicom_files = find_real_patient_dicom(non_anonymized_dir)
          for dicom_file in dicom_files:
            # Compare instance numbers
            instance_number_1 = get_instance_number(dicom_file_path)
            instance_number_2 = get_instance_number(dicom_file)
            if instance_number_1 is None or instance_number_2 is None or instance_number_1 != instance_number_2:
              logging.warning(f"Instance number mismatch: {instance_number_1} vs {instance_number_2}")
              continue
            
            laterality = get_laterality(dicom_file)
            if laterality == "Unknown":
              logging.warning(f"Laterality is unknown for DICOM file {dicom_file}")
              continue
            
            new_file_name = rename_file(file, laterality)
            move_file(dicom_file_path, os.path.join(checked_dir, new_file_name))
            logging.info(f"Moved and renamed file {file} to {new_file_name}")

def rename_file(file_name, laterality):
  """Rename the file based on the laterality."""
  parts = file_name.split('_')
  parts.insert(2, laterality)
  return '_'.join(parts)

def move_file(src_path, dest_path):
  """Move the file from src_path to dest_path."""
  if os.path.exists(src_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
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