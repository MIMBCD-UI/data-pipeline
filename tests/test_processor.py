#!/usr/bin/env python

"""
test_processor.py: Unit tests for the processor module.

These tests ensure that the DICOM batch processing script functions correctly,
including anonymization, file handling, and batch processing.
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.8.0"  # Version increment to reflect improvements
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import unittest
from unittest.mock import patch, mock_open
import os
import logging
import sys
import csv

# Configure logging to capture detailed debugging information during tests
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Append the src directory to sys.path to import modules correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..', 'src'))
sys.path.insert(0, src_dir)

# Import the processing functions to be tested
from processing.processor import process_directory, construct_filename_prefix

class TestProcessor(unittest.TestCase):
  """
  Unit tests for the processor.py script that handles large DICOM datasets with batch processing.
  These tests cover file processing, anonymization, and batch processing behavior.
  """

  def setUp(self):
    """
    Setup method to initialize variables and mock directories before each test.
    Creates a mock environment for testing batch processing and anonymization.
    """
    logging.debug("Setting up test environment.")

    # Define mock directories and files for testing
    self.source_folder = os.path.join(os.sep, 'mock', 'source')  # Mock source directory
    self.output_folder = os.path.join(os.sep, 'mock', 'output')  # Mock output directory for anonymized files
    self.mapping_file = os.path.join(os.sep, 'mock', 'mapping.csv')  # Mock mapping file for patient ID mapping
    self.batch_size = 2  # Small batch size for testing purposes

    # Ensure the mock directories exist by mocking os.makedirs
    with patch('os.makedirs') as mock_makedirs:
      os.makedirs(self.source_folder, exist_ok=True)
      os.makedirs(self.output_folder, exist_ok=True)
      logging.debug(f"Mock directories created: {self.source_folder}, {self.output_folder}")

  @patch('processing.processor.anonymize_dicom_file')  # Mock the anonymization function
  @patch('processing.processor.is_dicom_file')  # Mock the DICOM validation function
  @patch('processing.processor.extract_dicom_info')  # Mock the DICOM metadata extraction function
  @patch('processing.processor.encrypt_patient_id')  # Mock the patient ID encryption function
  @patch('os.makedirs')  # Mock os.makedirs to avoid actual directory creation
  @patch('os.path.exists')  # Mock os.path.exists to control file existence checks
  def test_process_directory_batch(self, mock_exists, mock_makedirs, mock_encrypt, mock_extract, mock_is_dicom, mock_anonymize):
    """
    Test the batch processing mechanism in the process_directory function.
    Ensures that files are processed in batches and anonymized correctly.
    """
    logging.info("Running test: test_process_directory_batch")

    # Mock the list of files in the source directory
    mock_files = ['file1.dcm', 'file2.dcm', 'file3.dcm']
    logging.debug(f"Mock files in source directory: {mock_files}")

    # Mock os.walk to simulate directory traversal
    with patch('os.walk') as mock_walk:
      mock_walk.return_value = [(self.source_folder, [], mock_files)]
      logging.debug(f"os.walk mocked to return: {mock_walk.return_value}")

      # Setup return values for the mocked DICOM-related functions
      mock_is_dicom.return_value = True  # All files are considered valid DICOM files
      mock_extract.side_effect = [
        {'PatientID': '123456', 'Modality': 'MR', 'StudyDate': '20220101'},
        {'PatientID': '123456', 'Modality': 'MR', 'StudyDate': '20220101'},
        {'PatientID': '789012', 'Modality': 'CT', 'StudyDate': '20220202'}
      ]
      mock_encrypt.side_effect = ['anon123', 'anon456']  # Mock anonymized patient IDs
      logging.debug("Mocked DICOM functions setup complete.")

      # Use mock_open to simulate file operations without actual I/O
      with patch('builtins.open', mock_open()) as mocked_file:
        logging.debug("Starting process_directory function with mocked environment.")

        # Call the function under test
        process_directory(self.source_folder, self.output_folder, self.mapping_file, self.batch_size)

        # Assertions to verify the expected behavior
        self.assertEqual(mock_anonymize.call_count, 3, "All DICOM files should be anonymized.")
        logging.debug(f"Anonymization function called {mock_anonymize.call_count} times.")

        logging.info("test_process_directory_batch passed.")

  @patch('processing.processor.anonymize_dicom_file')  # Mock the anonymization function
  @patch('processing.processor.is_dicom_file')  # Mock the DICOM validation function
  @patch('processing.processor.extract_dicom_info')  # Mock the DICOM metadata extraction function
  @patch('processing.processor.encrypt_patient_id')  # Mock the patient ID encryption function
  @patch('os.makedirs')  # Mock os.makedirs to avoid actual directory creation
  @patch('os.path.exists')  # Mock os.path.exists to control file existence checks
  def test_anonymization_flow(self, mock_exists, mock_makedirs, mock_encrypt, mock_extract, mock_is_dicom, mock_anonymize):
    """
    Test the full anonymization flow from metadata extraction to file anonymization.
    Ensures that anonymization is triggered with correct parameters.
    """
    logging.info("Running test: test_anonymization_flow")

    # Mock return values for DICOM-related functions
    mock_is_dicom.return_value = True  # All files are considered valid DICOM files
    mock_extract.return_value = {
      'PatientID': '123456',
      'Modality': 'MG',
      'StudyDate': '20220101',
      'ImageLaterality': 'L',
      'ViewPosition': 'CC',
      'InstanceNumber': '1',
      'ScanningSequence': 'NOSCANNINGSEQUENCE',
      'SeriesDescription': 'NOSERIESDESCRIPTION'
    }
    mock_encrypt.return_value = 'anon123'  # Mock encrypted patient ID
    logging.debug("Mocked DICOM functions setup complete.")

    # Mock the list of files in the source directory
    mock_files = ['file1.dcm']
    logging.debug(f"Mock files in source directory: {mock_files}")

    # Mock os.walk to simulate directory traversal
    with patch('os.walk') as mock_walk:
      mock_walk.return_value = [(self.source_folder, [], mock_files)]
      logging.debug(f"os.walk mocked to return: {mock_walk.return_value}")

      # Use mock_open to simulate file operations without actual I/O
      with patch('builtins.open', mock_open()) as mocked_file:
        logging.debug("Starting process_directory function with mocked environment.")

        # Call the function under test
        process_directory(self.source_folder, self.output_folder, self.mapping_file, self.batch_size)

        # Verify that anonymize_dicom_file was called at least once
        self.assertGreater(mock_anonymize.call_count, 0, "anonymize_dicom_file should have been called.")
        logging.debug(f"Anonymization function called {mock_anonymize.call_count} times.")

        # Construct expected arguments for the anonymization function
        expected_input_path = os.path.join(self.source_folder, 'file1.dcm')
        expected_output_path = os.path.join(self.output_folder, 'anon123_MG_CC_L_20220101_1_00000001.dcm')
        expected_anon_params = {
          'anon_patient_id': 'anon123',
          'modality': 'MG',
          'view': 'CC',
          'laterality': 'L',
          'date': '20220101',
          'sequence': 'NOSCANNINGSEQUENCE',
          'series': 'NOSERIESDESCRIPTION',
          'instance': '1_00000001'
        }

        # Ensure anonymize_dicom_file was called with the expected arguments
        mock_anonymize.assert_any_call(
          expected_input_path,
          expected_output_path,
          expected_anon_params
        )
        logging.debug(f"Anonymization function called with expected arguments: {expected_input_path}, {expected_output_path}, {expected_anon_params}")

        logging.info("test_anonymization_flow passed.")

  @patch('os.path.exists')  # Mock os.path.exists to control file existence checks
  def test_construct_filename_prefix(self, mock_exists):
    """
    Test the filename prefix construction logic based on DICOM metadata.
    Ensures the correct filename is generated from anonymization parameters.
    """
    logging.info("Running test: test_construct_filename_prefix")

    # Test cases for different modalities and parameters
    test_cases = [
      {
        'args': ('anon123', 'MG', 'CC', 'L', 'Routine'),
        'expected': 'anon123_MG_CC_L',
        'description': 'Mammography (MG) modality'
      },
      {
        'args': ('anon123', 'US', 'TRANS', 'R', 'Abdomen'),
        'expected': 'anon123_US_TRANS_R',
        'description': 'Ultrasound (US) modality'
      },
      {
        'args': ('anon123', 'MR', '', '', 'BrainScan'),
        'expected': 'anon123_MR_BrainScan',
        'description': 'MRI (MR) modality'
      }
    ]

    # Iterate over test cases and assert expected results
    for test_case in test_cases:
      prefix = construct_filename_prefix(*test_case['args'])
      logging.debug(f"Constructed prefix '{prefix}' for {test_case['description']}")
      self.assertEqual(prefix, test_case['expected'], f"Filename prefix for {test_case['description']} should match.")
      logging.debug(f"Test case passed for {test_case['description']}")

    logging.info("test_construct_filename_prefix passed.")

if __name__ == '__main__':
  logging.info("Starting processor module test suite...")
  unittest.main()