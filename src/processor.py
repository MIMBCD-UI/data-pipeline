#!/usr/bin/env python

"""
processor.py: TODO
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
import logging
from extractor import extract_dicom_info
from anonymizer import is_dicom_file, anonymize_dicom_file
import random

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
        for file in files:
            input_path = os.path.join(root, file)
            # Check if the file is a DICOM file
            if is_dicom_file(input_path):
                # Extract DICOM information
                dicom_info = extract_dicom_info(input_path)
                if dicom_info:
                    # Generate a random integer as the anonymized patient ID
                    anon_patient_id = f"{random.randint(100000, 999999)}"
                    modality = dicom_info["Modality"]
                    side = dicom_info["Side"]
                    view = dicom_info["View"]
                    date = dicom_info["StudyDate"].replace("-", "")
                    sequence = dicom_info["Sequence"]
                    instance = f"{len(files):03}"
                    
                    # Construct filename prefix
                    if modality == "MG":
                        filename_prefix = f"{anon_patient_id}_MG"
                    elif modality == "US":
                        if side == "Unknown":
                            filename_prefix = f"{anon_patient_id}_US_NA"
                        else:
                            filename_prefix = f"{anon_patient_id}_US_{side}"
                    elif modality.startswith("MRI"):
                        filename_prefix = f"{anon_patient_id}_{modality}"
                    else:
                        filename_prefix = f"{anon_patient_id}_{modality}"
                    
                    # Construct output path
                    output_path = os.path.join(output_folder, f"{filename_prefix}_{view}_{date}_{sequence}_{instance}.dcm")
                    
                    # Anonymize DICOM file
                    anonymize_dicom_file(input_path, output_path, anon_patient_id, modality, side, view, date, sequence, instance)
                    
                    # Write mapping to file
                    original_id = os.path.basename(input_path)
                    anonymized_id = os.path.basename(output_path)
                    with open(mapping_file, "a") as f:
                        f.write(f"{original_id},{anonymized_id}\n")