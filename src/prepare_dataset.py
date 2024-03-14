#!/usr/bin/env python

"""prepare_dataset.py: Script to anonymize DICOM files and prepare dataset."""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.1.0"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago", "Jacinto C. Nascimento"]

import os
import pydicom
import csv
from datetime import datetime
from pathlib import Path
from dicomanonymizer import anonymize

# Existing functions like update_id_mapping, extract_info, generate_anon_id remain unchanged

def anonymize_dicom_file(file_path, output_folder, instance_count, mapping_file):
  try:
    ds = pydicom.dcmread(str(file_path))
    real_id, modality, sequence = extract_info(ds)
    anon_patient_id = generate_anon_id(real_id)

    # Update mapping with real to anonymized ID
    update_id_mapping(mapping_file, real_id, anon_patient_id)

    # Use dicom-anonymizer to anonymize the dataset
    anonymized_ds = anonymize(dataset=ds)

    # Construct new file name and save the anonymized DICOM
    exam_date = datetime.strptime(anonymized_ds.StudyDate, '%Y%m%d').strftime('%Y%m%d')
    new_file_name = f"{anon_patient_id}_{exam_date}_{modality}_{sequence}_{str(instance_count).zfill(5)}.dcm"
    anonymized_ds.save_as(str(output_folder / new_file_name))

    return True, anon_patient_id
  except Exception as e:
    print(f"Error processing {file_path}: {e}")
    return False, None

# The rest of your script for defining paths and processing DICOM files remains the same