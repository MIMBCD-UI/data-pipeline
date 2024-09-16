#!/usr/bin/env python

"""
reidentified.py:

This script processes DICOM files located in the "identified" folder by extracting the SOP Instance UID 
from each DICOM file. It then searches the "raw" folder and its subfolders to find a matching SOP Instance UID. 
If a match is found, it extracts the Patient ID from the matching DICOM file in the "raw" folder, searches for 
the corresponding Anonymized Patient ID in the `mamo_patients_mapping_data.csv` file, updates the DICOM metadata 
and filename accordingly, and then moves the DICOM file to the "checked" folder. If no match is found, the DICOM file 
is moved from the "identified" folder to the "unsolvable" folder.

Intended Use Case:
- This script ensures that DICOM files in the "identified" folder are correctly identified based on SOP Instance UID 
  and have their Patient IDs anonymized according to the mapping file. Files that cannot be matched are moved to the "unsolvable" folder.

Expected Input:
- DICOM files in the "identified" folder and DICOM files in the "raw" folder.
- A CSV file containing mappings from Real Patient IDs to Anonymized Patient IDs.

"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.1.1"
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
identified_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "identified")
checked_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "checked")
unsolvable_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "unsolvable")
raw_dir = os.path.join(root_dir, "dicom-images-breast", "known", "raw")
mapping_csv = os.path.join(root_dir, "data-images-breast", "data", "mapping", mapping_fn)

# Debugging output for paths
logging.info(f"Mapping CSV: {mapping_csv}")
logging.info(f"Raw directory: {raw_dir}")
logging.info(f"Identified directory: {identified_dir}")
logging.info(f"Checked directory: {checked_dir}")
logging.info(f"Unsolvable directory: {unsolvable_dir}")

def load_mapping(csv_file):
  """Load mapping of real_patient_id to anonymized_patient_id from CSV."""
  logging.info(f"Loading mapping from {csv_file}")
  mapping = {}
  try:
    with open(csv_file, mode='r') as file:
      reader = csv.reader(file)
      next(reader)  # Skip header
      for row in reader:
        if len(row) < 2:
          logging.warning(f"Invalid row in CSV: {row}")
          continue
        real_id, anonymized_id = row
        mapping[real_id] = anonymized_id
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
    return dicom_data.get("PatientID", "Unknown")
  except Exception as e:
    logging.warning(f"Failed to read Patient ID from {dicom_file}: {e}")
    return None

def update_patient_id(dicom_file, new_patient_id):
  """Update the Patient ID in the DICOM metadata."""
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    dicom_data.PatientID = new_patient_id
    dicom_data.save_as(dicom_file)
    logging.info(f"Updated Patient ID to {new_patient_id} in file {dicom_file}")
  except Exception as e:
    logging.warning(f"Failed to update Patient ID in {dicom_file}: {e}")

def move_file(src_path, dest_path):
  """Move the file from src_path to dest_path."""
  if os.path.exists(src_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.move(src_path, dest_path)
    logging.info(f"File moved to {dest_path}")
  else:
    logging.warning(f"File not found: {src_path}")

def rename_file(file_name, new_patient_id):
  """Rename the file with the new patient ID."""
  parts = file_name.split('_')
  parts[0] = new_patient_id  # Replace the first part (anonymized_patient_id)
  return '_'.join(parts)

def process_identified_files(identified_path, raw_path, checked_path, unsolvable_path, mapping):
  """Process files in the identified directory and find matching SOP Instance UIDs in the raw directory."""
  logging.info(f"Processing DICOM files in identified directory: {identified_path}")
  for root, _, files in os.walk(identified_path):
    for file in files:
      identified_file_path = os.path.join(root, file)
      if not is_dicom_file(identified_file_path):
        continue

      sop_instance_uid_identified = get_sop_instance_uid(identified_file_path)
      if sop_instance_uid_identified is None:
        logging.warning(f"No SOP Instance UID found for {identified_file_path}. Moving to unsolvable...")
        move_file(identified_file_path, os.path.join(unsolvable_path, file))
        continue

      logging.info(f"Searching for matching SOP Instance UID: {sop_instance_uid_identified}")
      found_match = False
      for raw_root, _, raw_files in os.walk(raw_path):
        for raw_file in raw_files:
          raw_file_path = os.path.join(raw_root, raw_file)
          if not is_dicom_file(raw_file_path):
            continue

          sop_instance_uid_raw = get_sop_instance_uid(raw_file_path)
          if sop_instance_uid_identified == sop_instance_uid_raw:
            logging.info(f"Match found! Identified file SOP Instance UID: {sop_instance_uid_identified} | Raw file SOP Instance UID: {sop_instance_uid_raw}")
            logging.info(f"Identified file: {identified_file_path} | Raw file: {raw_file_path}")

            # Extract the real_patient_id from the matching raw file
            real_patient_id = get_patient_id(raw_file_path)
            if real_patient_id is None:
              logging.warning(f"Real Patient ID not found in {raw_file_path}. Moving to unsolvable...")
              move_file(identified_file_path, os.path.join(unsolvable_path, file))
              continue

            # Find the anonymized_patient_id using the mapping
            anonymized_patient_id = mapping.get(real_patient_id)
            if anonymized_patient_id is None:
              logging.warning(f"No mapping found for Real Patient ID {real_patient_id}. Moving to unsolvable...")
              move_file(identified_file_path, os.path.join(unsolvable_path, file))
              continue

            # Update the Patient ID in the DICOM metadata
            update_patient_id(identified_file_path, anonymized_patient_id)

            # Rename the file with the anonymized_patient_id
            new_file_name = rename_file(file, anonymized_patient_id)
            checked_file_path = os.path.join(checked_path, new_file_name)

            # Move the renamed file to the checked directory
            move_file(identified_file_path, checked_file_path)

            # Log the full path of the matched raw file
            logging.info(f"Raw file path where SOP Instance UID was identified: {raw_file_path}")
            found_match = True
            break

        if found_match:
          break

      if not found_match:
        logging.info(f"No matching SOP Instance UID found for {identified_file_path}. Moving to unsolvable...")
        move_file(identified_file_path, os.path.join(unsolvable_path, file))

if __name__ == '__main__':
  logging.info("Starting reidentified processing...")
  mapping = load_mapping(mapping_csv)
  logging.info("Mapping loaded!")
  process_identified_files(identified_dir, raw_dir, checked_dir, unsolvable_dir, mapping)
  logging.info("Reidentified processing complete!")

# End of file