#!/usr/bin/env python

"""prepare_dataset.py: TODO."""

__author__      = "Francisco Maria Calisto"
__maintainer__  = "Francisco Maria Calisto"
__email__       = "francisco.calisto@tecnico.ulisboa.pt"
__license__     = "ACADEMIC & COMMERCIAL"
__version__     = "0.0.1"
__status__      = "Development"
__copyright__   = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__     = [
  "Carlos Santiago",
  "Jacinto C. Nascimento"
]

import os
import pydicom
import csv
from datetime import datetime
from pathlib import Path

# Define functions
def update_id_mapping(mapping_file, real_id, anon_id):
  with mapping_file.open('a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([real_id, anon_id])

def extract_info(ds):
  patient_id = ds.PatientID
  modality = ds.Modality if 'Modality' in ds else 'UnknownModality'
  sequence = ds.SeriesDescription if 'SeriesDescription' in ds else 'UnknownSequence'
  return patient_id, modality, sequence

def generate_anon_id(real_id):
  # Placeholder for actual anonymization logic
  return f"A{real_id[-6:]}"

def anonymize_dicom_file(file_path, output_folder, instance_count, mapping_file):
  try:
    ds = pydicom.dcmread(str(file_path))
    real_id, modality, sequence = extract_info(ds)
    anon_patient_id = generate_anon_id(real_id)
    
    update_id_mapping(mapping_file, real_id, anon_patient_id)
    ds.PatientID = anon_patient_id
    ds.PatientName = "Anonymized"

    exam_date = datetime.strptime(ds.StudyDate, '%Y%m%d').strftime('%Y%m%d')
    new_file_name = f"{anon_patient_id}_{exam_date}_{modality}_{sequence}_{str(instance_count).zfill(5)}.dcm"

    ds.save_as(str(output_folder / new_file_name))
    return True, anon_patient_id  # Return True and the anonymized ID if successful
  except Exception as e:
    print(f"Error processing {file_path}: {e}")
    return False, None

# Define paths using pathlib for cross-platform compatibility
root_directory = Path(__file__).parent.parent.parent
print(root_directory)
# Change this after testing
source_folder = root_directory / "dicom-images-breast" / "tests" / "testing_data-pipeline_t001" / "known" / "raw"
output_folder = root_directory / "dataset-multimodal-breast" / "tests" / "dicom"
mapping_file = root_directory / "dicom-images-breast" / "data" / "mapping.csv"

print(source_folder)
print(output_folder)
print(mapping_file)

# Create output folder if it doesn't exist

output_folder.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists
print(f"Output folder: {output_folder}")
# Create mapping file if it doesn't exist
if not mapping_file.exists():
  with mapping_file.open('w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["RealID", "AnonID"])

# Dictionary to keep track of instance counts per patient
instance_counts = {}

# Process DICOM files
for file_path in source_folder.glob('*.dcm'):
  # Extract real patient ID from DICOM file first
  ds = pydicom.dcmread(str(file_path))
  real_id, _, _ = extract_info(ds)
  
  # Manage instance counts using real IDs
  if real_id not in instance_counts:
    instance_counts[real_id] = 1
  else:
    instance_counts[real_id] += 1
  
  # Now call anonymize_dicom_file with the correct instance count
  success, anon_patient_id = anonymize_dicom_file(file_path, output_folder, instance_counts[real_id], mapping_file)
  
  # Update counts for anonymized IDs here, if necessary
  # (This part depends on whether you track by real ID or anonymized ID post-anonymization)