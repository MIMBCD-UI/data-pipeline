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
import random

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

  # Iterate through DICOM files in the source folder
  for root, _, files in os.walk(source_folder):
    for file in files:
      input_path = os.path.join(root, file)
      # Check if the file is a DICOM file
      if is_dicom_file(input_path):
        # Extract DICOM information
        dicom_info = extract_dicom_info(input_path)
        if dicom_info:
          # Generate a random integer as the anonymized patient ID
          anon_patient_id = f"{random.randint(100000, 999999)}"
          modality = dicom_info.get("Modality", "NOMODALITY")
          laterality = dicom_info.get("ImageLaterality", "NOIMAGELATERALITY")
          view = dicom_info.get("ViewPosition", "NOVIEWPOSITION")
          date = dicom_info.get("StudyDate", "NOSTUDYDATE").replace("-", "")
          sequence = dicom_info.get("ScanningSequence", "NOSCANNINGSEQUENCE")
          instance = f"{len(files):03}"

          print(view)
          
          # Determine breast side abbreviation (L for left, R for right)
          breast_laterality = laterality.upper()
          
          # Construct filename prefix
          if modality == "MG":
            filename_prefix = f"{anon_patient_id}_{modality}_{view}_{breast_laterality}"
          elif modality == "US":
            filename_prefix = f"{anon_patient_id}_{modality}_{view}_{breast_laterality}" if laterality != "NOIMAGELATERALITY" else f"{anon_patient_id}_{modality}_{view}"
          elif modality.startswith("MRI"):
            filename_prefix = f"{anon_patient_id}_{modality}_{breast_laterality}"
          else:
            filename_prefix = f"{anon_patient_id}_{modality}_{breast_laterality}"
          
          # Construct output path
          output_path = os.path.join(output_folder, f"{filename_prefix}_{date}_{sequence}_{instance}.dcm")
          
          # Anonymize DICOM file
          anonymize_dicom_file(input_path, output_path, anon_patient_id, modality, view, laterality, date, sequence, instance)
          
          # Write mapping to file
          original_id = os.path.basename(input_path)
          anonymized_id = os.path.basename(output_path)
          with open(mapping_file, "a") as f:
            f.write(f"{original_id},{anonymized_id}\n")
