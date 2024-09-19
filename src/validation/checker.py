#!/usr/bin/env python

"""
checker.py:

This script compares anonymized and non-anonymized DICOM files to identify matching files based on the `SOPInstanceUID` metadata.
It traverses specified directories, reads DICOM files, and checks for matches. If a match is found, the file is moved to the "checked" folder.
If no match is found, the file is moved to the "unsolvable" folder.

Key Functions:
- Identify and validate DICOM files in the anonymized and non-anonymized directories.
- Compare DICOM files based on `SOPInstanceUID` to find matching pairs.
- Move the file to the "checked" folder if a match is found, otherwise move it to the "unsolvable" folder.
- Support for MG (Mammography), US (Ultrasound), and MRI (Magnetic Resonance Imaging) modalities.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "1.0.0"
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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress warnings for clean output
warnings.filterwarnings("ignore")
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


def is_supported_modality(dicom_file):
  """
  Check if the DICOM file is of a supported modality (US, MG, MRI).

  Args:
    dicom_file (pydicom.dataset.FileDataset): The DICOM file to check.

  Returns:
    bool: True if the file matches one of the supported modalities, False otherwise.
  """
  dicom_modality = dicom_file.get("Modality", "").upper()
  logging.info(f"Modality: {dicom_modality}")
  return dicom_modality in SUPPORTED_MODALITIES


def is_dicom_file(filepath):
  """
  Check if a file is a valid DICOM file by attempting to read it.

  Args:
    filepath (str): The file path to check.

  Returns:
    bool: True if the file is a valid DICOM file, False otherwise.
  """
  try:
    pydicom.dcmread(filepath, stop_before_pixels=True)
    return True
  except Exception as e:
    logging.warning(f"Not a DICOM file: {filepath} - {e}")
    return False


def compare_dicom_files(anonymized_path, non_anonymized_path, output_csv):
  """
  Compare anonymized and non-anonymized DICOM files based on `SOPInstanceUID` and move the files accordingly.

  Args:
    anonymized_path (str): Directory containing anonymized DICOM files.
    non_anonymized_path (str): Directory containing non-anonymized DICOM files.
    output_csv (str): Path to the output CSV file.
  """
  matching_paths = []
  anonymized_files = get_all_files(anonymized_path)
  non_anonymized_files = get_all_files(non_anonymized_path)

  for anonymized_filepath in anonymized_files:
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

    match_found = False
    for non_anonymized_filepath in non_anonymized_files:
      if not is_dicom_file(non_anonymized_filepath):
        continue
      non_anonymized_dicom = pydicom.dcmread(non_anonymized_filepath)

      if not hasattr(non_anonymized_dicom, 'SOPInstanceUID'):
        continue

      if anonymized_dicom.SOPInstanceUID == non_anonymized_dicom.SOPInstanceUID:
        matching_paths.append((anonymized_filepath, non_anonymized_filepath))
        move_to_checked(anonymized_filepath)
        match_found = True
        break

    if not match_found:
      move_to_unsolvable(anonymized_filepath)

  # Save matching paths to a CSV file
  save_to_csv(output_csv, matching_paths)


def save_to_csv(csv_path, data):
  """
  Save the matching file paths to a CSV file.

  Args:
    csv_path (str): Path to the CSV file.
    data (list of tuples): List of anonymized and non-anonymized file path pairs.
  """
  with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Anonymized Path', 'Non-Anonymized Path'])
    writer.writerows(data)
  logging.info(f"Saved matching file paths to {csv_path}")


def get_all_files(directory):
  """
  Get all files recursively from a directory.

  Args:
    directory (str): The directory path.

  Returns:
    list: A list of all file paths in the directory and subdirectories.
  """
  file_list = []
  for root, dirs, files in os.walk(directory):
    for file in files:
      file_list.append(os.path.join(root, file))
  return file_list


def move_to_checked(filepath):
  """
  Move the file to the 'checked' directory.

  Args:
    filepath (str): Path of the file to be moved.
  """
  filename = os.path.basename(filepath)
  dest_path = os.path.join(checked_dir, filename)
  move_file(filepath, dest_path)
  logging.info(f"File {filename} moved to checked directory.")


def move_to_unsolvable(filepath):
  """
  Move the file to the 'unsolvable' directory.

  Args:
    filepath (str): Path of the file to be moved.
  """
  filename = os.path.basename(filepath)
  dest_path = os.path.join(unsolvable_dir, filename)
  move_file(filepath, dest_path)
  logging.info(f"File {filename} moved to unsolvable directory.")


def move_file(src, dest):
  """
  Move a file from src to dest.

  Args:
    src (str): Source file path.
    dest (str): Destination file path.
  """
  if os.path.exists(src):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.move(src, dest)
    logging.info(f"File moved to {dest}")
  else:
    logging.warning(f"File not found: {src}")


if __name__ == '__main__':
  compare_dicom_files(anonymized_dir, non_anonymized_dir, output_csv_file)
  logging.info("Comparison complete!")

# End of file