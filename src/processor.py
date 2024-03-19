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

import os
from extract import extract_dicom_info
from anonymizer import is_dicom_file, anonymize_dicom_file
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_directory(source_folder, output_folder):
    """
    Process a directory containing DICOM files to anonymize them and prepare the dataset.

    Args:
        source_folder (str): Path to the source directory containing DICOM files.
        output_folder (str): Path to the output directory to save anonymized DICOM files.
    """
    mapping_file = "/Users/francisco/Git/dicom-images-breast/data/mapping.csv"
    with open(mapping_file, "w") as f:
        f.write("Original_ID,Anonymized_ID\n")

    for root, dirs, files in os.walk(source_folder):
        # Ensure output directory structure is maintained
        relative_root = os.path.relpath(root, source_folder)
        output_root = os.path.join(output_folder, relative_root)
        os.makedirs(output_root, exist_ok=True)
        
        for i, file in enumerate(files):
            input_path = os.path.join(root, file)
            # Check if the file is a DICOM file
            if not is_dicom_file(input_path):
                logging.info(f"Skipping non-DICOM file: {input_path}")
                continue
            # Extract DICOM information
            dicom_info = extract_dicom_info(input_path)
            if dicom_info:
                anon_patient_id = f"Patient{i+1}"
                modality = dicom_info["Modality"]
                date = dicom_info["StudyDate"].replace("-", "")
                sequence = dicom_info["Sequence"]
                instance = f"{i+1:03}"
                # Construct output path
                relative_path = os.path.relpath(input_path, source_folder)
                output_path = os.path.join(output_folder, relative_path.replace(".dcm", "_anonymized.dcm"))
                # Anonymize DICOM files
                anonymize_dicom_file(input_path, output_path, anon_patient_id, modality, date, sequence, instance)
                # Write mapping to file
                original_id = os.path.basename(input_path)
                anonymized_id = os.path.basename(output_path)
                with open(mapping_file, "a") as f:
                    f.write(f"{original_id},{anonymized_id}\n")