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
__version__ = "0.7.0"  # Version increment to reflect improvements
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import logging
import csv
import pydicom
from processing.extractor import extract_dicom_info
from processing.anonymizer import is_dicom_file, anonymize_dicom_file
from processing.encryption import encrypt_patient_id

# Batch size for batch processing
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))  # Default batch size is 100 files, can be set via env variables

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_directory(source_folder, output_folder, mapping_file, batch_size=BATCH_SIZE):
  """
  Process a directory containing DICOM files in batches to anonymize them and prepare the dataset.

  Args:
    source_folder (str): Path to the source directory containing DICOM files.
    output_folder (str): Path to the output directory to save anonymized DICOM files.
    mapping_file (str): Path to the file to write the mapping of original and anonymized IDs.
    batch_size (int): Number of files to process in each batch.
  """
  anonymized_ids = {}  # Dictionary to store original-to-anonymized ID mapping with dates
  ignored_files = ['DICOMDIR', 'LOCKFILE', 'VERSION', '.DS_Store']  # List of files to ignore
  instance_counter = 0
  first_row_written = False  # Flag to indicate if the first row has been written
  file_batch = []  # Initialize batch container

  # Create output folder if it doesn't exist
  os.makedirs(output_folder, exist_ok=True)

  def process_batch(batch):
    """Process a batch of DICOM files."""
    nonlocal instance_counter, first_row_written

    for input_path in batch:
      if is_dicom_file(input_path):
        try:
          logging.info(f"Processing DICOM file: {input_path}")
          dicom_info = extract_dicom_info(input_path)
          if dicom_info:
            patient_id = dicom_info.get("PatientID", "NOPATIENTID")
            date = dicom_info.get("StudyDate", "NOSTUDYDATE").replace("-", "")

            if patient_id not in anonymized_ids:
              anon_patient_id = encrypt_patient_id(patient_id)
              anonymized_ids[patient_id] = (anon_patient_id, date)

              with open(mapping_file, "a", newline='') as f:
                writer = csv.writer(f)
                if not first_row_written:
                  writer.writerow(["real_patient_id_date", "real_patient_id", "anonymized_patient_id"])
                  first_row_written = True
                writer.writerow([f"{date}", patient_id, anon_patient_id])

            modality = dicom_info.get("Modality", "NOMODALITY")
            laterality = dicom_info.get("ImageLaterality", "")
            view = dicom_info.get("ViewPosition", "NOVIEWPOSITION")
            sequence = dicom_info.get("ScanningSequence", "NOSCANNINGSEQUENCE")
            series = dicom_info.get("SeriesDescription", "NOSERIESDESCRIPTION")
            instance_number = dicom_info.get("InstanceNumber", "NOINSTANCENUMBER")
            instance_counter += 1
            instance = f"{instance_number}_{instance_counter:08}"

            breast_laterality = laterality.upper() if laterality else ""
            filename_prefix = construct_filename_prefix(anon_patient_id, modality, view, breast_laterality, series)
            output_path = os.path.join(output_folder, f"{filename_prefix}_{date}_{instance}.dcm")

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

            anonymize_dicom_file(input_path, output_path, anon_params)
            logging.info(f"Anonymized DICOM file: {input_path} -> {output_path}")

        except pydicom.errors.InvalidDicomError:
          logging.warning(f"Ignoring DICOM file with invalid value: {input_path}")
          continue

  # Iterate through DICOM files in the source folder
  for root, _, files in os.walk(source_folder):
    for file in files:
      if file in ignored_files:
        continue

      input_path = os.path.join(root, file)
      file_batch.append(input_path)

      # Process the batch when it reaches the batch size
      if len(file_batch) >= batch_size:
        logging.info(f"Processing batch of {batch_size} files...")
        process_batch(file_batch)
        file_batch = []  # Reset batch container after processing

  # Process remaining files in the final batch
  if file_batch:
    logging.info(f"Processing final batch of {len(file_batch)} files...")
    process_batch(file_batch)

def construct_filename_prefix(anon_patient_id, modality, view, laterality, series):
  """
  Construct a filename prefix based on the given DICOM metadata.

  Args:
    anon_patient_id (str): Anonymized patient ID.
    modality (str): Imaging modality (e.g., MG, US, MR).
    view (str): View position (e.g., CC, MLO).
    laterality (str): Image laterality (e.g., L, R).
    series (str): Series description.

  Returns:
    str: Constructed filename prefix.
  """
  if modality == "MG":
    return f"{anon_patient_id}_{modality}_{view}_{laterality}"
  elif modality == "US":
    return f"{anon_patient_id}_{modality}_{view}_{laterality}" if laterality else f"{anon_patient_id}_{modality}_{view}"
  elif modality.startswith("MR"):
    return f"{anon_patient_id}_{modality}_{series}"
  else:
    return f"{anon_patient_id}_{modality}"

# End of file