#!/usr/bin/env python

"""
anonymizer.py: Anonymize DICOM files by removing patient-related
information and renaming them according to a specified format.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.6.0"
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
    logging.info(f"Checking if {file_path} is a DICOM file...")
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
    logging.info(f"Saving metadata for {dicom_file_path} to {meta_to_save_path}...")
    # Read DICOM file
    dicom_meta = pydicom.dcmread(dicom_file_path)
    logging.info(f"DICOM file metadata: {dicom_meta}")

    # Determine filename suffix based on modality
    filename_suffix = f"_{anon_params['date']}_{anon_params['instance'].zfill(4)}.dcm.txt"
    logging.info(f"Filename suffix: {filename_suffix}")

    # Construct filename prefix
    if anon_params['modality'] == "MG":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['laterality']}"
      logging.info(f"Filename prefix: {filename_prefix}")
    elif anon_params['modality'] == "US":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}"
      logging.info(f"Filename prefix: {filename_prefix}")
    elif anon_params['modality'] == "MR":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['series']}"
      logging.info(f"Filename prefix: {filename_prefix}")
    else:
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['date']}"
      logging.info(f"Filename prefix: {filename_prefix}")

    # Construct metadata file path
    metadata_file_path = os.path.join(meta_to_save_path, f"{filename_prefix}{filename_suffix}")
    logging.info(f"Metadata file path: {metadata_file_path}")

    # Save DICOM metadata to the metadata file
    with open(metadata_file_path, "w") as f:
      logging.info(f"Saving metadata for {dicom_file_path} to {metadata_file_path}...")
      f.write(str(dicom_meta))
      logging.info(f"Metadata saved for {dicom_file_path} to {metadata_file_path}")

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
    logging.info(f"Saving metadata for {dicom_file_path} to {meta_to_save_path}...")
    dicom_meta = pydicom.dcmread(dicom_file_path)
    logging.info(f"DICOM file metadata: {dicom_meta}")
    dicom_file = os.path.basename(dicom_file_path)
    logging.info(f"Filename: {dicom_file}")
    metadata_file_path = os.path.join(meta_to_save_path, f"{dicom_file}.txt")
    logging.info(f"Metadata file path: {metadata_file_path}")

    # Save DICOM metadata to the metadata file
    with open(metadata_file_path, "w") as f:
      logging.info(f"Saving metadata for {dicom_file_path} to {metadata_file_path}...")
      f.write(str(dicom_meta))
      logging.info(f"Metadata saved for {dicom_file_path} to {metadata_file_path}")

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
    logging.info(f"Saving metadata for {input_path} before anonymization...")
    save_meta_pre(pre_folder, input_path, anon_params)
    logging.info(f"Metadata saved for {input_path} before anonymization.")

    # Read DICOM file
    logging.info(f"Reading DICOM file {input_path}...")
    ds = pydicom.dcmread(input_path)
    logging.info(f"DICOM file read: {ds}")

    # Anonymize patient-related fields
    logging.info(f"Anonymizing patient-related fields...")

    # Anonymize Patient Name
    if hasattr(ds, 'PatientName'):
      logging.info(f"Anonymizing Patient Name: {ds.PatientName}")
      ds.PatientName = "Anonymous"
      logging.info(f"PatientName: {ds.PatientName}")
    else:
      logging.info("Attribute 'PatientName' not found in DICOM file.")

    # Anonymize Patient ID
    if hasattr(ds, 'PatientID'):
      logging.info(f"Anonymizing Patient ID: {ds.PatientID}")
      ds.PatientID = anon_params['anon_patient_id']
      logging.info(f"PatientID: {ds.PatientID}")
    else:
      logging.info("Attribute 'PatientID' not found in DICOM file.")

    # Anonymize Patient's Birth Date
    if hasattr(ds, 'PatientBirthDate'):
      logging.info(f"Anonymizing Patient's Birth Date: {ds.PatientBirthDate}")
      ds.PatientBirthDate = ""
      logging.info(f"PatientBirthDate: {ds.PatientBirthDate}")
    else:
      logging.info("Attribute 'PatientBirthDate' not found in DICOM file.")
    
    # Anonymize Patient's Sex
    if hasattr(ds, 'PatientSex'):
      logging.info(f"Anonymizing Patient's Sex: {ds.PatientSex}")
      ds.PatientSex = ""
      logging.info(f"PatientSex: {ds.PatientSex}")
    else:
      logging.info("Attribute 'PatientSex' not found in DICOM file.")
    
    # Anonymize Patient's Age
    if hasattr(ds, 'PatientAge'):
      logging.info(f"Anonymizing Patient's Age: {getattr(ds, 'PatientAge', 'N/A')}")
      ds.PatientAge = ""
      logging.info(f"PatientAge: {ds.PatientAge}")
    else:
      logging.info("Attribute 'PatientAge' not found in DICOM file.")

    # Anonymize Study Description
    if hasattr(ds, 'StudyDescription'):
      logging.info(f"Anonymizing Study Description: {ds.StudyDescription}")
      ds.StudyDescription = ""
      logging.info(f"StudyDescription: {ds.StudyDescription}")
    else:
      logging.info("Attribute 'StudyDescription' not found in DICOM file.")

    # Anonymize Series Description
    if hasattr(ds, 'SeriesDescription'):
      logging.info(f"Anonymizing Series Description: {ds.SeriesDescription}")
      ds.SeriesDescription = ""
      logging.info(f"SeriesDescription: {ds.SeriesDescription}")
    else:
      logging.info("Attribute 'SeriesDescription' not found in DICOM file.")

    # Anonymize institution-related fields

    # Anonymize Institution Name
    if hasattr(ds, 'InstitutionName'):
      logging.info(f"Anonymizing Institution Name: {ds.InstitutionName}")
      ds.InstitutionName = ""
      logging.info(f"InstitutionName: {ds.InstitutionName}")
    else:
      logging.info("Attribute 'InstitutionName' not found in DICOM file.")

    # Anonymize Institution Address
    if hasattr(ds, 'InstitutionAddress'):
      logging.info(f"Anonymizing Institution Address: {ds.InstitutionAddress}")
      ds.InstitutionAddress = ""
      logging.info(f"InstitutionAddress: {ds.InstitutionAddress}")
    else:
      logging.info("Attribute 'InstitutionAddress' not found in DICOM file.")

    # Anonymize Institutional Department Name
    if hasattr(ds, 'InstitutionalDepartmentName'):
      logging.info(f"Anonymizing Institutional Department Name: {ds.InstitutionalDepartmentName}")
      ds.InstitutionalDepartmentName = ""
      logging.info(f"InstitutionalDepartmentName: {ds.InstitutionalDepartmentName}")
    else:
      logging.info("Institutional Department Name attribute not found.")

    # Anonymize referring physician-related fields

    # Anonymize Referring Physician's Name
    if hasattr(ds, 'ReferringPhysicianName'):
      logging.info(f"Anonymizing Referring Physician's Name:  {ds.ReferringPhysicianName}")
      ds.ReferringPhysicianName = ""
      logging.info(f"ReferringPhysicianName: {ds.ReferringPhysicianName}")
    else:
      logging.info("Attribute 'ReferringPhysicianName' not found in DICOM file.")

    # Anonymize Physician of Record if it exists
    if hasattr(ds, 'PhysiciansOfRecord'):
      logging.info(f"Anonymizing Physician of Record: {ds.PhysiciansOfRecord}")
      ds.PhysiciansOfRecord = ""
      logging.info(f"PhysiciansOfRecord: {ds.PhysiciansOfRecord}")
    else:
      logging.info("PhysiciansOfRecord attribute not found.")

    # Anonymize Window Center & Width Explanation
    if hasattr(ds, 'WindowCenterWidthExplanation'):
      logging.info(f"Anonymizing Window Center & Width Explanation: {ds.WindowCenterWidthExplanation}")
      ds.WindowCenterWidthExplanation = ""
      logging.info(f"WindowCenterWidthExplanation: {ds.WindowCenterWidthExplanation}")
    else:
      logging.info("Attribute 'WindowCenterWidthExplanation' not found in DICOM file.")

    # Anonymize other fields

    # Anonymize Requesting Physician if it exists
    if hasattr(ds, 'RequestingPhysician'):
      logging.info(f"Anonymizing Requesting Physician: {ds.RequestingPhysician}")
      ds.RequestingPhysician = ""
      logging.info(f"RequestingPhysician: {ds.RequestingPhysician}")
    else:
      logging.info("RequestingPhysician attribute not found.")

    # Anonymize Requested Procedure Description if it exists
    if hasattr(ds, 'RequestedProcedureDescription'):
      logging.info(f"Anonymizing Requested Procedure Description: {ds.RequestedProcedureDescription}")
      ds.RequestedProcedureDescription = ""
      logging.info(f"RequestedProcedureDescription: {ds.RequestedProcedureDescription}")
    else:
      logging.info("RequestedProcedureDescription attribute not found.")

    # Anonymize Performed Procedure Step Description
    if hasattr(ds, 'PerformedProcedureStepDescription'):
      logging.info(f"Anonymizing Performed Procedure Step Description: {ds.PerformedProcedureStepDescription}")
      ds.PerformedProcedureStepDescription = ""
      logging.info(f"PerformedProcedureStepDescription: {ds.PerformedProcedureStepDescription}")
    else:
      logging.info("Performed Procedure Step Description attribute not found.")

    # Anonymize Scheduled Procedure Step Description
    if hasattr(ds, 'ScheduledProcedureStepDescription'):
      logging.info(f"Anonymizing Scheduled Procedure Step Description: {ds.ScheduledProcedureStepDescription}")
      ds.ScheduledProcedureStepDescription = ""
      logging.info(f"ScheduledProcedureStepDescription: {ds.ScheduledProcedureStepDescription}")
    else:
      logging.info("Attribute 'ScheduledProcedureStepDescription' not found in DICOM file.")

    # Anonymize Private tag data (07a3, 1019) if it exists
    if hasattr(ds, '(0x07a3, 0x1019)'):
      logging.info(f"Anonymizing Private tag data (07a3, 1019): {ds[(0x07a3, 0x1019)].value}")
      ds[(0x07a3, 0x1019)].value = ""
      logging.info(f"Private tag data (07a3, 1019): {ds[(0x07a3, 0x1019)].value}")
    else:
      logging.info("Attribute (0x07a3, 0x1019) not found in DICOM file.")

    # Anonymize Private tag data (07a3, 101c) if it exists
    if hasattr(ds, '(0x07a3, 0x101c)'):
      logging.info(f"Anonymizing Private tag data (07a3, 101c): {ds[(0x07a3, 0x101c)].value}")
      ds[(0x07a3, 0x101c)].value = ""
      logging.info(f"Private tag data (07a3, 101c): {ds[(0x07a3, 0x101c)].value}")
    else:
      logging.info("Attribute (0x07a3, 0x101c) not found in DICOM file.")
    
    # Anonymize Private tag data (0040, 0007) if it exists
    if hasattr(ds, '(0x0040, 0x0007)'):
      logging.info(f"Anonymizing Private tag data (0040, 0007): {ds[(0x0040, 0x0007)].value}")
      ds[(0x0040, 0x0007)].value = ""
      logging.info(f"Private tag data (0040, 0007): {ds[(0x0040, 0x0007)].value}")
    else:
      logging.info("Attribute (0x0040, 0x0007) not found in DICOM file.")

    # Iterate over anonymized Requested Procedure Code Sequence
    if hasattr(ds, 'RequestedProcedureCodeSequence'):
      logging.info(f"Anonymizing Requested Procedure Code Sequence")
      for seq_item in ds.RequestedProcedureCodeSequence:
        logging.info(f"Anonymizing Requested Procedure Code Sequence item: {seq_item}")
        if 'CodeMeaning' in seq_item:
          # Anonymize code meaning in Requested Procedure Code Sequence
          logging.info(f"Anonymizing Requested Procedure Code Sequence item code meaning: {seq_item.CodeMeaning}")
          seq_item.CodeMeaning = ""
          logging.info(f"Requested Procedure Code Sequence item code meaning: {seq_item.CodeMeaning}")
        else:
          logging.info("No 'CodeMeaning' attribute found in Requested Procedure Code Sequence item.")
    else:
      logging.info("Attribute 'RequestedProcedureCodeSequence' not found in DICOM file.")

    # Iterate over Request Attributes Sequence
    logging.info(f"Anonymizing Request Attributes Sequence")
    if hasattr(ds, 'RequestAttributesSequence'):
      for seq_item in ds.RequestAttributesSequence:
        logging.info(f"Anonymizing Request Attributes Sequence item: {seq_item}")
        if hasattr(seq_item, 'ScheduledProcedureStepDescription'):
          # Anonymize Scheduled Procedure Step Description in Request Attributes Sequence
          logging.info(f"Anonymizing Request Attributes Sequence item Scheduled Procedure Step Description: {seq_item.ScheduledProcedureStepDescription}")
          seq_item.ScheduledProcedureStepDescription = ""
          logging.info(f"Request Attributes Sequence item Scheduled Procedure Step Description: {seq_item.ScheduledProcedureStepDescription}")
        else:
          logging.info("Attribute 'ScheduledProcedureStepDescription' not found in Request Attributes Sequence item.")
    else:
      logging.info("Attribute 'RequestAttributesSequence' not found in DICOM file.")

    # Anonymize Concept Name Code Sequence
    logging.info(f"Anonymizing Concept Name Code Sequence")
    if hasattr(ds, 'ConceptNameCodeSequence'):
      logging.info(f"Anonymizing Concept Name Code Sequence item: {ds.ConceptNameCodeSequence[0]}")
      ds.ConceptNameCodeSequence[0].CodeMeaning = ""
      logging.info(f"Concept Name Code Sequence item: {ds.ConceptNameCodeSequence[0].CodeMeaning}")
    else:
      logging.info("Attribute 'ConceptNameCodeSequence' not found in DICOM file.")

    # Anonymize Performing Physician Name
    if hasattr(ds, 'PerformingPhysicianName'):
      logging.info(f"Anonymizing Performing Physician Name: {ds.PerformingPhysicianName}")
      ds.PerformingPhysicianName = ""
      logging.info(f"Performing Physician Name: {ds.PerformingPhysicianName}")
    else:
      logging.info("Attribute 'PerformingPhysicianName' not found in DICOM file.")

    # Anonymize Procedure Code Sequence
    logging.info(f"Anonymizing Procedure Code Sequence")
    if 'ProcedureCodeSequence' in ds:
      for seq_item in ds.ProcedureCodeSequence:
        logging.info(f"Anonymizing Procedure Code Sequence item: {seq_item}")
        seq_item.CodeMeaning = ""
        logging.info(f"Procedure Code Sequence item: {seq_item.CodeMeaning}")
    else:
      logging.info("Attribute 'ProcedureCodeSequence' not found in DICOM file.")

    # Anonymize Code Meaning if it exists
    if hasattr(ds, 'CodeMeaning'):
      logging.info(f"Anonymizing Code Meaning: {ds.CodeMeaning}")
      ds.CodeMeaning = ""
      logging.info(f"CodeMeaning: {ds.CodeMeaning}")
    else:
      logging.info("CodeMeaning attribute not found.")

    # Save anonymized DICOM file
    logging.info(f"Saving anonymized DICOM file to {output_path}")
    post = output_path
    logging.info(f"Saving anonymized DICOM file to {post}")
    ds.save_as(output_path)
    logging.info(f"Anonymized DICOM file saved to {output_path}")

    # Save metadata after anonymization
    logging.info(f"Saving metadata after anonymization to {post_folder}")
    save_meta_post(post_folder, post)
    logging.info(f"Metadata after anonymization saved to {post_folder}")

    # Determine filename suffix based on modality
    logging.info(f"Determining filename suffix based on modality")
    filename_suffix = f"_{anon_params['date']}_{anon_params['instance'].zfill(4)}.dcm"
    logging.info(f"Filename suffix: {filename_suffix}")

    # Construct filename prefix
    logging.info(f"Constructing filename prefix")
    if anon_params['modality'] == "MG":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['laterality']}"
      logging.info(f"Filename prefix: {filename_prefix}")
    elif anon_params['modality'] == "US":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}"
      logging.info(f"Filename prefix: {filename_prefix}")
    elif anon_params['modality'] == "MR":
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['series']}"
      logging.info(f"Filename prefix: {filename_prefix}")
    else:
      filename_prefix = f"{anon_params['anon_patient_id']}_{anon_params['modality']}_{anon_params['view']}_{anon_params['date']}"
      logging.info(f"Filename prefix: {filename_prefix}")

    # Rename anonymized file according to the specified format
    logging.info(f"Renaming anonymized file to {filename_prefix}{filename_suffix}")
    os.rename(output_path, os.path.join(os.path.dirname(output_path), f"{filename_prefix}{filename_suffix}"))
    logging.info(f"Anonymized file saved as {filename_prefix}{filename_suffix}")
  
  # Handle exceptions
  except pydicom.errors.InvalidDicomError:
    logging.warning(f"Ignoring DICOM file with invalid value: {input_path}")
  except Exception as e:
    logging.error(f"Anonymization failed for {input_path}: {e}")

# End of file