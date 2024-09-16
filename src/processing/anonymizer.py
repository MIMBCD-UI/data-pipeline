#!/usr/bin/env python

"""
anonymizer.py: Anonymize DICOM files by removing patient-related
information and renaming them according to a specified format.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.6.1"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import logging
import pydicom

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root directory and folders to save metadata
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
pre_folder = os.path.join(root_dir, "dicom-images-breast", "data", "meta", "pre")
post_folder = os.path.join(root_dir, "dicom-images-breast", "data", "meta", "post")

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
    logging.info(f"{file_path} is a DICOM file.")
    return True
  except Exception:
    logging.info(f"{file_path} is not a DICOM file.")
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
    filename_suffix = f"_{anon_params['date']}_{anon_params['instance'].zfill(4)}.dcm.txt"
    filename_prefix = generate_filename_prefix(anon_params)
    metadata_file_path = os.path.join(meta_to_save_path, f"{filename_prefix}{filename_suffix}")
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
    metadata_file_path = os.path.join(meta_to_save_path, f"{os.path.basename(dicom_file_path)}.txt")
    with open(metadata_file_path, "w") as f:
      f.write(str(dicom_meta))
    logging.info(f"Metadata saved as {metadata_file_path}")
  except Exception as e:
    logging.error(f"Failed to save metadata for {dicom_file_path}: {e}")

def generate_filename_prefix(anon_params):
  """
  Generate the filename prefix based on anonymization parameters.

  Args:
    anon_params (dict): Dictionary containing anonymization parameters.

  Returns:
    str: Generated filename prefix.
  """
  if anon_params['modality'] == "MG":
    return f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['laterality']}"
  elif anon_params['modality'] == "US":
    return f"{anon_params['anon_patient_id']}_{anon_params['modality']}"
  elif anon_params['modality'] == "MR":
    return f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['series']}"
  else:
    return f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['date']}"

def anonymize_dicom_file(input_path, output_path, anon_params):
  """
  Anonymize a DICOM file and rename it according to the specified format.

  Args:
    input_path (str): Path to the input DICOM file.
    output_path (str): Path to save the anonymized DICOM file.
    anon_params (dict): Dictionary containing anonymization parameters.
  """
  try:
    save_meta_pre(pre_folder, input_path, anon_params)
    ds = pydicom.dcmread(input_path)

    # Anonymize patient-related fields
    anonymize_field(ds, 'PatientName', "Anonymous")
    anonymize_field(ds, 'PatientID', anon_params['anon_patient_id'])
    anonymize_field(ds, 'PatientBirthDate', "")
    anonymize_field(ds, 'PatientSex', "")
    anonymize_field(ds, 'PatientAge', "")
    anonymize_field(ds, 'StudyDescription', "")
    anonymize_field(ds, 'SeriesDescription', "")
    anonymize_field(ds, 'InstitutionName', "")
    anonymize_field(ds, 'InstitutionAddress', "")
    anonymize_field(ds, 'InstitutionalDepartmentName', "")
    anonymize_field(ds, 'ReferringPhysicianName', "")
    anonymize_field(ds, 'PhysiciansOfRecord', "")
    anonymize_field(ds, 'WindowCenterWidthExplanation', "")
    anonymize_field(ds, 'RequestingPhysician', "")
    anonymize_field(ds, 'RequestedProcedureDescription', "")
    anonymize_field(ds, 'PerformedProcedureStepDescription', "")
    anonymize_field(ds, 'ScheduledProcedureStepDescription', "")
    anonymize_field(ds, '(0x07a3, 0x1019)', "")
    anonymize_field(ds, '(0x07a3, 0x101c)', "")
    anonymize_field(ds, '(0x0040, 0x0007)', "")

    if hasattr(ds, 'RequestedProcedureCodeSequence'):
      for seq_item in ds.RequestedProcedureCodeSequence:
        anonymize_field(seq_item, 'CodeMeaning', "")

    if hasattr(ds, 'RequestAttributesSequence'):
      for seq_item in ds.RequestAttributesSequence:
        anonymize_field(seq_item, 'ScheduledProcedureStepDescription', "")

    if hasattr(ds, 'ConceptNameCodeSequence'):
      anonymize_field(ds.ConceptNameCodeSequence[0], 'CodeMeaning', "")

    if hasattr(ds, 'PerformingPhysicianName'):
      anonymize_field(ds, 'PerformingPhysicianName', "")

    if 'ProcedureCodeSequence' in ds:
      for seq_item in ds.ProcedureCodeSequence:
        anonymize_field(seq_item, 'CodeMeaning', "")

    save_dicom(ds, output_path, anon_params)
  except pydicom.errors.InvalidDicomError:
    logging.warning(f"Ignoring DICOM file with invalid value: {input_path}")
  except Exception as e:
    logging.error(f"Anonymization failed for {input_path}: {e}")

def anonymize_field(ds, field_name, new_value):
  """
  Anonymize a specific field in the DICOM dataset.

  Args:
    ds (Dataset): The DICOM dataset.
    field_name (str): The name of the field to anonymize.
    new_value (str): The new value to set for the field.
  """
  if hasattr(ds, field_name):
    setattr(ds, field_name, new_value)
    logging.info(f"Anonymized {field_name}: {new_value}")
  else:
    logging.info(f"Field {field_name} not found in DICOM file.")

def save_dicom(ds, output_path, anon_params):
  """
  Save the anonymized DICOM file and update its name.

  Args:
    ds (Dataset): The DICOM dataset.
    output_path (str): The path to save the anonymized DICOM file.
    anon_params (dict): Dictionary containing anonymization parameters.
  """
  ds.save_as(output_path)
  save_meta_post(post_folder, output_path)

  filename_prefix = generate_filename_prefix(anon_params)
  filename_suffix = f"_{anon_params['date']}_{anon_params['instance'].zfill(4)}.dcm"
  new_filename = f"{filename_prefix}{filename_suffix}"
  os.rename(output_path, os.path.join(os.path.dirname(output_path), new_filename))
  logging.info(f"Anonymized file saved as {new_filename}")

# End of file