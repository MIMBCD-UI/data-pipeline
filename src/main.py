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

import os
import logging
from processor import process_directory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
  """
  Main function to execute the data processing pipeline.
  """
  source_folder = "/Users/francisco/Git/dicom-images-breast/tests/testing_data-pipeline_t001/known/raw"
  output_folder = "/Users/francisco/Git/dataset-multimodal-breast/tests/dicom"
  process_directory(source_folder, output_folder)

if __name__ == "__main__":
  main()