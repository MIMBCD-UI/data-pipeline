#!/usr/bin/env python

"""
explorer.py:
This script reads DICOM files from the "unexplored" folder, extracts the Patient ID from the DICOM metainformation, 
and checks if the Patient ID exists in the second column of the 'anonymized_patients_birads_curation.csv' file.
If a match is found, the DICOM file is moved to the "checking" folder. Otherwise, it stays in the "unexplored" folder.
The script processes up to 50,000 DICOM files.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.1.3"  # Version increment to reflect further refinements
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import csv
import logging
import pydicom
import shutil

# Configure detailed logging for debugging and tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Limit the number of files to process (configurable)
FILE_LIMIT = 10

# File name for the CSV mapping of patients
csv_fn = "anonymized_patients_birads_curation.csv"

# Directory paths (handled holistically to ensure cross-platform compatibility)
# The logic ensures the root_dir points to the correct absolute root folder
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Define subdirectories relative to the root directory
unexplored_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "unexplored")
checking_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "checking")
csv_file = os.path.join(root_dir, "dataset-multimodal-breast", "data", "birads", csv_fn)

# Ensure the "checking" directory exists; create it if it doesn't
os.makedirs(checking_dir, exist_ok=True)

def load_patient_ids(csv_filepath):
  """
  Load Patient IDs from the second column of the CSV file into a set for fast lookups.
  
  Args:
    csv_filepath (str): Path to the CSV file.
  
  Returns:
    set: A set containing Patient IDs.
  """
  patient_ids = set()
  try:
    # Open the CSV file and read patient IDs from the second column
    with open(csv_filepath, mode='r') as file:
      reader = csv.reader(file)
      next(reader)  # Skip the header row
      for row in reader:
        if len(row) >= 2:  # Ensure row has enough columns
          # Add Patient ID from the second column and strip any extra spaces
          patient_ids.add(row[1].strip())
      logging.info(f"Loaded {len(patient_ids)} Patient IDs from CSV.")
  except Exception as e:
    logging.error(f"Error reading CSV file {csv_filepath}: {e}")
  return patient_ids

def extract_patient_id(dicom_file):
  """
  Extract the Patient ID from the DICOM file's metadata.
  
  Args:
    dicom_file (str): Path to the DICOM file.
  
  Returns:
    str: The Patient ID, or None if it cannot be found.
  """
  try:
    # Read the DICOM file's metadata and attempt to extract the Patient ID
    ds = pydicom.dcmread(dicom_file)
    return ds.PatientID if hasattr(ds, 'PatientID') else None  # Extract PatientID if it exists
  except Exception as e:
    # Log if reading the DICOM file fails
    logging.warning(f"Failed to read DICOM file {dicom_file}: {e}")
    return None

def move_file_to_checking(src_path, dest_dir):
  """
  Move a DICOM file to the "checking" folder.
  
  Args:
    src_path (str): Source path of the DICOM file.
    dest_dir (str): Destination directory where the file will be moved.
  """
  try:
    # Move file from the unexplored directory to the checking directory
    shutil.move(src_path, dest_dir)
    logging.info(f"Moved file {src_path} to {dest_dir}")
  except Exception as e:
    # Log an error if the file move operation fails
    logging.error(f"Failed to move file {src_path} to {dest_dir}: {e}")

def process_dicom_files(unexplored_dir, checking_dir, patient_ids, file_limit):
  """
  Process DICOM files from the "unexplored" folder, extracting Patient IDs and checking them against the CSV file.
  If a match is found, move the file to the "checking" folder. Otherwise, leave it in "unexplored".
  
  Args:
    unexplored_dir (str): Path to the "unexplored" folder.
    checking_dir (str): Path to the "checking" folder.
    patient_ids (set): Set of Patient IDs loaded from the CSV.
    file_limit (int): Maximum number of DICOM files to process.
  """
  processed_files = 0  # Track how many files have been processed
  moved_files = 0  # Track how many files were moved

  # Walk through each file in the unexplored directory
  for root, _, files in os.walk(unexplored_dir):
    for file in files:
      if processed_files >= file_limit:  # Stop if the file limit is reached
        logging.info(f"Reached the limit of {file_limit} files.")
        logging.info(f"Total files moved to checking: {moved_files}")
        return

      # Full path of the DICOM file to process
      dicom_file_path = os.path.join(root, file)
      patient_id = extract_patient_id(dicom_file_path)  # Extract the Patient ID

      if patient_id:
        if patient_id in patient_ids:
          # If Patient ID exists in the CSV, move the file to the checking directory
          move_file_to_checking(dicom_file_path, checking_dir)
          moved_files += 1  # Track number of files moved
        else:
          logging.info(f"Patient ID {patient_id} not found in CSV. File remains in unexplored.")
      else:
        logging.warning(f"No Patient ID found in {dicom_file_path}")  # Log if no Patient ID is found

      processed_files += 1  # Increment the count of processed files

if __name__ == "__main__":
  # Load Patient IDs from the specified CSV file
  patient_ids = load_patient_ids(csv_file)

  # Process DICOM files in the "unexplored" folder based on the loaded Patient IDs
  process_dicom_files(unexplored_dir, checking_dir, patient_ids, FILE_LIMIT)

  # Log when DICOM file exploration is complete
  logging.info("DICOM file exploration complete.") 

# End of file