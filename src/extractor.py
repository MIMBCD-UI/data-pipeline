#!/usr/bin/env python

"""
extractor.py: Module to extract relevant information from DICOM files.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.6.0"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import pydicom
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_dicom_info(dicom_file):
  """
  Extract relevant information from a DICOM file.

  Args:
    dicom_file (str): Path to the DICOM file.

  Returns:
    dict: Dictionary containing extracted information (Modality, Side, View, StudyDate, Sequence).
  """
  try:
    # Extract DICOM information
    logging.info(f"Extracting DICOM info from {dicom_file}")
    ds = pydicom.dcmread(dicom_file)
    logging.info(f"DICOM info extracted: {ds}")
    # Extract relevant information
    logging.info("Extracting relevant information")
    modality = ds.Modality if hasattr(ds, "Modality") else "NOMODALITY"
    logging.info(f"Modality: {modality}")
    # Extract patient ID if available, otherwise use a placeholder
    logging.info("Extracting patient ID")
    patientid = ds.PatientID if hasattr(ds, "PatientID") else "NOPATIENTID"
    logging.info(f"Patient ID: {patientid}")
    # Extract other relevant information
    logging.info("Extracting other relevant information")
    info = {
      "PatientID": patientid,
      "Modality": modality,
      "ImageLaterality": ds.ImageLaterality if modality != "MR" and hasattr(ds, "ImageLaterality") else "NOIMAGELATERALITY",
      "ViewPosition": ds.ViewPosition if hasattr(ds, "ViewPosition") else "NOVIEWPOSITION",
      "StudyDate": ds.StudyDate if hasattr(ds, "StudyDate") else "NOSTUDYDATE",
      "ScanningSequence": ds.ScanningSequence if hasattr(ds, "ScanningSequence") else "NOSCANNINGSEQUENCE",
      "SeriesDescription": ds.SeriesDescription if hasattr(ds, "SeriesDescription") else "NOSERIESDESCRIPTION",
      "InstanceNumber": ds.InstanceNumber if hasattr(ds, "InstanceNumber") else "NOINSTANCENUMBER"
    }
    logging.info(f"Extracted information: {info}")
    return info
  except Exception as e:
    # Log an error if the extraction fails
    logging.error(f"Failed to extract DICOM info from {dicom_file}: {e}")
    return None

# End of file