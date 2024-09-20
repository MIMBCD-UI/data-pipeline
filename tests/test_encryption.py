#!/usr/bin/env python

"""
test_encryption.py: Unit tests for the encryption and secret phrase reading functionality.
This script tests two main functionalities: 
1. Encrypting a patient ID using a secret phrase.
2. Reading a secret phrase from a file.

The test ensures that the encryption process is working as expected, 
and that the secret phrase is correctly read from a temporary file.

Unit testing is achieved using the unittest framework.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.0.3"  # Incremented version to reflect improvements
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import unittest  # For creating and running test cases
import os  # To handle file paths and environment variables
import tempfile  # To create temporary files for testing
import logging  # To log messages and steps in the testing process
import sys  # To modify system path for module importing

# Add the project root directory to the system path for importing modules from 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions we are testing from the encryption module
from src.processing.encryption import encrypt_patient_id, read_secret_phrase

# Configure logging to log at the INFO level, including timestamps for each log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class TestEncryptionFunctions(unittest.TestCase):
  """
  This class contains unit tests for the encryption module.
  It ensures that patient ID encryption and secret phrase reading work correctly.
  """

  def setUp(self):
    """
    The setUp() method is executed before each test case.
    It creates a temporary file with a mock secret phrase, which is used to simulate reading from a real secret file.
    It also sets the SECRET_FILE_PATH environment variable to point to this temporary file.
    """
    logging.info("Setting up temporary secret file for testing...")
    # Create a temporary file to store the secret phrase
    self.temp_secret_file = tempfile.NamedTemporaryFile(delete=False)
    
    # Write the mock secret phrase into the file and flush the contents to disk
    self.temp_secret_file.write(b"my_secret_phrase")
    self.temp_secret_file.flush()

    # Set the environment variable to point to the temporary file's path
    os.environ["SECRET_FILE_PATH"] = self.temp_secret_file.name
    logging.info(f"Temporary secret file created at: {self.temp_secret_file.name}")

  def tearDown(self):
    """
    The tearDown() method is executed after each test case.
    It cleans up by removing the temporary secret file created during the setUp() phase.
    """
    logging.info(f"Cleaning up temporary file: {self.temp_secret_file.name}")
    if os.path.exists(self.temp_secret_file.name):
      os.remove(self.temp_secret_file.name)  # Remove the temporary file
      logging.info("Temporary file removed successfully.")

  def test_encrypt_patient_id(self):
    """
    This test ensures that the encrypt_patient_id function:
    1. Encrypts the patient ID.
    2. The encrypted ID has the same length as the original patient ID.
    """
    logging.info("Starting test: test_encrypt_patient_id")
    
    # Define a mock patient ID for testing
    test_patient_id = "12345678"
    logging.info(f"Original Patient ID: {test_patient_id}")
    
    # Encrypt the patient ID
    encrypted_id = encrypt_patient_id(test_patient_id)
    logging.info(f"Encrypted Patient ID: {encrypted_id}")

    # Verify that the encrypted ID is different from the original
    self.assertNotEqual(encrypted_id, test_patient_id, "Encrypted ID should not be the same as the original.")

    # Verify that the encrypted ID has the same length as the original ID
    self.assertEqual(len(encrypted_id), len(test_patient_id), "Encrypted ID should have the same length as the original.")
    logging.info("Test passed: Encrypted ID differs from the original and has the correct length.")

  def test_read_secret_phrase(self):
    """
    This test checks that the read_secret_phrase function correctly reads the secret phrase from the temporary file.
    """
    logging.info("Starting test: test_read_secret_phrase")

    # Read the secret phrase from the temporary file
    secret_phrase = read_secret_phrase(self.temp_secret_file.name)
    logging.info(f"Secret phrase read: {secret_phrase}")

    # Verify that the read secret phrase matches the expected value
    self.assertEqual(secret_phrase, "my_secret_phrase", "Secret phrase read does not match the expected value.")
    logging.info("Test passed: Secret phrase read matches the expected value.")

if __name__ == "__main__":
  """
  Entry point of the script when executed directly.
  It initializes logging and runs all the test cases within the TestEncryptionFunctions class.
  """
  logging.info("Starting the encryption test suite...")
  unittest.main()  # Discover and run all test methods in the TestEncryptionFunctions class

  logging.info("All encryption tests completed successfully.")

# End of file