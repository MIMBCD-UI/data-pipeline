#!/usr/bin/env python

"""
main.py: Module for running the data processing pipeline.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.5.0"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago", "Jacinto C. Nascimento"]

import logging
import os
from processor import process_directory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define source, output, and mapping file paths
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
source_folder = os.path.join(root_dir, "dicom-images-breast", "tests", "testing_data-pipeline_t002")
output_folder = os.path.join(root_dir, "dataset-multimodal-breast", "tests", "dicom")
mapping_file = os.path.join(root_dir, "dicom-images-breast", "data", "mapping.csv")

def main():
  # Print information about the data processing pipeline
  print("Current directory: ", root_dir)
  print("Source folder: ", source_folder)
  print("Output folder: ", output_folder)
  print("Mapping file: ", mapping_file)

  # Process DICOM files
  process_directory(source_folder, output_folder, mapping_file)

if __name__ == "__main__":
  main()
