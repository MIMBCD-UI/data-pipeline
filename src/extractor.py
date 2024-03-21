#!/usr/bin/env python

"""
extractor.py: Module to extract relevant information from DICOM files.
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
    ds = pydicom.dcmread(dicom_file)
    modality = ds.Modality if hasattr(ds, "Modality") else "NOMODALITY"
    info = {
      "Modality": modality,
      "ImageLaterality": ds.ImageLaterality if modality != "MRI" and hasattr(ds, "ImageLaterality") else None,
      "ViewPosition": ds.ViewPosition if hasattr(ds, "ViewPosition") else "NOVIEWPOSITION",
      "StudyDate": ds.StudyDate if hasattr(ds, "StudyDate") else "NOSTUDYDATE",
      "ScanningSequence": ds.ScanningSequence if hasattr(ds, "ScanningSequence") else "NOSCANNINGSEQUENCE"
    }
    return info
  except Exception as e:
    logging.error(f"Failed to extract DICOM info from {dicom_file}: {e}")
    return None
