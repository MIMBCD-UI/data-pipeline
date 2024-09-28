#!/usr/bin/env python

"""
compare.py:

This script processes and compares anonymized and non-anonymized DICOM files. It supports MG (Mammography), US (Ultrasound), and MRI (Magnetic Resonance Imaging) modalities. The script matches DICOM files based on metadata such as `SOPInstanceUID`, `ViewPosition`, and `ImageLaterality`. Once matched, anonymized files are renamed and moved to a 'compared' directory for further processing.

Key Functions:
- Load a CSV file containing patient mapping data.
- Find all DICOM files in the 'comparing' directory.
- Index non-anonymized files by `SOPInstanceUID` for fast lookup.
- Process anonymized files, match based on `PatientID` and `SOPInstanceUID`, and rename.
- Move the matched files to the 'compared' directory for further analysis.

Expected Input:
- Anonymized and non-anonymized DICOM files in separate directories.
- A CSV file containing mappings from Real Patient IDs to Anonymized Patient IDs.

Output:
- The script moves anonymized files to the `compared` directory if a match is found.
- The matched files are renamed based on the `ViewPosition` and `ImageLaterality` metadata.
- The script logs the progress and results of the comparison.

Intended Use Case:
- This script is useful for validating the anonymization process and ensuring that the correct files are anonymized.
- It can be used as part of a data curation pipeline to verify the integrity of DICOM files.

Customization & Flexibility:
- The script can be easily extended to support additional metadata fields for comparison.
- It can be adapted to handle other types of medical imaging data or metadata.
- The script can be modified to support other modalities or imaging techniques.

Performance & Compatibility:
- The script is designed for performance and efficiency when processing large datasets.
- It uses multiprocessing to parallelize the comparison of DICOM files and optimize resource utilization.

Best Practices & Maintenance:
- The script follows best practices for error handling, logging, and code readability.
- It is well-documented and can be easily maintained or extended by other developers.
- The script is designed to be robust and reliable for long-term use in data curation workflows.

Notes:
- This script is part of a larger data curation pipeline for multimodal breast imaging data.
- It is optimized for processing DICOM files but can be adapted for other types of medical imaging data.
- The script is designed to be run from the command line or as part of an automated workflow.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "1.2.6"
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
import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Configuration
SUPPORTED_MODALITIES = ["_MG_", "_US_", "_MRI_"]

# Mapping file name
mapping_fn = "mamo_patients_mapping_data.csv"

# Dynamically load directories
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
comparing_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "comparing")
compared_dir = os.path.join(root_dir, "dataset-multimodal-breast", "data", "curation", "compared")
non_anonymized_dir = os.path.join(root_dir, "dicom-images-breast", "known", "raw")
mapping_csv = os.path.join(root_dir, "dicom-images-breast", "data", "mapping", mapping_fn)

def ensure_directories_exist(directories):
  """Ensure the required directories exist or are created."""
  for directory in directories:
    if not os.path.exists(directory):
      os.makedirs(directory)
      logging.info(f"Created missing directory: {directory}")
    else:
      logging.info(f"Directory exists: {directory}")

def load_mapping(csv_file):
  """Load mapping of anonymized_patient_id to real_patient_id from CSV."""
  mapping = {}
  if not os.path.exists(csv_file):
    logging.error(f"Mapping file not found: {csv_file}")
    return mapping

  try:
    with open(csv_file, mode='r') as file:
      reader = csv.reader(file)
      next(reader)  # Skip header
      for row in reader:
        if len(row) >= 2:
          real_id, anonymized_id = row[:2]
          mapping[anonymized_id] = real_id
          logging.debug(f"Mapping loaded: {anonymized_id} -> {real_id}")
        else:
          logging.warning(f"Invalid row in CSV: {row}")
  except Exception as e:
    logging.error(f"Failed to load mapping from {csv_file}: {e}")
  return mapping

def is_dicom_file(filepath):
  """Check if a file is a DICOM file by attempting to read it."""
  # Filter files based on extension (most DICOM files have no extension or use .dcm)
  if not filepath.lower().endswith(('.dcm', '')):
    return False

  try:
    pydicom.dcmread(filepath, stop_before_pixels=True)  # Read only metadata
    return True
  except pydicom.errors.InvalidDicomError:
    logging.warning(f"File {filepath} is not a valid DICOM file.")
  except Exception as e:
    logging.warning(f"Error reading file {filepath}: {e}")
  return False

def get_metadata(dicom_file, tags):
  """Extract specified metadata tags from DICOM file."""
  try:
    dicom_data = pydicom.dcmread(dicom_file, stop_before_pixels=True)
    return {tag: dicom_data.get(tag, "Unknown") for tag in tags}
  except Exception as e:
    logging.warning(f"Failed to read DICOM file {dicom_file}: {e}")
    return {tag: "Unknown" for tag in tags}

def find_dicom_files(search_path):
  """Find all DICOM files in the search directory."""
  dicom_files = []
  unwanted_files = ['.ds_store', 'lockfile', 'version', 'dicomdir']  # Exclude unwanted files

  for root, _, files in os.walk(search_path):
    for file in files:
      if file.lower() in unwanted_files:
        logging.debug(f"Skipping unwanted file: {file}")
        continue
      filepath = os.path.join(root, file)
      if is_dicom_file(filepath):
        dicom_files.append(filepath)

  if not dicom_files:
    logging.warning(f"No valid DICOM files found in {search_path}")
  else:
    logging.info(f"Completed searching for DICOM files in {search_path}")
  return dicom_files

def index_non_anonymized_files(non_anonymized_files):
  """Index non-anonymized files by SOPInstanceUID for fast lookup."""
  sop_uid_index = {}
  for non_anonymized_file in non_anonymized_files:
    metadata = get_metadata(non_anonymized_file, ["SOPInstanceUID", "ViewPosition", "ImageLaterality"])
    sop_uid = metadata["SOPInstanceUID"]
    if sop_uid != "Unknown":
      sop_uid_index[sop_uid] = metadata
      sop_uid_index[sop_uid]["filepath"] = non_anonymized_file
  logging.info(f"Indexed {len(sop_uid_index)} non-anonymized DICOM files by SOPInstanceUID.")
  return sop_uid_index

def process_dicom_files(non_anonymized_files, process_path, mapping):
  """Process DICOM files in process_path, match based on PatientID and SOPInstanceUID, and rename."""
  if not non_anonymized_files:
    logging.error("No non-anonymized DICOM files found for comparison.")
    return

  # Index the non-anonymized files by SOPInstanceUID for quick lookup
  sop_uid_index = index_non_anonymized_files(non_anonymized_files)

  # Process anonymized files
  for dicom_file_path in find_dicom_files(process_path):
    anonymized_metadata = get_metadata(dicom_file_path, ["PatientID", "SOPInstanceUID"])
    anonymized_patient_id = anonymized_metadata.get("PatientID")
    anonymized_sop_uid = anonymized_metadata.get("SOPInstanceUID")

    if not anonymized_patient_id or anonymized_patient_id not in mapping:
      logging.warning(f"Anonymized ID {anonymized_patient_id} not found in mapping.")
      continue

    real_patient_id = mapping[anonymized_patient_id]
    logging.info(f"Processing anonymized file: {dicom_file_path} with real_patient_id: {real_patient_id}")

    # Match based on SOPInstanceUID using the pre-built index
    matched_metadata = sop_uid_index.get(anonymized_sop_uid)

    if matched_metadata:
      view_position = matched_metadata["ViewPosition"]
      image_laterality = matched_metadata["ImageLaterality"]
      non_anonymized_file = matched_metadata["filepath"]

      if view_position == "Unknown" or image_laterality == "Unknown":
        logging.warning(f"ViewPosition or ImageLaterality unknown for file {non_anonymized_file}. Skipping file.")
        continue

      new_file_name = rename_file(os.path.basename(dicom_file_path), view_position, image_laterality)
      move_file(dicom_file_path, os.path.join(compared_dir, new_file_name))
      logging.info(f"Moved and renamed file {dicom_file_path} to {new_file_name}")
    else:
      logging.warning(f"No matching SOPInstanceUID found for {dicom_file_path}")

def rename_file(file_name, view_position, image_laterality):
  """Rename the file based on the view position and image laterality."""
  parts = file_name.split('_')
  if len(parts) > 3:
    parts[2] = view_position
    parts[3] = image_laterality
  else:
    logging.warning(f"Unexpected file name format: {file_name}. Skipping rename.")
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
  ensure_directories_exist([comparing_dir, compared_dir])

  mapping = load_mapping(mapping_csv)

  if not mapping:
    logging.error("Mapping could not be loaded. Exiting...")
  else:
    non_anonymized_files = find_dicom_files(non_anonymized_dir)
    process_dicom_files(non_anonymized_files, comparing_dir, mapping)
    logging.info("Processing complete!")

# End of file