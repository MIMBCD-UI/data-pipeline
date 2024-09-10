#!/usr/bin/env python

"""
reanonimyzer.py:

This script processes DICOM files by comparing anonymized and non-anonymized versions to ensure that the anonymized patient IDs are correct. It corrects any discrepancies in filenames and DICOM metadata based on predefined mappings, and then moves the corrected files to a designated 'checked' directory. This ensures the integrity and consistency of patient data, which is crucial for maintaining accurate and reliable datasets in research projects like the MIMBCD-UI initiative.

Key Functions:
- Load and use mappings between real and anonymized patient IDs to validate and correct DICOM files.
- Compare instance numbers between anonymized and non-anonymized files to identify corresponding pairs.
- Update filenames and DICOM metadata to reflect the correct anonymized patient ID.
- Move processed and validated files to a designated directory for further use.

Intended Use Case:
- This script is vital in environments where maintaining the integrity of anonymized medical imaging data is crucial. It supports the correct linkage between anonymized and non-anonymized datasets, ensuring accurate data management in research projects like the MIMBCD-UI initiative.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "1.0.1"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import logging
import pydicom
import shutil
import warnings
import pandas as pd
from urllib3.exceptions import NotOpenSSLWarning

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress warnings
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Mapping file name
mapping_fn = "mamo_patients_mapping_data_curated_21052024.csv"

# Define root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define paths
non_anonymized_dir = os.path.join(root_dir, "dicom-images-breast", "known", "raw")
checking_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "checking")
checked_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "checked")
mapping_csv_path = os.path.join(root_dir, "dataset-multimodal-breast", "data", "inconsistencies", mapping_fn)

# Debugging output for paths
# non_anonymized_dir = os.path.join(root_dir, "dicom-images-breast", "tests", "testing_checking_test001")
# checking_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "tests_to_delete", "checking_test001")
# checked_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "tests_to_delete", "checked_test001")
# mapping_csv_path = os.path.join(root_dir, "dataset-multimodal-breast", "data", "inconsistencies", mapping_fn)

# Load the mapping CSV into a DataFrame, ensuring the header row is skipped
logging.info(f"Loading mapping CSV from {mapping_csv_path}")
mapping_df = pd.read_csv(mapping_csv_path, dtype=str)
logging.info(f"First few rows of the mapping CSV:\n{mapping_df.head()}")

# Log the shape of the DataFrame to confirm the correct number of rows
logging.info(f"Shape of the mapping DataFrame: {mapping_df.shape}")

# Load the mapping into a dictionary for quick lookup
mapping_dict = pd.Series(mapping_df.anonymized_patient_id.values, index=mapping_df.real_patient_id).to_dict()
logging.info(f"Mapping dictionary created with {len(mapping_dict)} entries")

def is_dicom_file(filepath):
  """Check if a file is a DICOM file by attempting to read it."""
  logging.info(f"Checking if {filepath} is a DICOM file...")
  try:
    pydicom.dcmread(filepath)
    logging.info(f"{filepath} is a DICOM file.")
    return True
  except Exception:
    logging.info(f"{filepath} is not a DICOM file.")
    return False

def get_instance_number(dicom_file):
  """Extract instance number from DICOM metadata."""
  logging.info(f"Extracting instance number from DICOM metadata for file: {dicom_file}")
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    instance_number = dicom_data.get("InstanceNumber", None)
    logging.info(f"Instance Number for {dicom_file}: {instance_number}")
    return instance_number
  except Exception as e:
    logging.warning(f"Failed to read DICOM file {dicom_file}: {e}")
    return None

def get_patient_id(dicom_file):
  """Extract patient ID from DICOM metadata."""
  logging.info(f"Extracting patient ID from DICOM metadata for file: {dicom_file}")
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    patient_id = dicom_data.get("PatientID", "Unknown")
    logging.info(f"Patient ID for {dicom_file}: {patient_id}")
    return patient_id
  except Exception as e:
    logging.warning(f"Failed to read DICOM file {dicom_file}: {e}")
    return "Unknown"

def update_dicom_metadata(dicom_file, new_patient_id):
  """Update the PatientID in the DICOM metadata."""
  logging.info(f"Updating DICOM metadata for file: {dicom_file}")
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    dicom_data.PatientID = new_patient_id
    dicom_data.save_as(dicom_file)
    logging.info(f"Updated DICOM metadata for {dicom_file} with new PatientID: {new_patient_id}")
  except Exception as e:
    logging.warning(f"Failed to update DICOM metadata for {dicom_file}: {e}")

def find_dicom_files(search_path):
  """Find all DICOM files in the search directory."""
  logging.info(f"Finding DICOM files in {search_path}")
  dicom_files = []
  for root, _, files in os.walk(search_path):
    logging.info(f"Checking directory {root}")
    for file in files:
      filepath = os.path.join(root, file)
      if is_dicom_file(filepath):
        dicom_files.append(filepath)
        logging.info(f"Found DICOM file: {filepath}")
  return dicom_files

def process_dicom_files(checking_path, non_anonymized_path, checked_path, mapping_dict):
  """Process DICOM files, correct anonymized_patient_id and metadata, and move to checked directory."""
  logging.info(f"Scanning for DICOM files in {non_anonymized_path}")
  non_anonymized_files = find_dicom_files(non_anonymized_path)
  logging.info(f"Found {len(non_anonymized_files)} DICOM files in {non_anonymized_path}")

  logging.info(f"Scanning for DICOM files in {checking_path}")
  for root, _, files in os.walk(checking_path):
    logging.info(f"Checking directory {root}")
    for file in files:
      if "_MG_" in file:
        logging.info(f"Processing file {file}")
        anonymized_id = file.split('_')[0]
        dicom_file_path = os.path.join(root, file)
        instance_number = get_instance_number(dicom_file_path)
        logging.info(f"Anonymized ID from filename: {anonymized_id}")
        logging.info(f"Instance Number from anonymized file: {instance_number}")

        for non_anonymized_file in non_anonymized_files:
          logging.info(f"Checking non-anonymized file {non_anonymized_file}")
          non_anonymized_instance_number = get_instance_number(non_anonymized_file)
          real_patient_id = get_patient_id(non_anonymized_file)
          logging.info(f"Non-anonymized Instance Number: {non_anonymized_instance_number}, Real Patient ID: {real_patient_id}")

          if instance_number == non_anonymized_instance_number:
            correct_anonymized_id = mapping_dict.get(real_patient_id, None)
            
            if correct_anonymized_id:
              logging.info(f"Correct anonymized ID for real patient ID {real_patient_id} is {correct_anonymized_id}")
            else:
              logging.warning(f"No mapping found for real patient ID {real_patient_id}")
              correct_anonymized_id = anonymized_id

            if correct_anonymized_id != anonymized_id:
              logging.info(f"Correcting anonymized_patient_id in {dicom_file_path} to {correct_anonymized_id}")
              new_file_name = f"{correct_anonymized_id}_{'_'.join(file.split('_')[1:])}"
              new_file_path = os.path.join(checked_path, new_file_name)
              logging.info(f"New file name: {new_file_name}")
              logging.info(f"New file path: {new_file_path}")

              os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
              shutil.move(dicom_file_path, new_file_path)
              logging.info(f"Renamed and moved file {dicom_file_path} to {new_file_path}")
              update_dicom_metadata(new_file_path, correct_anonymized_id)
              logging.info(f"Updated metadata for {new_file_path} with PatientID: {correct_anonymized_id}")
            break

if __name__ == '__main__':
  logging.info("Starting DICOM file processing...")
  process_dicom_files(checking_dir, non_anonymized_dir, checked_dir, mapping_dict)
  logging.info("DICOM file processing complete!")

# End of file