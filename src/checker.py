#!/usr/bin/env python

"""
checker.py: Compare two DICOM files and save paths to CSV.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.7.0"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import csv
import logging
import warnings
import pydicom
from urllib3.exceptions import NotOpenSSLWarning

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress all warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Define paths
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
anonymized_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "dicom")
non_anonymized_dir = os.path.join(root_dir, "dicom-images-breast", "known", "raw")
output_csv_file = os.path.join(root_dir, "dicom-images-breast", "data", "checking", "mapping.csv")

# Modality to be used
modality = 'US'.lower()

def is_modality(dicom_file):
  """Check if DICOM file is of the specified modality."""
  dicom_modality = dicom_file.get("Modality", "").lower()
  logging.info(f"Modality: {dicom_modality}")
  return dicom_modality == modality

def is_dicom_file(filepath):
  """Check if a file is a DICOM file by attempting to read it."""
  try:
    pydicom.dcmread(filepath)
    return True
  except Exception as e:
    logging.warning(f"Not a DICOM file: {filepath} - {e}")
    return False

def compare_dicom_files(anonymized_path, non_anonymized_path, output_csv):
  """Compare DICOM files and save matching paths to CSV."""
  matching_paths = []
  anonymized_files = get_all_files(anonymized_path)
  non_anonymized_files = get_all_files(non_anonymized_path)

  for anonymized_filepath in anonymized_files:
    logging.info(f"Comparing: {anonymized_filepath}")
    if not is_dicom_file(anonymized_filepath):
      logging.warning(f"Not a DICOM file: {anonymized_filepath}")
      continue
    anonymized_dicom = pydicom.dcmread(anonymized_filepath)

    if not hasattr(anonymized_dicom, 'InstanceNumber'):
      logging.warning(f"InstanceNumber not found in DICOM file: {anonymized_filepath}")
      continue

    for non_anonymized_filepath in non_anonymized_files:
      logging.info(f"Comparing: {non_anonymized_filepath}")
      if not is_dicom_file(non_anonymized_filepath):
        logging.warning(f"Not a DICOM file: {non_anonymized_filepath}")
        continue

      non_anonymized_dicom = pydicom.dcmread(non_anonymized_filepath)
      if not hasattr(non_anonymized_dicom, 'InstanceNumber'):
        continue

      if (anonymized_dicom.InstanceNumber == non_anonymized_dicom.InstanceNumber):
        matching_paths.append((anonymized_filepath, non_anonymized_filepath))
        break

  with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Anonymized Path', 'Non-Anonymized Path'])
    writer.writerows(matching_paths)

def get_all_files(directory):
  """Recursively get all files from directory and subdirectories."""
  file_list = []
  for root, dirs, files in os.walk(directory):
    for file in files:
      file_list.append(os.path.join(root, file))
  return file_list

if __name__ == '__main__':
  compare_dicom_files(anonymized_dir, non_anonymized_dir, output_csv_file)
  logging.info("Comparison complete!")

# End of file