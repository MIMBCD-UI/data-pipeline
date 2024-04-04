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
          logging.info(f"Processing DICOM file: {input_path}")
          dicom_info = extract_dicom_info(input_path)
          logging.info(f"Extracted DICOM information: {dicom_info}")
          if dicom_info:
            # Extract relevant information
            patient_id = dicom_info.get("PatientID", "NOPATIENTID")
            logging.info(f"Extracted patient ID: {patient_id}")
            # Extract study date
            date = dicom_info.get("StudyDate", "NOSTUDYDATE").replace("-", "")
            logging.info(f"Extracted study date: {date}")

            # Check if the patient ID has already been anonymized
            if patient_id not in anonymized_ids:
              # Generate a new anonymized ID
              logging.info(f"Generating new anonymized ID for patient ID: {patient_id}")
              anon_patient_id = encrypt_patient_id(patient_id)
              logging.info(f"Generated new anonymized ID: {anon_patient_id}")
              # Add anonymized ID to the dictionary with its associated date
              logging.info(f"Adding anonymized ID to dictionary: {patient_id} -> {anon_patient_id}")
              anonymized_ids[patient_id] = (anon_patient_id, date)
              logging.info(f"Anonymized IDs: {anonymized_ids}")

              # Write mapping to file
              with open(mapping_file, "a", newline='') as f:
                logging.info(f"Writing mapping to file: {mapping_file}")
                writer = csv.writer(f)
                logging.info(f"Successfully created writer: {writer}")
                if not first_row_written:
                  logging.info(f"Writing header row to file: {mapping_file}")
                  writer.writerow(["real_patient_id_date", "real_patient_id", "anonymized_patient_id"])
                  logging.info(f"Successfully wrote header row to file: {mapping_file}")
                  first_row_written = True
                writer.writerow([f"{date}", patient_id, anon_patient_id])
                logging.info(f"Successfully wrote mapping to file: {date}, {patient_id}, {anon_patient_id}")

            # Anonymize DICOM file
            logging.info(f"Anonymizing DICOM file: {input_path}")

            # Extract modality, laterality, view, sequence, and instance
            logging.info(f"Extracted DICOM information: {dicom_info}")
            modality = dicom_info.get("Modality", "NOMODALITY")
            logging.info(f"Extracted modality: {modality}")
            laterality = dicom_info.get("ImageLaterality")
            logging.info(f"Extracted laterality: {laterality}")
            view = dicom_info.get("ViewPosition", "NOVIEWPOSITION")
            logging.info(f"Extracted view: {view}")
            sequence = dicom_info.get("ScanningSequence", "NOSCANNINGSEQUENCE")
            logging.info(f"Extracted sequence: {sequence}")
            series = dicom_info.get("SeriesDescription", "NOSERIESDESCRIPTION")
            logging.info(f"Extracted series: {series}")
            instance_number = dicom_info.get("InstanceNumber", "NOINSTANCENUMBER")
            logging.info(f"Extracted instance number: {instance_number}")
            instance_counter += 1

            # Convert instance_counter to 8-digit string
            logging.info(f"Converting instance counter to 8-digit string: {instance_counter}")
            instance = f"{instance_number}_{instance_counter:08}"
            logging.info(f"Converted instance counter: {instance}")

            # Determine breast side abbreviation (L for left, R for right)
            logging.info(f"Determining breast side abbreviation: {laterality}")
            breast_laterality = laterality.upper() if laterality else ""
            logging.info(f"Determined breast side abbreviation: {breast_laterality}")
            logging.info(f"Constructing filename prefix: {anon_patient_id}, {modality}, {view}, {breast_laterality}")

            # Construct filename prefix
            if modality == "MG":
              logging.info(f"Constructing MG filename prefix: {anon_patient_id}, {modality}, {view}, {breast_laterality}")
              filename_prefix = f"{anon_patient_id}_{modality}_{view}_{breast_laterality}"
              logging.info(f"Constructed MG filename prefix: {filename_prefix}")
            elif modality == "US":
              logging.info(f"Constructing US filename prefix: {anon_patient_id}, {modality}, {view}")
              filename_prefix = f"{anon_patient_id}_{modality}_{view}_{breast_laterality}" if laterality else f"{anon_patient_id}_{modality}_{view}"
              logging.info(f"Constructed US filename prefix: {filename_prefix}")
            elif modality.startswith("MR"):
              logging.info(f"Constructing MR filename prefix: {anon_patient_id}, {modality}, {series}")
              filename_prefix = f"{anon_patient_id}_{modality}_{series}"
              logging.info(f"Constructed MR filename prefix: {filename_prefix}")
            else:
              logging.info(f"Constructing default filename prefix: {anon_patient_id}, {modality}, {view}, {date}")
              filename_prefix = f"{anon_patient_id}_{modality}"
              logging.info(f"Constructed default filename prefix: {filename_prefix}")

            # Construct output path
            logging.info(f"Constructing output path: {output_folder}, {filename_prefix}, {date}, {instance}")
            output_path = os.path.join(output_folder, f"{filename_prefix}_{date}_{instance}.dcm")
            logging.info(f"Constructed output path: {output_path}")

            # Anonymize DICOM file
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
            logging.info(f"Constructed anonymization parameters dictionary: {anon_params}")

            # Create output folder if it doesn't exist
            # if not os.path.exists(output_folder):
            #   os.makedirs(output_folder)
            #   logging.info(f"Created output folder: {output_folder}")

            # Anonymize DICOM file
            logging.info(f"Anonymizing DICOM file: {input_path} -> {output_path}")
            anonymize_dicom_file(input_path, output_path, anon_params)
            logging.info(f"Anonymized DICOM file: {input_path} -> {output_path}")

        except pydicom.errors.InvalidDicomError:
          logging.warning(f"Ignoring DICOM file with invalid value: {input_path}")
          continue

# End of file