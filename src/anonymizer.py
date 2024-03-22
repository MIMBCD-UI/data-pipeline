import pydicom
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    
    # Save anonymized DICOM file
    ds.save_as(output_path)
    
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
