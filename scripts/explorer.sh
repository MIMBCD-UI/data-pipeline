#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-22
# Revised Date: 2024-09-26  # Enhanced logging and optimized Patient ID matching.
# Version: 2.26
# Status: Development
# Usage: ./explorer.sh
# Example: ./scripts/explorer.sh
# Description: Processes DICOM files, extracts Patient IDs, compares with CSV, and moves matches to the "checking" folder.

# Exit script immediately if any command fails
set -e

# Configuration: Define how many files to process in one run.
FILE_LIMIT=50000  # Adjust the limit for production use

# Define key directories and file paths
home="$HOME"  # User's home directory
root_dir="$home/Git"  # Root directory for the project
unchecked_dir="$root_dir/dataset-multimodal-breast/data/curation/unexplored"  # Directory with unprocessed DICOM files
checking_dir="$root_dir/dataset-multimodal-breast/data/curation/checking"  # Directory to move matched DICOM files
csv_file="$root_dir/dataset-multimodal-breast/data/birads/anonymized_patients_birads_curation.csv"  # CSV file with patient data
LOG_DIR="$root_dir/dataset-multimodal-breast/data/logs"  # Log directory
LOG_FILE="$LOG_DIR/explorer_$(date +'%Y%m%d_%H%M%S').log"  # Log file with timestamp

# Ensure the log directory exists
mkdir -p "$LOG_DIR"

# Function to log messages to both console and log file
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Validate that required directories and files exist
validate_path() {
  if [ ! -e "$1" ]; then
    log_message "Error: $2 ($1) does not exist. Exiting."
    exit 1
  fi
}

# Ensure essential paths exist
validate_path "$unchecked_dir" "Unchecked folder"
validate_path "$checking_dir" "Checking folder"
validate_path "$csv_file" "CSV file"

# Function to extract the Patient ID from DICOM file metadata
# Uses `dcmdump` and extracts the Patient ID from the DICOM tag (0010,0020)
extract_patient_id() {
  local dicom_file="$1"
  log_message "Attempting to extract Patient ID from: $dicom_file"
  
  # Extract Patient ID from DICOM metadata, cleaning up any whitespace
  local patient_id=$(dcmdump +P PatientID "$dicom_file" 2>/dev/null | awk -F'[][]' '{print $2}' | tr -d '[:space:]')
  
  if [ -n "$patient_id" ]; then
    log_message "Successfully extracted Patient ID: $patient_id"
    echo "$patient_id"
  else
    log_message "No Patient ID found in DICOM file: $dicom_file"
    echo ""
  fi
}

# Function to check if a Patient ID exists in the CSV file
# Uses grep to look for exact matches in the second column of the CSV
patient_id_in_csv() {
  local patient_id="$1"
  
  # Log that we're checking for the patient ID in the CSV
  log_message "Checking if Patient ID: $patient_id exists in CSV..."
  
  # Use grep to search for the patient ID in the CSV
  if grep -q ",${patient_id}," "$csv_file"; then
    log_message "Patient ID: $patient_id found in CSV"
    return 0  # Found
  else
    log_message "Patient ID: $patient_id not found in CSV"
    return 1  # Not found
  fi
}

# Main function to process DICOM files
process_files() {
  local count=0  # Track number of processed files

  log_message "Starting to process DICOM files from: $unchecked_dir"
  
  # Find and process DICOM files in the unchecked directory
  find "$unchecked_dir" -type f -name "*.dcm" | head -n "$FILE_LIMIT" | while IFS= read -r dicom_file; do
    if (( count >= FILE_LIMIT )); then
      log_message "File limit of $FILE_LIMIT reached. Stopping."
      break
    fi

    # Extract Patient ID from DICOM file
    patient_id=$(extract_patient_id "$dicom_file")
    
    # Proceed if a valid Patient ID was extracted
    if [ -n "$patient_id" ]; then
      if patient_id_in_csv "$patient_id"; then
        # If the Patient ID exists in the CSV, move the DICOM file to the checking directory
        if mv "$dicom_file" "$checking_dir"; then
          log_message "Successfully moved $dicom_file to $checking_dir (Patient ID: $patient_id)"
        else
          log_message "Failed to move $dicom_file to $checking_dir. Skipping."
        fi
      else
        log_message "No matching Patient ID in CSV for: $dicom_file"
      fi
    else
      log_message "Skipping $dicom_file due to missing Patient ID."
    fi

    ((count++))  # Increment the file counter after each processed file
  done

  log_message "Processed $count file(s) out of the $FILE_LIMIT limit."
}

# Start processing DICOM files
process_files

log_message "DICOM file exploration completed successfully."

# End of script