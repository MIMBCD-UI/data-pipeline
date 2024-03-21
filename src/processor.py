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
__credits__ = ["Carlos Santiago", "Jacinto C. Nascimento"]

import os
import logging
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
  # Create or truncate the mapping file
  with open(mapping_file, "w") as f:
    f.write("Original_ID,Anonymized_ID\n")

  # Initialize variables to track the current sequence and instance
  current_sequence = None
  instance_counter = 0

  # Iterate through DICOM files in the source folder
  for root, _, files in os.walk(source_folder):
    for file in files:
      input_path = os.path.join(root, file)
      # Check if the file is a DICOM file
      if is_dicom_file(input_path):
        # Extract DICOM information
        dicom_info = extract_dicom_info(input_path)
        if dicom_info:
          # Generate the patient ID
          patient_id = dicom_info.get("PatientID", "NOPATIENTID")
          # Encrypt the patient ID using the imported function
          anon_patient_id = encrypt_patient_id(patient_id)
          modality = dicom_info.get("Modality", "NOMODALITY")
          laterality = dicom_info.get("ImageLaterality")
          view = dicom_info.get("ViewPosition", "NOVIEWPOSITION")
          date = dicom_info.get("StudyDate", "NOSTUDYDATE").replace("-", "")
          sequence = dicom_info.get("ScanningSequence", "NOSCANNINGSEQUENCE")
          instance_counter += 1

          # Check if a new sequence has started
          if sequence != current_sequence:
            # Reset instance counter for the new sequence
            current_sequence = sequence
            instance_counter = 1

          instance = f"{instance_counter:03}"

          # Determine breast side abbreviation (L for left, R for right)
          breast_laterality = laterality.upper() if laterality else ""

          # Construct filename prefix
          if modality == "MG":
            filename_prefix = f"{anon_patient_id}_{modality}_{breast_laterality}_{view}"
          elif modality == "US":
            filename_prefix = f"{anon_patient_id}_{modality}_{breast_laterality}_{view}" if laterality else f"{anon_patient_id}_{modality}_{view}"
          elif modality.startswith("MR"):
            filename_prefix = f"{anon_patient_id}_{modality}"
            print(filename_prefix)
          else:
            filename_prefix = f"{anon_patient_id}_{modality}"

          # Construct output path
          output_path = os.path.join(output_folder, f"{filename_prefix}_{date}_{instance}.dcm")

          # Anonymize DICOM file
          anonymize_dicom_file(input_path, output_path, anon_patient_id, modality, view, laterality, date, sequence, instance)

          # Write mapping to file
          original_id = os.path.basename(input_path)
          anonymized_id = os.path.basename(output_path)
          with open(mapping_file, "a") as f:
            f.write(f"{original_id},{anonymized_id}\n")
