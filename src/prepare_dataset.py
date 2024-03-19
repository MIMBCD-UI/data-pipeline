#!/usr/bin/env python

"""
prepare_dataset.py: Script to anonymize DICOM files and prepare dataset for ML projects.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.4.0"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago", "Jacinto C. Nascimento"]

import pydicom
from pydicom.filereader import InvalidDicomError
import csv
from datetime import datetime
from pathlib import Path
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_id_mapping(mapping_file, real_id, anon_id):
    with mapping_file.open('a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([real_id, anon_id])

def generate_anon_id(real_id):
    return f"A{real_id[-6:]}"  # Placeholder for actual anonymization logic

def is_dicom_file(file_path):
    if file_path.name.upper() == 'DICOMDIR':
        return False  # Skip DICOMDIR files
    try:
        pydicom.dcmread(str(file_path), stop_before_pixels=True)
        return True
    except InvalidDicomError:
        return False

def should_skip_file(file_name):
    # Define logic to skip files based on their names or extensions
    return file_name.upper() in ['DICOMDIR', 'VERSION', 'LOCKFILE']  # Example

def anonymize_dicom_file(file_path, output_folder, mapping_file):
    output_file_path = output_folder / f"{file_path.stem}_anonymized{file_path.suffix}"
    try:
        subprocess.run(["dicom-anonymizer", str(file_path), str(output_file_path)], check=True)
        logging.info(f"Anonymized file saved to {output_file_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Anonymization failed for {file_path}: {e}")

def process_directory(directory, output_folder, mapping_file):
    for item in directory.rglob('*'):
        if item.is_file() and not item.name.startswith('.') and not should_skip_file(item.name):
            if is_dicom_file(item):
                anonymize_dicom_file(item, output_folder, mapping_file)
            else:
                logging.info(f"Skipping non-DICOM file: {item}")

root_directory = Path(__file__).resolve().parent.parent.parent
source_folder = root_directory / "dicom-images-breast" / "tests" / "testing_data-pipeline_t001" / "known" / "raw"
output_folder = root_directory / "dataset-multimodal-breast" / "tests" / "dicom"
mapping_file = root_directory / "dicom-images-breast" / "data" / "mapping.csv"

output_folder.mkdir(parents=True, exist_ok=True)
if not mapping_file.exists():
    with mapping_file.open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["RealID", "AnonID"])

process_directory(source_folder, output_folder, mapping_file)
