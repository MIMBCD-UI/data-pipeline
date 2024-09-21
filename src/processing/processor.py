#!/usr/bin/env python

"""
processor.py: Optimized for handling large datasets with batch processing and improved memory management.

This script processes DICOM files by anonymizing and preparing the dataset,
ensuring efficient handling of large files using batch processing.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.7.2"  # Version increment to reflect improvements
__status__ = "Development"
__credits__ = ["Carlos Santiago", "Catarina Barata", "Jacinto C. Nascimento", "Diogo Araújo"]

import os
import logging
import sys
import csv
import pydicom

# Set a default batch size for batch processing, but allow overriding via environment variable
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))

# Configure logging to track each step in the process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Append the src directory to sys.path to ensure correct module import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'src'))
sys.path.insert(0, src_dir)

# Import necessary processing functions from the src module
from processing.extractor import extract_dicom_info
from processing.anonymizer import is_dicom_file, anonymize_dicom_file
from processing.encryption import encrypt_patient_id

def process_directory(source_folder, output_folder, mapping_file, batch_size=BATCH_SIZE):
  """
  Process a directory of DICOM files in batches, anonymizing and preparing them for analysis.
  
  Args:
    source_folder (str): Path to the directory containing DICOM files.
    output_folder (str): Path to the directory to save anonymized DICOM files.
    mapping_file (str): CSV file to store the mapping of original and anonymized IDs.
    batch_size (int): Number of files to process in each batch (default is 100).
  """
  # Dictionary to store the mapping between original and anonymized patient IDs
  anonymized_ids = {}
  # Ignored files during processing, such as system or DICOM-specific files
  ignored_files = ['DICOMDIR', 'LOCKFILE', 'VERSION', '.DS_Store']
  instance_counter = 0  # Counter for instance numbers in filenames
  first_row_written = False  # Track if the CSV header row has been written
  file_batch = []  # Container to hold files in the current batch

  # Ensure the output directory exists
  os.makedirs(output_folder, exist_ok=True)
  logging.info(f"Output directory ensured at: {output_folder}")

  def process_batch(batch):
    """Process a batch of DICOM files, anonymizing them and updating the mapping."""
    nonlocal instance_counter, first_row_written

    for input_path in batch:
      if is_dicom_file(input_path):  # Check if the file is a valid DICOM file
        try:
          logging.info(f"Processing DICOM file: {input_path}")
          
          # Extract metadata from the DICOM file
          dicom_info = extract_dicom_info(input_path)  

          if dicom_info:  # Ensure the DICOM info was successfully extracted
            # Extract the PatientID and StudyDate with defaults
            patient_id = dicom_info.get("PatientID", "NOPATIENTID")
            date = dicom_info.get("StudyDate", "NOSTUDYDATE").replace("-", "")  

            # If the patient ID has not been anonymized, create a new anonymized ID
            if patient_id not in anonymized_ids:
              anon_patient_id = encrypt_patient_id(patient_id)
              anonymized_ids[patient_id] = (anon_patient_id, date)

              # Append new anonymization mapping to the CSV file
              with open(mapping_file, "a", newline='') as f:
                writer = csv.writer(f)
                if not first_row_written:
                  writer.writerow(["real_patient_id_date", "real_patient_id", "anonymized_patient_id"])
                  first_row_written = True
                writer.writerow([f"{date}", patient_id, anon_patient_id])

            # If the patient ID has already been anonymized, retrieve the existing anon_patient_id
            else:
              anon_patient_id = anonymized_ids[patient_id][0]

            # Extract other relevant fields from the DICOM metadata
            modality = dicom_info.get("Modality", "NOMODALITY")
            laterality = dicom_info.get("ImageLaterality", "")
            view = dicom_info.get("ViewPosition", "NOVIEWPOSITION")
            sequence = dicom_info.get("ScanningSequence", "NOSCANNINGSEQUENCE")
            series = dicom_info.get("SeriesDescription", "NOSERIESDESCRIPTION")
            instance_number = dicom_info.get("InstanceNumber", "NOINSTANCENUMBER")

            # Update instance counter for filename uniqueness
            instance_counter += 1
            instance = f"{instance_number}_{instance_counter:08}"

            # Construct the output filename based on the anonymized metadata
            breast_laterality = laterality.upper() if laterality else ""
            filename_prefix = construct_filename_prefix(anon_patient_id, modality, view, breast_laterality, series)
            output_path = os.path.join(output_folder, f"{filename_prefix}_{date}_{instance}.dcm")

            # Anonymization parameters passed to the anonymization function
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

            # Anonymize the DICOM file and save it to the output directory
            anonymize_dicom_file(input_path, output_path, anon_params)
            logging.info(f"Anonymized DICOM file: {input_path} -> {output_path}")

        except pydicom.errors.InvalidDicomError as e:
          logging.warning(f"Invalid DICOM file: '{input_path}'. Skipping. Error: {e}")
        except Exception as e:
          logging.error(f"Error processing file '{input_path}': {e}")

  # Walk through the source directory, collecting files into batches
  for root, _, files in os.walk(source_folder):
    for file in files:
      if file in ignored_files:
        logging.debug(f"Ignoring file: {file}")
        continue

      input_path = os.path.join(root, file)
      file_batch.append(input_path)

      # Once the batch size is met, process the batch
      if len(file_batch) >= batch_size:
        logging.info(f"Processing batch of {batch_size} files...")
        process_batch(file_batch)
        file_batch = []  # Reset the batch after processing

  # Process any remaining files in the final batch
  if file_batch:
    logging.info(f"Processing final batch of {len(file_batch)} files...")
    process_batch(file_batch)

def construct_filename_prefix(anon_patient_id, modality, view, laterality, series):
  """
  Construct a filename prefix using anonymized patient ID and DICOM metadata.

  Args:
    anon_patient_id (str): Anonymized patient ID.
    modality (str): Imaging modality (e.g., MG, US, MR).
    view (str): Image view position (e.g., CC, MLO).
    laterality (str): Image laterality (e.g., L, R).
    series (str): Series description from the DICOM file.

  Returns:
    str: The constructed filename prefix.
  """
  # Create a consistent naming convention based on modality and metadata
  if modality == "MG":
    return f"{anon_patient_id}_{modality}_{view}_{laterality}"
  elif modality == "US":
    return f"{anon_patient_id}_{modality}_{view}_{laterality}" if laterality else f"{anon_patient_id}_{modality}_{view}"
  elif modality.startswith("MR"):
    return f"{anon_patient_id}_{modality}_{series}"
  else:
    return f"{anon_patient_id}_{modality}"

# End of file