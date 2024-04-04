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
__credits__ = ["Carlos Santiago",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import pydicom
import os
import logging
import pydicom

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

def save_meta_pre(meta_to_save_path, dicom_file_path, anon_params):
  """
  Save the DICOM file metadata to a text file before anonymization.

  Args:
    meta_to_save_path (str): Path to the folder to save metadata.
    dicom_file_path (str): Path to the DICOM file.
    anon_params (dict): Dictionary containing anonymization parameters.
  """
  try:
    dicom_meta = pydicom.dcmread(dicom_file_path)
    dicom_file = os.path.basename(dicom_file_path)

    # Determine filename suffix based on modality
    filename_suffix = f"_{anon_params['date']}_{anon_params['instance'].zfill(4)}.dcm.txt"

    # Construct filename prefix
    if anon_params['modality'] == "MG":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['laterality']}"
    elif anon_params['modality'] == "US":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}"
    elif anon_params['modality'] == "MR":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['series']}"
    else:
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['date']}"

    metadata_file_path = os.path.join(meta_to_save_path, f"{filename_prefix}{filename_suffix}")

    # Save DICOM metadata to the metadata file
    with open(metadata_file_path, "w") as f:
      f.write(str(dicom_meta))

    logging.info(f"Metadata saved as {metadata_file_path}")
  except Exception as e:
    logging.error(f"Failed to save metadata for {dicom_file_path}: {e}")

def save_meta_post(meta_to_save_path, dicom_file_path):
  """
  Save the DICOM file metadata to a text file after anonymization.

  Args:
    meta_to_save_path (str): Path to save the metadata.
    dicom_file_path (str): Path to the DICOM file.
  """
  try:
    dicom_meta = pydicom.dcmread(dicom_file_path)
    dicom_file = os.path.basename(dicom_file_path)
    metadata_file_path = os.path.join(meta_to_save_path, f"{dicom_file}.txt")

    # Save DICOM metadata to the metadata file
    with open(metadata_file_path, "w") as f:
      f.write(str(dicom_meta))

    logging.info(f"Metadata saved as {metadata_file_path}")
  except Exception as e:
    logging.error(f"Failed to save metadata for {meta_to_save_path}: {e}")

def anonymize_dicom_file(input_path, output_path, anon_params):
  """
  Anonymize a DICOM file and rename it according to the specified format.

  Args:
    input_path (str): Path to the input DICOM file.
    output_path (str): Path to save the anonymized DICOM file.
    anon_params (dict): Dictionary containing anonymization parameters.
  """
  try:
    # Save metadata before anonymization
    save_meta_pre(pre_folder, input_path, anon_params)

    # Read DICOM file
    ds = pydicom.dcmread(input_path)

    # Anonymize patient-related fields
    ds.PatientName = "Anonymous"
    ds.PatientID = anon_params['anon_patient_id']
    ds.PatientBirthDate = ""
    ds.PatientSex = ""
    ds.PatientAge = ""

    # Anonymize Study Description
    ds.StudyDescription = ""

    # Anonymize institution-related fields
    ds.InstitutionName = ""
    ds.InstitutionAddress = ""
    ds.InstitutionalDepartmentName = ""

    # Anonymize referring physician-related fields
    ds.ReferringPhysicianName = ""
    ds.PhysiciansOfRecord = ""

    # Anonymize Window Center & Width Explanation
    ds.WindowCenterWidthExplanation = ""

    # Anonymize other fields
    ds.RequestingPhysician = ""
    ds.RequestedProcedureDescription = ""
    ds.CodeMeaning = ""
    ds.PerformedProcedureStepDescription = ""
    ds.ScheduledProcedureStepDescription = ""

    # Anonymize Private tag data (07a3, 1019) if it exists
    if (0x07a3, 0x1019) in ds:
      ds[(0x07a3, 0x1019)].value = ""

    # Anonymize Private tag data (07a3, 101c) if it exists
    if (0x07a3, 0x101c) in ds:
      ds[(0x07a3, 0x101c)].value = ""
    
    # Anonymize Private tag data (0040, 0007) if it exists
    if (0x0040, 0x0007) in ds:
      ds[(0x0040, 0x0007)].value = ""

    # Iterate over anonymized Requested Procedure Code Sequence
    if hasattr(ds, 'RequestedProcedureCodeSequence'):
      for seq_item in ds.RequestedProcedureCodeSequence:
        if 'CodeMeaning' in seq_item:
          # Anonymize code meaning in Requested Procedure Code Sequence
          seq_item.CodeMeaning = ""
    
    # Iterate over Request Attributes Sequence
    for seq_item in ds.RequestAttributesSequence:
      if 'ScheduledProcedureStepDescription' in seq_item:
        seq_item.ScheduledProcedureStepDescription = ""

    if hasattr(ds, 'ConceptNameCodeSequence'):
      ds.ConceptNameCodeSequence[0].CodeMeaning = ""

    ds.PerformingPhysicianName = ""

    if 'ProcedureCodeSequence' in ds:
      for seq_item in ds.ProcedureCodeSequence:
        seq_item.CodeMeaning = ""

    if hasattr(ds, 'CodeMeaning'):
      ds.CodeMeaning = ""

    # Save anonymized DICOM file
    post = output_path
    ds.save_as(output_path)

    # Save metadata after anonymization
    save_meta_post(post_folder, post)

    # Determine filename suffix based on modality
    filename_suffix = f"_{anon_params['date']}_{anon_params['instance'].zfill(4)}.dcm"

    # Construct filename prefix
    if anon_params['modality'] == "MG":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['laterality']}"
    elif anon_params['modality'] == "US":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}"
    elif anon_params['modality'] == "MR":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['series']}"
    else:
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['date']}"

    # Rename anonymized file according to the specified format
    os.rename(output_path, os.path.join(os.path.dirname(output_path), f"{filename_prefix}{filename_suffix}"))

    logging.info(f"Anonymized file saved as {filename_prefix}{filename_suffix}")
  except Exception as e:
    logging.error(f"Anonymization failed for {input_path}: {e}")

# End of file