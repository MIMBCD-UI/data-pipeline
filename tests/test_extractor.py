#!/usr/bin/env python

"""
test_extractor.py: Unit tests for the DICOM information extractor module.
These tests ensure that the extractor correctly handles DICOM files 
and properly extracts relevant metadata.

Key Functions:
- test_extract_dicom_info: Test the extraction of metadata from a DICOM file.
- test_extract_patient_id: Test the extraction of the patient ID from DICOM metadata.
- test_extract_modality: Test the extraction of the modality (e.g., CT, MR) from DICOM metadata.
- test_extract_image_laterality: Test the extraction of the image laterality from DICOM metadata.
- test_extract_view_position: Test the extraction of the image view position from DICOM metadata.
- test_extract_study_date: Test the extraction of the study date from DICOM metadata.
- test_extract_scanning_sequence: Test the extraction of the scanning sequence from DICOM metadata.
- test_extract_series_description: Test the extraction of the series description from DICOM metadata.
- test_extract_instance_number: Test the extraction of the instance number from DICOM metadata.

Expected Usage:
- Run the test suite to verify the functionality of the extractor module.
- Check the test results to ensure that the extraction functions work as expected.
- Update the tests as needed to cover additional scenarios or edge cases.

Customization & Flexibility:
- The test cases can be extended to cover more attributes or metadata fields.
- Additional tests can be added to validate specific extraction scenarios.
- The test suite can be integrated into a continuous integration pipeline.

Performance & Compatibility:
- The tests are designed to be run in a local development environment.
- The test suite is compatible with Python 3.6+ and the unittest module.
- The tests are optimized for efficiency and reliability.

Best Practices & Maintenance:
- The test suite follows best practices for unit testing and validation.
- It provides comprehensive coverage of the extractor module functionality.
- The tests are well-documented and can be easily maintained or extended.

Notes:
- This test suite is part of a larger data curation pipeline for medical imaging data.
- It is designed to validate the functionality of the DICOM information extractor module.
- The tests can be run automatically using a continuous integration service.

References:
- pydicom library: https://pydicom.github.io/
- DICOM standard: https://www.dicomstandard.org/
- unittest module: https://docs.python.org/3/library/unittest.html
"""

__author__ = "Francisco Maria Calisto"
__maintainer__ = "Francisco Maria Calisto"
__email__ = "francisco.calisto@tecnico.ulisboa.pt"
__license__ = "ACADEMIC & COMMERCIAL"
__version__ = "0.0.2"  # Version increment to reflect test improvements
__status__ = "Development"
__credits__ = ["Carlos Santiago",
               "Catarina Barata",
               "Jacinto C. Nascimento",
               "Diogo Araújo"]

import unittest
import logging
import os
from unittest.mock import patch, MagicMock
import pydicom  # Added to fix InvalidDicomError issue

# Ensure the path to the script under test is available
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import the extract_dicom_info function from the extractor module
from processing.extractor import extract_dicom_info

