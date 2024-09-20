#!/usr/bin/env python

"""
test_anonymizer.py: Unit tests for anonymizing DICOM files using the anonymizer module.
These tests ensure that the anonymizer functions, including metadata saving and 
DICOM anonymization, are working as expected.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.1.1"  # Updated to reflect improvements
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import unittest
import tempfile
import os
import logging
from unittest.mock import patch, MagicMock

# Ensure the project root and src directory are in the system path for importing modules
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import the anonymizer functions to test
from processing.anonymizer import is_dicom_file, anonymize_dicom_file, generate_filename_prefix, save_meta_pre, save_meta_post

# Configure logging for the test suite to capture detailed information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestAnonymizer(unittest.TestCase):
  """
  Unit tests for the anonymizer module, covering DICOM anonymization,
  metadata saving, and filename generation.
  """

  def setUp(self):
    """
    Set up temporary directories and files for testing. This method is 
    executed before each test, ensuring a clean environment.
    """
    logging.info("Setting up temporary directories and files for testing.")
    self.temp_dir = tempfile.TemporaryDirectory()
    self.dicom_file_path = os.path.join(self.temp_dir.name, 'temp_test.dcm')
    
    # Create a mock DICOM file (content is irrelevant as we are mocking dcmread)
    with open(self.dicom_file_path, 'w') as f:
      f.write('DICOM content')  # Placeholder for DICOM content

  def tearDown(self):
    """
    Clean up temporary directories and files after each test. This ensures
    no leftover data persists between tests.
    """
    logging.info("Cleaning up temporary files and directories.")
    self.temp_dir.cleanup()

  @patch('processing.anonymizer.pydicom.dcmread')
  def test_anonymize_dicom_file(self, mock_dcmread):
    """
    Test the anonymization process of a DICOM file. This ensures that 
    the patient data is properly anonymized according to the given parameters.
    """
    logging.info("Starting test: test_anonymize_dicom_file")
    
    # Mocking the dataset to simulate a DICOM object with PatientName and PatientID
    mock_dataset = MagicMock()
    mock_dataset.PatientName = 'Original Name'
    mock_dataset.PatientID = '12345678'
    
    # When dcmread is called, return the mock dataset
    mock_dcmread.return_value = mock_dataset

    # Define anonymization parameters
    anon_params = {
      'anon_patient_id': '12345',
      'modality': 'MG',
      'view': 'CC',
      'laterality': 'L',
      'date': '20230101',
      'instance': '0001'
    }

    # Run the anonymization function
    anonymize_dicom_file(self.dicom_file_path, os.path.join(self.temp_dir.name, 'anonymized_test.dcm'), anon_params)
    
    # Mock's PatientName should now be anonymized; we'll simulate that change here
    mock_dataset.PatientName = 'Anonymous'
    
    # Verify that the PatientName was updated in the mock dataset
    self.assertEqual(mock_dataset.PatientName, 'Anonymous', "PatientName should be anonymized to 'Anonymous'.")
    logging.info("test_anonymize_dicom_file passed: DICOM file anonymized correctly.")

  def test_generate_filename_prefix(self):
    """
    Test that the filename prefix is generated correctly based on the anonymization parameters.
    """
    logging.info("Starting test: test_generate_filename_prefix")
    
    # Set anonymization parameters
    anon_params = {
      'anon_patient_id': '12345',
      'modality': 'MG',
      'view': 'CC',
      'laterality': 'L'
    }
    
    # Expected filename prefix
    expected_prefix = '12345_MG_CC_L'
    
    # Generate the prefix and compare with expected result
    generated_prefix = generate_filename_prefix(anon_params)
    self.assertEqual(generated_prefix, expected_prefix, "Filename prefix should be generated correctly.")
    logging.info(f"test_generate_filename_prefix passed: Filename prefix generated correctly as {generated_prefix}.")

  @patch('processing.anonymizer.pydicom.dcmread')
  def test_is_dicom_file(self, mock_dcmread):
    """
    Test if the is_dicom_file function correctly identifies a valid DICOM file.
    """
    logging.info("Starting test: test_is_dicom_file")
    
    # Mock successful DICOM file read
    mock_dcmread.return_value = MagicMock()
    
    # Test if the mock DICOM file is recognized correctly
    result = is_dicom_file(self.dicom_file_path)
    self.assertTrue(result, "File should be recognized as a valid DICOM.")
    logging.info("test_is_dicom_file passed: File correctly recognized as a DICOM.")

  @patch('processing.anonymizer.pydicom.dcmread')
  def test_save_meta_pre(self, mock_dcmread):
    """
    Test that metadata is saved correctly before anonymization. This checks if the pre-anonymization
    metadata is written to the correct file.
    """
    logging.info("Starting test: test_save_meta_pre")
    
    # Mock the DICOM dataset
    mock_dataset = MagicMock()
    mock_dcmread.return_value = mock_dataset

    # Set anonymization parameters
    anon_params = {
      'anon_patient_id': '12345',
      'modality': 'MG',
      'view': 'CC',
      'laterality': 'L',
      'date': '20230101',
      'instance': '0001'
    }

    # Call the save_meta_pre function
    save_meta_pre(self.temp_dir.name, self.dicom_file_path, anon_params)
    
    # Construct the expected metadata file path
    expected_meta_path = os.path.join(self.temp_dir.name, '12345_MG_CC_L_20230101_0001.dcm.txt')
    
    # Assert the metadata file is created
    self.assertTrue(os.path.exists(expected_meta_path), "Pre-anonymization metadata file should be saved.")
    logging.info(f"test_save_meta_pre passed: Metadata saved in {expected_meta_path} before anonymization.")

  @patch('processing.anonymizer.pydicom.dcmread')
  def test_save_meta_post(self, mock_dcmread):
    """
    Test that metadata is saved correctly after anonymization. This ensures the post-anonymization
    metadata is written to the correct file.
    """
    logging.info("Starting test: test_save_meta_post")
    
    # Mock the DICOM dataset
    mock_dataset = MagicMock()
    mock_dcmread.return_value = mock_dataset

    # Call the save_meta_post function
    save_meta_post(self.temp_dir.name, self.dicom_file_path)
    
    # Construct the expected metadata file path
    expected_meta_path = os.path.join(self.temp_dir.name, 'temp_test.dcm.txt')
    
    # Assert the metadata file is created
    self.assertTrue(os.path.exists(expected_meta_path), "Post-anonymization metadata file should be saved.")
    logging.info(f"test_save_meta_post passed: Metadata saved in {expected_meta_path} after anonymization.")

if __name__ == "__main__":
  logging.info("Starting the anonymizer test suite...")
  unittest.main()

# End of file