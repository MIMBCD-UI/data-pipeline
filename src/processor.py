#!/usr/bin/env python

"""
processor.py: Module for processing DICOM files.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.5.0"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import logging
import csv
import pydicom
from extractor import extract_dicom_info
from anonymizer import is_dicom_file, anonymize_dicom_file
from encryption import encrypt_patient_id

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_directory(source_folder, output_folder, mapping_file):
  """
  Process a directory containing DICOM files to anonymize them and prepare the dataset.

  Args:
      source_folder (str): Path to the source directory containing DICOM files.
      output_folder (str): Path to the output directory to save anonymized DICOM files.
      mapping_file (str): Path to the file to write the mapping of original and anonymized IDs.
  """
  # Initialize variables to track the anonymized IDs and their associated dates
  anonymized_ids = {}  # Dictionary to store original-to-anonymized ID mapping with dates

  # List of directories or filenames to ignore
  ignored_directories = []
  ignored_files = ['DICOMDIR', 'LOCKFILE', 'VERSION', '.DS_Store']

  # Initialize instance counter
  instance_counter = 0

  # Flag to indicate if the first row has been written
  first_row_written = False

  # Iterate through DICOM files in the source folder
  for root, _, files in os.walk(source_folder):
    # Skip ignored directories
    if any(dir_name in root for dir_name in ignored_directories):
      continue

    for file in files:
      # Skip ignored files
      if file in ignored_files:
        continue

      input_path = os.path.join(root, file)
      # Check if the file is a DICOM file
      if is_dicom_file(input_path):
        try:
          # Extract DICOM information
          dicom_info = extract_dicom_info(input_path)
          if dicom_info:
            # Extract relevant information
            patient_id = dicom_info.get("PatientID", "NOPATIENTID")
            date = dicom_info.get("StudyDate", "NOSTUDYDATE").replace("-", "")

            # Check if the patient ID has already been anonymized
            if patient_id not in anonymized_ids:
              # Generate a new anonymized ID
              anon_patient_id = encrypt_patient_id(patient_id)
              # Add anonymized ID to the dictionary with its associated date
              anonymized_ids[patient_id] = (anon_patient_id, date)

              # Write mapping to file
              with open(mapping_file, "a", newline='') as f:
                writer = csv.writer(f)
                if not first_row_written:
                  writer.writerow(["real_patient_id_date", "real_patient_id", "anonymized_patient_id"])
                  first_row_written = True
                writer.writerow([f"{date}", patient_id, anon_patient_id])

            # Extract modality, laterality, view, sequence, and instance
            modality = dicom_info.get("Modality", "NOMODALITY")
            laterality = dicom_info.get("ImageLaterality")
            view = dicom_info.get("ViewPosition", "NOVIEWPOSITION")
            sequence = dicom_info.get("ScanningSequence", "NOSCANNINGSEQUENCE")
            series = dicom_info.get("SeriesDescription", "NOSERIESDESCRIPTION")
            instance_number = dicom_info.get("InstanceNumber", "NOINSTANCENUMBER")
            instance_counter += 1

            # Convert instance_counter to 8-digit string
            instance = f"{instance_number}_{instance_counter:08}"

            # Determine breast side abbreviation (L for left, R for right)
            breast_laterality = laterality.upper() if laterality else ""

            # Construct filename prefix
            if modality == "MG":
              filename_prefix = f"{anon_patient_id}_{modality}_{view}_{breast_laterality}"
            elif modality == "US":
              filename_prefix = f"{anon_patient_id}_{modality}_{view}_{breast_laterality}" if laterality else f"{anon_patient_id}_{modality}_{view}"
            elif modality.startswith("MR"):
              filename_prefix = f"{anon_patient_id}_{modality}_{series}"
            else:
              filename_prefix = f"{anon_patient_id}_{modality}"

            # Construct output path
            output_path = os.path.join(output_folder, f"{filename_prefix}_{date}_{instance}.dcm")
            logging.info(f"Anonymizing DICOM file: {input_path} -> {output_path}")

            # Construct anonymization parameters dictionary
            anon_params = {
              'anon_patient_id': anon_patient_id,
              'modality': modality,
              'view': view,
              'laterality': laterality,
              'date': date,
              'sequence': sequence,
              'series': series,
              'instance': instance
            }

            # Create output folder if it doesn't exist
            # if not os.path.exists(output_folder):
            #   os.makedirs(output_folder)
            #   logging.info(f"Created output folder: {output_folder}")

            # Anonymize DICOM file
            anonymize_dicom_file(input_path, output_path, anon_params)
            logging.info(f"Anonymized DICOM file: {input_path} -> {output_path}")

        except pydicom.errors.InvalidDicomError:
          logging.warning(f"Ignoring DICOM file with invalid value: {input_path}")
          continue