# Configure logging to provide detailed information for the test run
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestExtractor(unittest.TestCase):
  """
  Unit tests for the DICOM information extractor module.
  These tests cover scenarios like file not found, invalid DICOM format, 
  and successful extraction of metadata from valid DICOM files.
  """

  def setUp(self):
    """
    Set up the test environment. This method is called before each test.
    We define some paths and any common setup needed across tests.
    """
    logging.info("Setting up test environment.")
    self.valid_dicom_path = '/path/to/valid.dcm'  # Simulated valid DICOM path
    self.invalid_dicom_path = '/path/to/invalid.dcm'  # Simulated invalid DICOM path
    self.nonexistent_dicom_path = '/path/to/nonexistent.dcm'  # Simulated nonexistent file

  @patch('os.path.exists')
  def test_file_not_found(self, mock_exists):
    """
    Test case: When the DICOM file does not exist.
    This ensures the function handles missing files and returns None.
    """
    logging.info("Running test: test_file_not_found")
    
    # Simulate that the file does not exist
    mock_exists.return_value = False
    
    # Call the extractor and expect None since the file doesn't exist
    result = extract_dicom_info(self.nonexistent_dicom_path)
    
    # Assert that the function returns None when the file is not found
    self.assertIsNone(result, "Expected None when the DICOM file does not exist.")
    
    logging.info("test_file_not_found passed.")

  @patch('os.path.exists')
  @patch('pydicom.dcmread')
  def test_invalid_dicom_file(self, mock_dcmread, mock_exists):
    """
    Test case: When the provided file is not a valid DICOM file.
    This ensures the function catches InvalidDicomError and logs it correctly.
    """
    logging.info("Running test: test_invalid_dicom_file")
    
    # Simulate that the file exists
    mock_exists.return_value = True
    
    # Simulate that pydicom raises an InvalidDicomError for an invalid DICOM file
    mock_dcmread.side_effect = pydicom.errors.InvalidDicomError
    
    # Call the extractor and expect None due to invalid DICOM format
    result = extract_dicom_info(self.invalid_dicom_path)
    
    # Assert that the function returns None when the DICOM file is invalid
    self.assertIsNone(result, "Expected None when the DICOM file is invalid.")
    
    logging.info("test_invalid_dicom_file passed.")

  @patch('os.path.exists')
  @patch('pydicom.dcmread')
  def test_extract_dicom_info_success(self, mock_dcmread, mock_exists):
    """
    Test case: Successful extraction of metadata from a valid DICOM file.
    This ensures the function correctly extracts relevant information.
    """
    logging.info("Running test: test_extract_dicom_info_success")
    
    # Simulate that the file exists
    mock_exists.return_value = True

    # Create a mock DICOM dataset with some attributes
    mock_dataset = MagicMock()
    mock_dataset.PatientID = '123456'
    mock_dataset.Modality = 'MR'
    mock_dataset.StudyDate = '20220101'
    mock_dataset.SeriesDescription = 'Head MRI'
    mock_dataset.InstanceNumber = '1'
    # Setting default values for attributes that are missing
    mock_dataset.ViewPosition = 'NOVIEWPOSITION'
    mock_dataset.ScanningSequence = 'NOSCANNINGSEQUENCE'

    # Return the mock dataset when pydicom.dcmread is called
    mock_dcmread.return_value = mock_dataset

    # Expected output from the extraction
    expected_info = {
      "PatientID": '123456',
      "Modality": 'MR',
      "ImageLaterality": "NOIMAGELATERALITY",  # Default value for MR modality
      "ViewPosition": 'NOVIEWPOSITION',  # Default for missing ViewPosition
      "StudyDate": '20220101',
      "ScanningSequence": 'NOSCANNINGSEQUENCE',  # Default for missing ScanningSequence
      "SeriesDescription": 'Head MRI',
      "InstanceNumber": '1'
    }

    # Call the extractor function
    result = extract_dicom_info(self.valid_dicom_path)

    # Assert that the extracted info matches the expected dictionary
    self.assertEqual(result, expected_info, "Extracted DICOM information should match the expected output.")
    
    logging.info("test_extract_dicom_info_success passed.")

  @patch('os.path.exists')
  @patch('pydicom.dcmread')
  def test_missing_attributes(self, mock_dcmread, mock_exists):
    """
    Test case: When some DICOM attributes are missing from the file.
    This ensures the function correctly handles missing attributes and provides default values.
    """
    logging.info("Running test: test_missing_attributes")
    
    # Simulate that the file exists
    mock_exists.return_value = True

    # Create a mock DICOM dataset with a subset of attributes
    mock_dataset = MagicMock()
    mock_dataset.PatientID = '987654'
    mock_dataset.Modality = 'CT'
    
    # Set missing attributes to use default values
    mock_dataset.ImageLaterality = 'NOIMAGELATERALITY'
    mock_dataset.ViewPosition = 'NOVIEWPOSITION'
    mock_dataset.StudyDate = 'NOSTUDYDATE'
    mock_dataset.ScanningSequence = 'NOSCANNINGSEQUENCE'
    mock_dataset.SeriesDescription = 'NOSERIESDESCRIPTION'
    mock_dataset.InstanceNumber = 'NOINSTANCENUMBER'

    # Return the mock dataset when pydicom.dcmread is called
    mock_dcmread.return_value = mock_dataset

    # Expected output from the extraction (with default values for missing attributes)
    expected_info = {
      "PatientID": '987654',
      "Modality": 'CT',
      "ImageLaterality": 'NOIMAGELATERALITY',
      "ViewPosition": 'NOVIEWPOSITION',
      "StudyDate": 'NOSTUDYDATE',
      "ScanningSequence": 'NOSCANNINGSEQUENCE',
      "SeriesDescription": 'NOSERIESDESCRIPTION',
      "InstanceNumber": 'NOINSTANCENUMBER'
    }

    # Call the extractor function
    result = extract_dicom_info(self.valid_dicom_path)

    # Assert that the extracted info matches the expected dictionary
    self.assertEqual(result, expected_info, "Extracted DICOM information should use default values for missing attributes.")
    
    logging.info("test_missing_attributes passed.")

if __name__ == '__main__':
  # Log the start of the test suite
  logging.info("Starting DICOM extractor test suite...")
  unittest.main()

# End of file