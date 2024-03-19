
#!/usr/bin/env python

"""
.py: TODO
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

def extract_dicom_info(dicom_file):
    """
    Extract relevant information from a DICOM file.

    Args:
        dicom_file (str): Path to the DICOM file.

    Returns:
        dict: Dictionary containing extracted information (PatientID, StudyDate, Modality, Sequence).
    """
    try:
        ds = pydicom.dcmread(dicom_file)
        info = {
            "PatientID": ds.PatientID,
            "StudyDate": ds.StudyDate,
            "Modality": ds.Modality,
            "Sequence": ds.SequenceName if hasattr(ds, "SequenceName") else "Unknown"
        }
        return info
    except Exception as e:
        logging.error(f"Failed to extract DICOM info from {dicom_file}: {e}")
        return None
