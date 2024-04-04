#!/usr/bin/env python

"""
encryption.py: Module for encrypting patient IDs.
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
import hashlib

# Define the root folder path
root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
secret_folder = os.path.join(root_folder, "secrets", "phrases")
secret_file_path = os.path.join(secret_folder, "data_pipeline_secret_phrase.txt")

# Define the function to read the secret phrase from an external file
def read_secret_phrase(rsp_secret_file_path):
  """
  Reads the secret phrase from an external file located in the root folder.

  Returns:
    str: Secret phrase read from the file.
  """
  with open(rsp_secret_file_path, "r") as file:
    # Read the secret phrase from the file
    rsp_secret_phrase = file.read().strip()
  return rsp_secret_phrase

# Define the function to encrypt the patient ID
def encrypt_patient_id(patient_id):
  """
  Encrypts the patient ID using SHA-256 hash function with a secret phrase.

  Args:
    patient_id (str): Original patient ID.

  Returns:
    str: Encrypted patient ID with the same length as the original.
  """
  # Read the secret phrase from the file
  epi_secret_phrase = read_secret_phrase(secret_file_path)

  
  # Combine the patient ID and secret phrase
  combined_str = f"{epi_secret_phrase}{patient_id}"
  
  # Use SHA-256 hash function for encryption
  encrypted_id = hashlib.sha256(combined_str.encode()).hexdigest()
  
  # Truncate the encrypted ID to match the length of the original patient ID
  encrypted_id = encrypted_id[:len(patient_id)]
  
  return encrypted_id

# End of file