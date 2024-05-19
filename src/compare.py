#!/usr/bin/env python

"""
compare.py: Compare anonymized and non-anonymized DICOM files, rename them based on metadata, and move to a checked directory.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "1.0.0"
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
    next(reader)  # Skip header
    for row in reader:
      real_id, anonymized_id = row
      mapping[anonymized_id] = real_id
  return mapping

def is_dicom_file(filepath):
  """Check if a file is a DICOM file by attempting to read it."""
  try:
    pydicom.dcmread(filepath)
    return True
  except Exception:
    return False

def get_metadata(dicom_file, tags):
  """Extract specified metadata tags from DICOM file."""
  try:
    dicom_data = pydicom.dcmread(dicom_file)
    return {tag: dicom_data.get(tag, "Unknown") for tag in tags}
  except Exception as e:
    logging.warning(f"Failed to read DICOM file {dicom_file}: {e}")
    return {tag: "Unknown" for tag in tags}

def find_dicom_files(search_path):
  """Find all DICOM files in the search directory."""
  dicom_files = []
  for root, _, files in os.walk(search_path):
    for file in files:
      filepath = os.path.join(root, file)
      if is_dicom_file(filepath):
        dicom_files.append(filepath)
  return dicom_files

def process_dicom(process_path, mapping):
  """Process DICOM files in process_path, map to real_patient_id, and extract metadata."""
  dicom_tags = ["PatientID", "InstanceNumber", "ViewPosition", "ImageLaterality"]
  
  for root, _, files in os.walk(process_path):
    for file in files:
      if "_MG_" in file:
        anonymized_id = file.split('_')[0]
        real_patient_id = mapping.get(anonymized_id)
        dicom_file_path = os.path.join(root, file)
        
        if real_patient_id:
          non_anonymized_dicom_files = find_dicom_files(non_anonymized_dir)
          for non_anonymized_file in non_anonymized_dicom_files:
            instance_number_1 = get_metadata(dicom_file_path, ["InstanceNumber"])["InstanceNumber"]
            instance_number_2 = get_metadata(non_anonymized_file, ["InstanceNumber"])["InstanceNumber"]
            
            if instance_number_1 == instance_number_2:
              view_position = get_metadata(non_anonymized_file, ["ViewPosition"])["ViewPosition"]
              image_laterality = get_metadata(non_anonymized_file, ["ImageLaterality"])["ImageLaterality"]
              
              if view_position == "Unknown" or image_laterality == "Unknown":
                continue
              
              new_file_name = rename_file(file, view_position, image_laterality)
              move_file(dicom_file_path, os.path.join(checked_dir, new_file_name))

def rename_file(file_name, view_position, image_laterality):
  """Rename the file based on the view position and image laterality."""
  parts = file_name.split('_')
  parts[2] = view_position
  parts[3] = image_laterality
  return '_'.join(parts)

def move_file(src_path, dest_path):
  """Move the file from src_path to dest_path."""
  if os.path.exists(src_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.move(src_path, dest_path)

if __name__ == '__main__':
  logging.info("Starting processing...")
  mapping = load_mapping(mapping_csv)
  logging.info("Mapping loaded!")
  process_dicom(checking_dir, mapping)
  logging.info("Processing complete!")

# End of file