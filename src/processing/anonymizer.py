#!/usr/bin/env python

"""
anonymizer.py: Anonymize DICOM files by removing patient-related
information and renaming them according to a specified format.
This script handles the anonymization of sensitive fields in DICOM files 
and provides options to save the metadata before and after the anonymization process.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.6.2"  # Version updated to reflect new improvements
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import logging
import pydicom

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define root directories and folders for saving metadata
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
pre_folder = os.path.join(root_dir, "dicom-images-breast", "data", "meta", "pre")
post_folder = os.path.join(root_dir, "dicom-images-breast", "data", "meta", "post")

def is_dicom_file(file_path):
  """
  Check if a given file is a DICOM file by attempting to read its metadata.

  Args:
    file_path (str): The path to the file.

  Returns:
    bool: True if the file is a valid DICOM file, False otherwise.
  """
  try:
    # Attempt to read the DICOM file
    pydicom.dcmread(file_path, stop_before_pixels=True)
    logging.info(f"{file_path} is a valid DICOM file.")
    return True
  except Exception:
    logging.warning(f"{file_path} is not a valid DICOM file.")
    return False

def save_meta_pre(meta_to_save_path, dicom_file_path, anon_params):
  """
  Save metadata of the DICOM file before anonymization to a text file.

  Args:
    meta_to_save_path (str): Directory path where metadata will be saved.
    dicom_file_path (str): Path to the original DICOM file.
    anon_params (dict): Dictionary containing anonymization parameters.
  """
  try:
    # Read the DICOM file metadata
    dicom_meta = pydicom.dcmread(dicom_file_path)
    # Generate a metadata filename based on anonymization parameters
    filename_suffix = f"_{anon_params['date']}_{anon_params['instance'].zfill(4)}.dcm.txt"
    filename_prefix = generate_filename_prefix(anon_params)
    metadata_file_path = os.path.join(meta_to_save_path, f"{filename_prefix}{filename_suffix}")

    # Save the metadata to a text file
    with open(metadata_file_path, "w") as f:
      f.write(str(dicom_meta))
    
    logging.info(f"Pre-anonymization metadata saved as {metadata_file_path}")
  except Exception as e:
    logging.error(f"Failed to save pre-anonymization metadata for {dicom_file_path}: {e}")

def save_meta_post(meta_to_save_path, dicom_file_path):
  """
  Save metadata of the DICOM file after anonymization to a text file.

  Args:
    meta_to_save_path (str): Directory path where metadata will be saved.
    dicom_file_path (str): Path to the anonymized DICOM file.
  """
  try:
    # Read the DICOM file metadata after anonymization
    dicom_meta = pydicom.dcmread(dicom_file_path)
    metadata_file_path = os.path.join(meta_to_save_path, f"{os.path.basename(dicom_file_path)}.txt")

    # Save the metadata to a text file
    with open(metadata_file_path, "w") as f:
      f.write(str(dicom_meta))
    
    logging.info(f"Post-anonymization metadata saved as {metadata_file_path}")
  except Exception as e:
    logging.error(f"Failed to save post-anonymization metadata for {dicom_file_path}: {e}")

def generate_filename_prefix(anon_params):
  """
  Generate a filename prefix based on anonymization parameters such as modality and patient ID.

  Args:
    anon_params (dict): Dictionary containing anonymization parameters.

  Returns:
    str: The generated filename prefix.
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
  Anonymize a DICOM file by removing sensitive patient information and renaming it.

  Args:
    input_path (str): Path to the original DICOM file.
    output_path (str): Path to save the anonymized DICOM file.
    anon_params (dict): Dictionary containing anonymization parameters.
  """
  try:
    # Save pre-anonymization metadata
    save_meta_pre(pre_folder, input_path, anon_params)

    # Read the DICOM file
    ds = pydicom.dcmread(input_path)

    # Anonymize sensitive fields
    fields_to_anonymize = ['PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex', 'PatientAge', 'StudyDescription', 
                           'SeriesDescription', 'InstitutionName', 'InstitutionAddress', 'InstitutionalDepartmentName', 
                           'ReferringPhysicianName', 'PhysiciansOfRecord', 'WindowCenterWidthExplanation', 
                           'RequestingPhysician', 'RequestedProcedureDescription', 'PerformedProcedureStepDescription', 
                           'ScheduledProcedureStepDescription', '(0x07a3, 0x1019)', '(0x07a3, 0x101c)', '(0x0040, 0x0007)']

    for field in fields_to_anonymize:
      anonymize_field(ds, field, "")

    # Anonymize sequence fields
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

    # Save the anonymized DICOM file
    save_dicom(ds, output_path, anon_params)
  except pydicom.errors.InvalidDicomError:
    logging.warning(f"Invalid DICOM file: {input_path}")
  except Exception as e:
    logging.error(f"Anonymization failed for {input_path}: {e}")

def anonymize_field(ds, field_name, new_value):
  """
  Replace the value of a field in the DICOM dataset.

  Args:
    ds (Dataset): The DICOM dataset.
    field_name (str): The name of the field to anonymize.
    new_value (str): The new value for the field.
  """
  if hasattr(ds, field_name):
    setattr(ds, field_name, new_value)
    logging.info(f"Anonymized field {field_name}: {new_value}")
  else:
    logging.debug(f"Field {field_name} not found in the DICOM file.")

def save_dicom(ds, output_path, anon_params):
  """
  Save the anonymized DICOM file to the output path and rename it.

  Args:
    ds (Dataset): The DICOM dataset.
    output_path (str): The path to save the anonymized file.
    anon_params (dict): Dictionary containing anonymization parameters.
  """
  ds.save_as(output_path)
  
  # Save post-anonymization metadata
  save_meta_post(post_folder, output_path)

  # Generate a new file name based on the anonymization parameters
  filename_prefix = generate_filename_prefix(anon_params)
  filename_suffix = f"_{anon_params['date']}_{anon_params['instance'].zfill(4)}.dcm"
  new_filename = f"{filename_prefix}{filename_suffix}"
  
  # Rename the anonymized file
  new_file_path = os.path.join(os.path.dirname(output_path), new_filename)
  os.rename(output_path, new_file_path)

  logging.info(f"Anonymized DICOM file saved as {new_filename}")

# End of file