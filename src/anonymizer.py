#!/usr/bin/env python

"""
anonymizer.py: Anonymize DICOM files by removing patient-related
information and renaming them according to a specified format.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.5.0"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago", "Jacinto C. Nascimento"]

import pydicom
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root directory and folders to save metadata.
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
pre_folder = os.path.join(root_dir, "dicom-images-breast", "data", "meta", "pre", "")
post_folder = os.path.join(root_dir, "dicom-images-breast", "data", "meta", "post", "")

def is_dicom_file(file_path):
  """
  Check if a file is a DICOM file.

  Args:
      file_path (str): Path to the file.

  Returns:
      bool: True if the file is a DICOM file, False otherwise.
  """
  try:
    pydicom.dcmread(file_path, stop_before_pixels=True)
    return True
  except Exception:
    return False

# 
def save_meta(meta_to_save_path, dicom_file_path):
    """
    Save the DICOM file metadata to a text file.

    Args:
        dicom_file (str): Path to the DICOM file.
    """
    try:
      dicom_meta = pydicom.dcmread(dicom_file_path)
      dicom_file = os.path.basename(dicom_file_path)
      metadata_file_path = os.path.join(meta_to_save_path, f"{dicom_file}.txt")
      with open(metadata_file_path, "w") as f:
        f.write(str(dicom_meta))
      logging.info(f"Metadata saved as {metadata_file_path}")
    except Exception as e:
      logging.error(f"Failed to save metadata for {meta_to_save_path}: {e}")

def anonymize_dicom_file(input_path, output_path, anon_patient_id, modality, view, laterality, date, sequence, instance):
  """
  Anonymize a DICOM file and rename it according to the specified format.

  Args:
      input_path (str): Path to the input DICOM file.
      output_path (str): Path to save the anonymized DICOM file.
      anon_patient_id (str): Anonymized patient ID.
      modality (str): Imaging modality (e.g., MR, CT, US).
      laterality (str): Laterality of the breast (e.g., L, R, NA for US).
      view (str): View of the breast (e.g., CC, MLO, NA for US).
      date (str): Date of the exam in YYYYMMDD format.
      sequence (str): Sequence or protocol used within the modality.
      instance (str): Numeric identifier for each image or slice within a series.
  """
  try:
    # Read DICOM file
    ds = pydicom.dcmread(input_path)

    # Anonymize patient-related fields
    ds.PatientName = "Anonymous"
    ds.PatientID = anon_patient_id
    ds.InstitutionName = "ISTtestFMC"
    ds.InstitutionAddress = "ISTAddressTestFMC"

    # Save anonymized DICOM file
    post = output_path
    ds.save_as(output_path)

    # Save metadata after anonymization
    save_meta(post_folder, post)

    # Determine filename suffix based on modality
    filename_suffix = f"_{date}_{instance.zfill(4)}.dcm"

    # Construct filename prefix
    if modality == "MG":
      filename_prefix = f"{anon_patient_id}_{modality}_{laterality}"
    elif modality == "US":
      filename_prefix = f"{anon_patient_id}_{modality}"
    elif modality == "MR":
      filename_prefix = f"{anon_patient_id}_{modality}_{sequence}"
    else:
      filename_prefix = f"{anon_patient_id}_{modality}_{view}_{date}"

    # Rename anonymized file according to the specified format
    os.rename(output_path, os.path.join(os.path.dirname(output_path), f"{filename_prefix}{filename_suffix}"))

    logging.info(f"Anonymized file saved as {filename_prefix}{filename_suffix}")
  except Exception as e:
    logging.error(f"Anonymization failed for {input_path}: {e}")
