#!/usr/bin/env python

"""
laterality.py:

This script processes DICOM files by checking for the "Modality" and "Laterality" DICOM tags. It ensures that medical imaging data 
is correctly linked and organized, particularly in the context of anonymization, for both US (ultrasound) and MG (mammography) modalities.

Files are moved based on laterality:
- To the "incongruities" folder if laterality is found in the DICOM tags and correctly matches the filename.
- To the "unsolvable" folder if laterality is missing or cannot be matched.

This script is especially useful for managing anonymized imaging data for research projects.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.4.1"
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import logging
import pydicom
import shutil
import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress specific warnings
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Define paths for DICOM processing
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
verifying_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "verifying")
incongruities_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "incongruities")
unsolvable_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "unsolvable")

# Debugging output for paths
logging.info(f"Verifying directory: {verifying_dir}")
logging.info(f"Incongruities directory: {incongruities_dir}")
logging.info(f"Unsolvable directory: {unsolvable_dir}")

def is_dicom_file(filepath):
  """
  Check if the given file is a valid DICOM file.
  
  Args:
    filepath (str): Path to the file to check.

  Returns:
    bool: True if the file is a valid DICOM file, False otherwise.
  """
  try:
    pydicom.dcmread(filepath, stop_before_pixels=True)
    logging.debug(f"File {filepath} is a valid DICOM file.")
    return True
  except pydicom.errors.InvalidDicomError:
    logging.warning(f"File {filepath} is not a valid DICOM file.")
    return False
  except Exception as e:
    logging.warning(f"Unexpected error reading file {filepath}: {e}")
    return False

def get_dicom_tag(dicom_file, tag):
  """
  Extract a specified DICOM tag from the DICOM metadata.
  
  Args:
    dicom_file (str): Path to the DICOM file.
    tag (str): Tag to extract (e.g., 'Modality', 'ImageLaterality').

  Returns:
    str: Value of the specified tag or an empty string if not found.
  """
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    value = dicom_data.get(tag, "")
    logging.debug(f"File {dicom_file} has {tag}: {value}.")
    return value
  except Exception as e:
    logging.warning(f"Failed to read {tag} from {dicom_file}: {e}")
    return ""

def move_file(filepath, folder, laterality=None):
  """
  Move a file to a specified folder, renaming it if necessary.
  
  Args:
    filepath (str): The path of the file to move.
    folder (str): The destination folder.
    laterality (str): Optional. If provided, it will be included in the filename.
  """
  filename = os.path.basename(filepath)
  
  # Ensure '_NA_' is formatted properly, not '__NA__'
  if laterality:
    filename = rename_file(filename, laterality)
  
  dest_path = os.path.join(folder, filename)
  
  if os.path.exists(filepath):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.move(filepath, dest_path)
    logging.info(f"File moved to {dest_path}")
  else:
    logging.warning(f"File not found: {filepath}")

def rename_file(filename, laterality):
  """
  Rename the file by inserting the laterality if not already present.
  
  Args:
    filename (str): The original filename.
    laterality (str): The laterality (e.g., 'L', 'R', '_NA_') to insert.

  Returns:
    str: The new filename with laterality inserted.
  """
  parts = filename.split('_')
  
  # Ensure clean formatting and avoid double underscores
  if laterality not in parts:
    new_parts = [part for part in parts if part]  # Remove any empty parts
    new_parts.insert(2, laterality.strip('_'))  # Insert the laterality properly
    return '_'.join(new_parts)
  
  return filename

def process_dicom_files(directory):
  """
  Process all DICOM files in a directory, checking modality and laterality.
  
  Args:
    directory (str): The path to the directory containing DICOM files.
  """
  logging.info(f"Processing DICOM files in directory: {directory}")
  processed_count = 0
  
  for root, _, files in os.walk(directory):
    for file in files:
      dicom_file_path = os.path.join(root, file)
      logging.info(f"Processing file: {dicom_file_path}")

      if not is_dicom_file(dicom_file_path):
        logging.warning(f"Skipping non-DICOM file: {file}")
        continue

      modality = get_dicom_tag(dicom_file_path, "Modality")
      if modality not in ["US", "MG"]:
        logging.info(f"Skipping file {file} with unsupported modality {modality}.")
        continue

      laterality = get_dicom_tag(dicom_file_path, "ImageLaterality")
      if laterality not in ["L", "R"]:
        move_file(dicom_file_path, unsolvable_dir, laterality="_NA_")
      else:
        move_file(dicom_file_path, incongruities_dir, laterality)

      processed_count += 1

  logging.info(f"Processed {processed_count} DICOM files.")

if __name__ == '__main__':
  logging.info("Starting processing...")
  process_dicom_files(verifying_dir)
  logging.info("Processing complete!")

# End of file