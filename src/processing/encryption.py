#!/usr/bin/env python

"""
encryption.py: Module for encrypting patient IDs.

This module provides functions for encrypting patient IDs using the SHA-256 hash function
combined with a secret phrase. The encrypted patient IDs are truncated to match the length
of the original IDs to ensure consistency and compatibility with existing data.

Key Functions:
- read_secret_phrase: Read the secret phrase from an external file.
- encrypt_patient_id: Encrypt a patient ID using the secret phrase.

Expected Usage:
- Read the secret phrase from a file using `read_secret_phrase`.
- Encrypt a patient ID using `encrypt_patient_id`.

Customization & Flexibility:
- The encryption algorithm can be easily modified or extended to use different hash functions.
- The secret phrase can be updated or changed to enhance security and protect sensitive data.
- The encryption process can be adapted to include additional metadata or parameters.

Performance & Compatibility:
- The encryption process is optimized for efficiency and security using the SHA-256 hash function.
- The module is compatible with Python 3.6+ and can be used in various environments and platforms.
- The encryption functions are designed to handle large datasets and sensitive patient information.

Best Practices & Maintenance:
- The script follows best practices for error handling, logging, and code readability.
- It is well-documented and can be easily maintained or extended by other developers.
- The script is designed to be robust and reliable for long-term use in data curation workflows.

Notes:
- This module is part of a larger data curation pipeline for multimodal breast imaging data.
- It is optimized for processing DICOM files but can be adapted for other types of medical imaging data.
- The script is designed to be run from the command line or as part of an automated workflow.

References:
- SHA-256 hash function: https://en.wikipedia.org/wiki/SHA-2
- Secure hash algorithms: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf
- Cryptographic hash functions: https://en.wikipedia.org/wiki/Cryptographic_hash_function
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.6.2"
__status__ = "Development"
__copyright__ = "Copyright 2024, Instituto Superior Técnico (IST)"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import os
import hashlib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the root folder path
root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
secret_file_path = os.getenv("SECRET_FILE_PATH", os.path.join(root_folder, "secrets", "phrases", "data_pipeline_secret_phrase.txt"))

def read_secret_phrase(file_path):
  """
  Reads the secret phrase from an external file.

  Args:
    file_path (str): Path to the file containing the secret phrase.

  Returns:
    str: Secret phrase read from the file.
  """
  try:
    with open(file_path, "r") as file:
      secret_phrase = file.read().strip()
      logging.info(f"Secret phrase successfully read from {file_path}")
      return secret_phrase
  except FileNotFoundError:
    logging.error(f"Secret phrase file not found: {file_path}")
    raise FileNotFoundError(f"Secret phrase file not found: {file_path}")
  except Exception as e:
    logging.error(f"Error reading secret phrase: {e}")
    raise Exception(f"Error reading secret phrase: {e}")

def encrypt_patient_id(patient_id):
  """
  Encrypts the patient ID using the SHA-256 hash function combined with a secret phrase.

  Args:
    patient_id (str): Original patient ID.

  Returns:
    str: Encrypted patient ID truncated to match the length of the original ID.
  """
  try:
    secret_phrase = read_secret_phrase(secret_file_path)
    combined_str = f"{secret_phrase}{patient_id}"
    encrypted_id = hashlib.sha256(combined_str.encode()).hexdigest()
    truncated_id = encrypted_id[:len(patient_id)]
    logging.info(f"Successfully encrypted patient ID {patient_id}")
    return truncated_id
  except Exception as e:
    logging.error(f"Error during encryption: {e}")
    raise e

# End of file