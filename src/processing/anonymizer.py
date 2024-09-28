#!/usr/bin/env python

"""
anonymizer.py: Anonymize DICOM files by removing patient-related
information and renaming them according to a specified format.
This script handles the anonymization of sensitive fields in DICOM files 
and provides options to save the metadata before and after the anonymization process.

Key Functions:
- is_dicom_file: Check if a file is a valid DICOM file.
- anonymize_dicom_file: Anonymize a DICOM file by removing patient-related information.
- anonymize_field: Replace a DICOM field's value with a new value.
- anonymize_sequences: Anonymize specific DICOM sequence fields.
- save_dicom: Save the anonymized DICOM file with a new name.
- anonymize_directory: Anonymize all DICOM files in a directory.

Expected Input:
- A directory containing DICOM files to be anonymized.
- An optional configuration file with anonymization rules.
- Output directory for saving the anonymized files.

Output:
- Anonymized DICOM files saved in the output directory.
- Metadata files saved before and after anonymization for each DICOM file.

Intended Use Case:
- This script is useful for anonymizing DICOM files for research or sharing purposes.
- It can be used to remove sensitive patient information from medical imaging data.
- The script is designed to be run from the command line or as part of an automated workflow.

Customization & Flexibility:
- The script can be extended to support additional anonymization rules or fields.
- It can be adapted to handle other types of medical imaging data or metadata.
- The script can be integrated into a larger data curation pipeline for multimodal breast imaging data.

Performance & Compatibility:
- The script is optimized for performance and efficiency when processing DICOM files.
- It uses the pydicom library for reading and writing DICOM files.

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
__version__ = "0.6.8"  # Version incremented to reflect improvements
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import logging
import pydicom

# Configure logging to capture detailed debugging information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define root directory paths for metadata storage (before and after anonymization)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
pre_folder = os.path.join(root_dir, "dicom-images-breast", "data", "meta", "pre")
post_folder = os.path.join(root_dir, "dicom-images-breast", "data", "meta", "post")

# Ensure that the pre- and post-anonymization folders exist
os.makedirs(pre_folder, exist_ok=True)
os.makedirs(post_folder, exist_ok=True)
logging.info(f"Pre-anonymization folder: {pre_folder}")
logging.info(f"Post-anonymization folder: {post_folder}")

def is_dicom_file(file_path):
  """
  Check if a given file is a valid DICOM file by attempting to read its metadata.

  Args:
    file_path (str): Path to the file.

  Returns:
    bool: True if the file is a valid DICOM file, False otherwise.
  """
  try:
    # Attempt to read the DICOM header (excluding pixel data)
    pydicom.dcmread(file_path, stop_before_pixels=True)
    logging.info(f"File '{file_path}' is a valid DICOM file.")
    return True
  except Exception as e:
    logging.warning(f"File '{file_path}' is not a valid DICOM file. Error: {e}")
    return False

def save_meta_pre(dicom_file_path, anon_params):
  """
  Save the pre-anonymization metadata to the specified folder (pre_folder).

  Args:
    dicom_file_path (str): Path to the original DICOM file.
    anon_params (dict): Dictionary containing anonymization parameters.
  """
  try:
    # Read the metadata of the DICOM file
    dicom_meta = pydicom.dcmread(dicom_file_path)
    
    # Construct the filename for saving metadata
    filename_suffix = f"_{anon_params['date']}_{anon_params['instance'].zfill(4)}.dcm.txt"
    filename_prefix = generate_filename_prefix(anon_params)
    metadata_file_path = os.path.join(pre_folder, f"{filename_prefix}{filename_suffix}")
    
    # Save the metadata to the pre-folder
    with open(metadata_file_path, "w") as f:
      f.write(str(dicom_meta))
    
    logging.info(f"Pre-anonymization metadata saved at '{metadata_file_path}'")
    return metadata_file_path
  except Exception as e:
    logging.error(f"Failed to save pre-anonymization metadata for '{dicom_file_path}': {e}")
    return None

def save_meta_post(dicom_file_path):
  """
  Save the post-anonymization metadata to the specified folder (post_folder).

  Args:
    dicom_file_path (str): Path to the anonymized DICOM file.
  """
  try:
    # Read the metadata of the anonymized DICOM file
    dicom_meta = pydicom.dcmread(dicom_file_path)
    
    # Save metadata in post-folder with a .txt extension
    metadata_file_path = os.path.join(post_folder, f"{os.path.basename(dicom_file_path)}.txt")
    
    # Write metadata to the post-anonymization folder
    with open(metadata_file_path, "w") as f:
      f.write(str(dicom_meta))
    
    logging.info(f"Post-anonymization metadata saved at '{metadata_file_path}'")
    return metadata_file_path
  except Exception as e:
    logging.error(f"Failed to save post-anonymization metadata for '{dicom_file_path}': {e}")
    return None

def generate_filename_prefix(anon_params):
  """
  Generate a filename prefix based on anonymization parameters.

  Args:
    anon_params (dict): Dictionary containing anonymization parameters.

  Returns:
    str: Generated filename prefix.
  """
  try:
    # Generate the filename prefix based on the modality and parameters
    if anon_params['modality'] == "MG":
      return f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['laterality']}"
    elif anon_params['modality'] == "US":
      return f"{anon_params['anon_patient_id']}_{anon_params['modality']}"
    elif anon_params['modality'] == "MR":
      return f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['series']}"
    else:
      return f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['date']}"
  except KeyError as e:
    logging.error(f"Missing key in anonymization parameters: {e}")
    return "unknown"

def anonymize_dicom_file(input_path, output_path, anon_params):
  """
  Anonymize a DICOM file by removing sensitive fields and saving the file with a new name.

  Args:
    input_path (str): Path to the original DICOM file.
    output_path (str): Path to save the anonymized DICOM file.
    anon_params (dict): Dictionary containing anonymization parameters.
  """
  try:
    # Save the metadata before anonymization
    pre_meta_path = save_meta_pre(input_path, anon_params)
    if pre_meta_path is None:
      logging.error("Pre-anonymization metadata saving failed. Aborting anonymization.")
      return

    # Read the DICOM file into a dataset
    ds = pydicom.dcmread(input_path)

    # List of fields to anonymize by clearing their values
    fields_to_anonymize = ['PatientName', 'PatientBirthDate', 'PatientSex', 'PatientAge',
                           'StudyDescription', 'SeriesDescription', 'InstitutionName', 'InstitutionAddress',
                           'InstitutionalDepartmentName', 'ReferringPhysicianName', 'PhysiciansOfRecord',
                           'WindowCenterWidthExplanation', 'RequestingPhysician', 'RequestedProcedureDescription',
                           'PerformedProcedureStepDescription', 'ScheduledProcedureStepDescription', 
                           '(0x07a3, 0x1019)', '(0x07a3, 0x101c)', '(0x0040, 0x0007)']

    # Anonymize each sensitive field
    for field in fields_to_anonymize:
      anonymize_field(ds, field, "")

    # Update the PatientID with the anonymized ID
    anonymize_field(ds, 'PatientID', anon_params['anon_patient_id'])

    # Handle anonymization of sequence fields (e.g., ProcedureCodeSequence)
    anonymize_sequences(ds)

    # Save the anonymized DICOM file
    save_dicom(ds, output_path, anon_params)
  except pydicom.errors.InvalidDicomError:
    logging.warning(f"Invalid DICOM file: '{input_path}'")
  except Exception as e:
    logging.error(f"Anonymization failed for '{input_path}': {e}")

def anonymize_field(ds, field_name, new_value):
  """
  Replace a DICOM field's value with a new value.

  Args:
    ds (Dataset): The DICOM dataset.
    field_name (str): The name of the field to anonymize.
    new_value (str): The new value to set for the field.
  """
  if hasattr(ds, field_name):
    # Set the field to the new (anonymized) value
    setattr(ds, field_name, new_value)
    logging.info(f"Anonymized field '{field_name}' with new value.")
  else:
    logging.debug(f"Field '{field_name}' not found in the DICOM file.")

def anonymize_sequences(ds):
  """
  Anonymize specific DICOM sequence fields.

  Args:
    ds (Dataset): The DICOM dataset.
  """
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

def save_dicom(ds, output_path, anon_params):
  """
  Save the anonymized DICOM file with a new name.

  Args:
    ds (Dataset): The DICOM dataset.
    output_path (str): The path to save the anonymized file.
    anon_params (dict): Dictionary containing anonymization parameters.
  """
  # Save the anonymized dataset as a new DICOM file
  ds.save_as(output_path)
  
  # Save post-anonymization metadata
  post_meta_path = save_meta_post(output_path)
  if post_meta_path is None:
    logging.error("Post-anonymization metadata saving failed. Anonymized file renaming aborted.")
    return

  # Generate a new filename based on anonymization parameters
  filename_prefix = generate_filename_prefix(anon_params)
  filename_suffix = f"_{anon_params['date']}_{anon_params['instance'].zfill(4)}.dcm"
  new_filename = f"{filename_prefix}{filename_suffix}"
  
  # Rename the anonymized file
  new_file_path = os.path.join(os.path.dirname(output_path), new_filename)
  os.rename(output_path, new_file_path)
  
  logging.info(f"Anonymized DICOM file saved as '{new_filename}'")

# End of file