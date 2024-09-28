#!/usr/bin/env python

"""
extractor.py: Module to extract relevant information from DICOM files.
This module reads DICOM files and extracts essential metadata, 
including patient information, modality, and image details.
The extracted information is used for data processing and analysis.

Key Functions:
- extract_dicom_info: Extract relevant information from a DICOM file.
- extract_patient_id: Extract the patient ID from DICOM metadata.
- extract_modality: Extract the modality (e.g., CT, MR) from DICOM metadata.
- extract_image_laterality: Extract the image laterality from DICOM metadata.
- extract_view_position: Extract the image view position from DICOM metadata.
- extract_study_date: Extract the study date from DICOM metadata.
- extract_scanning_sequence: Extract the scanning sequence from DICOM metadata.
- extract_series_description: Extract the series description from DICOM metadata.
- extract_instance_number: Extract the instance number from DICOM metadata.

Expected Usage:
- Extract relevant information from a DICOM file using `extract_dicom_info`.
- Access specific attributes using individual extraction functions.
- Process the extracted information for analysis or visualization.

Customization & Flexibility:
- The extraction functions can be extended to include additional attributes.
- The extracted information can be formatted or transformed based on requirements.
- The module can be integrated into existing data processing pipelines.

Performance & Compatibility:
- The module is optimized for processing DICOM files efficiently.
- It uses the pydicom library for reading DICOM files.
- The module is compatible with Python 3.6+ and can be used in various environments and platforms.

Best Practices & Maintenance:
- The script follows best practices for error handling, logging, and code readability.
- It is well-documented and can be easily maintained or extended by other developers.
- The script is designed to be robust and reliable for long-term use in data curation workflows.

Notes:
- This module is part of a larger data curation pipeline for multimodal breast imaging data.
- It is optimized for processing DICOM files but can be adapted for other types of medical imaging data.
- The script is designed to be run from the command line or as part of an automated workflow.

References:
- pydicom library: https://pydicom.github.io/
- DICOM standard: https://www.dicomstandard.org/
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.6.5"  # Version incremented to reflect improvements
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import pydicom
import logging
import os

# Configure logging to provide detailed information about execution flow and potential issues.
# The log format includes timestamps, log level, and the message for better traceability.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_dicom_info(dicom_file):
  """
  Extract relevant information from a DICOM file.

  This function reads a DICOM file and extracts key attributes related to the patient, image, and study.
  If certain attributes are not available in the DICOM file, default values will be used.
  
  Args:
    dicom_file (str): Path to the DICOM file.

  Returns:
    dict: A dictionary containing extracted DICOM information with default values for missing attributes.
  """
  try:
    # Log the start of the DICOM info extraction process
    logging.info(f"Starting extraction of DICOM info from file: {dicom_file}")
    
    # Check if the provided DICOM file exists before attempting to read it
    if not os.path.exists(dicom_file):
      raise FileNotFoundError(f"File '{dicom_file}' does not exist.")
    
    # Read the DICOM file using pydicom's dcmread method
    ds = pydicom.dcmread(dicom_file)
    logging.info(f"Successfully read DICOM file: {dicom_file}")

    # Extract relevant information from the DICOM dataset using default values if attributes are missing.
    # The 'getattr' function allows specifying a default value if the attribute is not present in the DICOM file.
    info = {
      "PatientID": getattr(ds, "PatientID", "NOPATIENTID"),  # Extract PatientID, default to "NOPATIENTID" if not found
      "Modality": getattr(ds, "Modality", "NOMODALITY"),  # Extract Modality (e.g., CT, MR, etc.)
      "ImageLaterality": getattr(ds, "ImageLaterality", "NOIMAGELATERALITY") if ds.Modality != "MR" else "NOIMAGELATERALITY",  # Image laterality for non-MR modalities
      "ViewPosition": getattr(ds, "ViewPosition", "NOVIEWPOSITION"),  # Position of the image view (e.g., CC, MLO)
      "StudyDate": getattr(ds, "StudyDate", "NOSTUDYDATE"),  # Study date of the image
      "ScanningSequence": getattr(ds, "ScanningSequence", "NOSCANNINGSEQUENCE"),  # Scanning sequence, relevant for MR images
      "SeriesDescription": getattr(ds, "SeriesDescription", "NOSERIESDESCRIPTION"),  # Series description, usually indicates the type of scan
      "InstanceNumber": getattr(ds, "InstanceNumber", "NOINSTANCENUMBER")  # Instance number within the series
    }

    # Log the successfully extracted information for traceability
    logging.info(f"Extracted DICOM information: {info}")
    return info

  except FileNotFoundError as fnf_error:
    # Log an error if the file is not found
    logging.error(f"File not found: {fnf_error}. Please check the file path.")
  except pydicom.errors.InvalidDicomError:
    # Handle invalid DICOM file errors and log the issue
    logging.error(f"Invalid DICOM file format: {dicom_file}. Unable to process.")
  except Exception as e:
    # Catch any other unexpected exceptions that may occur during the extraction process
    logging.error(f"An unexpected error occurred while extracting DICOM info from {dicom_file}: {e}")
    
  # Return None if any errors occur during the process
  return None

# End of file