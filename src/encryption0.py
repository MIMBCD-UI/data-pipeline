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
__credits__ = ["Carlos Santiago", "Jacinto C. Nascimento"]

import hashlib

def encrypt_patient_id(patient_id):
  """
  Encrypts the patient ID using SHA-256 hash function.

  Args:
    patient_id (str): Original patient ID.

  Returns:
    str: Encrypted patient ID with the same length as the original.
  """
  # Use SHA-256 hash function for encryption
  encrypted_id = hashlib.sha256(patient_id.encode()).hexdigest()
  # Truncate the encrypted ID to match the length of the original patient ID
  encrypted_id = encrypted_id[:len(patient_id)]
  print(patient_id)
  return encrypted_id
