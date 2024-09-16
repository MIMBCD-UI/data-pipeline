#!/usr/bin/env python

"""
extractor.py: Module to extract relevant information from DICOM files.
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

import pydicom
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_dicom_info(dicom_file):
  """
  Extract relevant information from a DICOM file.

  Args:
    dicom_file (str): Path to the DICOM file.

  Returns:
    dict: Dictionary containing extracted information (Modality, PatientID, ImageLaterality, ViewPosition, StudyDate, ScanningSequence, SeriesDescription, InstanceNumber).
  """
  try:
    logging.info(f"Extracting DICOM info from {dicom_file}")
    ds = pydicom.dcmread(dicom_file)

    # Extract relevant information
    info = {
      "PatientID": getattr(ds, "PatientID", "NOPATIENTID"),
      "Modality": getattr(ds, "Modality", "NOMODALITY"),
      "ImageLaterality": getattr(ds, "ImageLaterality", "NOIMAGELATERALITY") if ds.Modality != "MR" else "NOIMAGELATERALITY",
      "ViewPosition": getattr(ds, "ViewPosition", "NOVIEWPOSITION"),
      "StudyDate": getattr(ds, "StudyDate", "NOSTUDYDATE"),
      "ScanningSequence": getattr(ds, "ScanningSequence", "NOSCANNINGSEQUENCE"),
      "SeriesDescription": getattr(ds, "SeriesDescription", "NOSERIESDESCRIPTION"),
      "InstanceNumber": getattr(ds, "InstanceNumber", "NOINSTANCENUMBER")
    }

    logging.info(f"Extracted information: {info}")
    return info

  except Exception as e:
    logging.error(f"Failed to extract DICOM info from {dicom_file}: {e}")
    return None

# End of file