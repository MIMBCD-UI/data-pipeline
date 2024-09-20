#!/usr/bin/env python

"""
encryption.py: Optimized module for encrypting patient IDs.

This module reads a secret phrase from a file and uses it to encrypt patient IDs with SHA-256 hashing.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.6.3"  # Updated after improvements
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import hashlib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the root folder path
root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
default_secret_path = os.path.join(root_folder, "secrets", "phrases", "data_pipeline_secret_phrase.txt")
secret_file_path = os.getenv("SECRET_FILE_PATH", default_secret_path)

def read_secret_phrase(file_path):
  """
  Reads the secret phrase from an external file.

  Args:
    file_path (str): Path to the file containing the secret phrase.

  Returns:
    str: Secret phrase read from the file.

  Raises:
    FileNotFoundError: If the secret file does not exist.
    Exception: For any other issues reading the file.
  """
  if not os.path.exists(file_path):
    logger.error(f"Secret phrase file not found at {file_path}")
    raise FileNotFoundError(f"Secret phrase file not found at {file_path}")
  
  try:
    with open(file_path, "r") as file:
      secret_phrase = file.read().strip()
      if not secret_phrase:
        raise ValueError("Secret phrase file is empty.")
      logger.info(f"Successfully read secret phrase from {file_path}")
      return secret_phrase
  except Exception as e:
    logger.error(f"Error reading secret phrase: {e}")
    raise

def encrypt_patient_id(patient_id):
  """
  Encrypts the patient ID using SHA-256 hash combined with a secret phrase.

  Args:
    patient_id (str): Original patient ID to be encrypted.

  Returns:
    str: Encrypted and truncated patient ID to match the length of the original ID.

  Raises:
    ValueError: If patient_id is empty.
  """
  if not patient_id:
    logger.error("Patient ID is empty. Cannot encrypt an empty ID.")
    raise ValueError("Patient ID cannot be empty.")

  try:
    # Read the secret phrase from the file
    secret_phrase = read_secret_phrase(secret_file_path)

    # Combine the secret phrase with the patient ID and hash using SHA-256
    combined_str = f"{secret_phrase}{patient_id}"
    encrypted_id = hashlib.sha256(combined_str.encode()).hexdigest()

    # Truncate the encrypted ID to the length of the original patient ID
    truncated_id = encrypted_id[:len(patient_id)]

    logger.info(f"Successfully encrypted patient ID {patient_id}")
    return truncated_id
  except Exception as e:
    logger.error(f"Encryption failed for patient ID {patient_id}: {e}")
    raise

# End of file