#!/usr/bin/env python

"""
.py: TODO
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
from processor import process_directory

if __name__ == "__main__":
    # Define input and output folders
    source_folder = "/Users/francisco/Git/dicom-images-breast/tests/testing_data-pipeline_t001/known/raw"
    output_folder = "/Users/francisco/Git/dataset-multimodal-breast/tests/dicom"

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Process directory to anonymize DICOM files
    process_directory(source_folder, output_folder)
