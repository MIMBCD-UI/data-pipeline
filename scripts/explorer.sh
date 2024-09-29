#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-22
# Revised Date: 2024-09-28  # Improved logging, error handling, and optimized Patient ID processing
# Version: 2.28
# Status: Development
# Usage: ./explorer.sh
# Example: ./scripts/explorer.sh
# Description: Processes DICOM files, extracts Patient IDs, compares with CSV, and moves matches to the "checking" folder.

# Exit script immediately if any command fails to prevent further errors
set -e

# Configuration: Set the maximum number of DICOM files to process in one run
FILE_LIMIT=50000  # You can adjust this for testing or set higher for production

# Define key directories and file paths for processing
home="$HOME"  # User's home directory
root_dir="$home/Git"  # Root project directory
unchecked_dir="$root_dir/dataset-multimodal-breast/data/curation/unexplored"  # Unprocessed DICOM files
checking_dir="$root_dir/dataset-multimodal-breast/data/curation/checking"  # Folder for files with matching Patient IDs
csv_file="$root_dir/dataset-multimodal-breast/data/birads/anonymized_patients_birads_curation.csv"  # CSV file containing anonymized patient IDs
LOG_DIR="$root_dir/dataset-multimodal-breast/data/logs"  # Log directory for all logging
LOG_FILE="$LOG_DIR/explorer_$(date +'%Y%m%d_%H%M%S').log"  # Log file with timestamp for uniqueness

# Ensure the log directory exists, creating it if necessary
mkdir -p "$LOG_DIR"

# Function to log messages with timestamps
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Validate if a directory or file exists, exiting the script if it doesn't
# Arguments:
#   $1: Path to validate
#   $2: Friendly name to display in case of an error
validate_path() {
  if [ ! -e "$1" ]; then
    log_message "Error: $2 ($1) does not exist. Exiting."
    exit 1  # Terminate the script if the path is invalid
  fi
}

# Validate that all required paths (directories and CSV file) exist before starting
validate_path "$unchecked_dir" "Unchecked DICOM folder"
validate_path "$checking_dir" "Checking folder"
validate_path "$csv_file" "CSV file"

# Function to extract the Patient ID from a DICOM file
# Uses dcmdump to extract Patient ID from tag (0010,0020) and cleans output
# Arguments:
#   $1: Full path to the DICOM file
extract_patient_id() {
  local dicom_file="$1"
  
  log_message "Attempting to extract Patient ID from: $dicom_file"
  
  # Extract Patient ID using dcmdump, capturing only the ID and removing extra whitespace
  local patient_id=$(dcmdump +P PatientID "$dicom_file" 2>/dev/null | awk -F'[][]' '{print $2}' | tr -d '[:space:]')
  
  # Check if a Patient ID was extracted and log the result
  if [ -n "$patient_id" ]; then
    log_message "Successfully extracted Patient ID: $patient_id"
    echo "$patient_id"  # Return the Patient ID
  else
    log_message "No Patient ID found in DICOM file: $dicom_file"
    echo ""  # Return an empty string if no ID was found
  fi
}

# Function to check if a given Patient ID exists in the CSV file
# Uses grep to search for the ID in the second column of the CSV
# Arguments:
#   $1: The Patient ID to search for
patient_id_in_csv() {
  local patient_id="$1"
  
  log_message "Checking if Patient ID: $patient_id exists in the CSV file..."
  
  # Search for the Patient ID in the CSV, ensuring an exact match in the correct column
  if grep -q ",${patient_id}," "$csv_file"; then
    log_message "Patient ID: $patient_id found in the CSV"
    return 0  # Return 0 (success) if the Patient ID is found
  else
    log_message "Patient ID: $patient_id not found in the CSV"
    return 1  # Return 1 (failure) if the Patient ID is not found
  fi
}

# Main function to process the DICOM files
process_files() {
  local count=0  # Initialize a counter for processed files

  log_message "Starting to process DICOM files from: $unchecked_dir"
  
  # Find all DICOM files in the unexplored folder, limiting to the FILE_LIMIT
  find "$unchecked_dir" -type f -name "*.dcm" | head -n "$FILE_LIMIT" | while IFS= read -r dicom_file; do
    # Stop processing if the file limit has been reached
    if (( count >= FILE_LIMIT )); then
      log_message "File limit of $FILE_LIMIT reached. Stopping."
      break
    fi

    # Extract the Patient ID from the DICOM file
    patient_id=$(extract_patient_id "$dicom_file")
    
    # Proceed if a valid Patient ID was extracted
    if [ -n "$patient_id" ]; then
      # Check if the Patient ID exists in the CSV
      if patient_id_in_csv "$patient_id"; then
        # Attempt to move the DICOM file if the Patient ID matches
        if mv "$dicom_file" "$checking_dir"; then
          log_message "Successfully moved $dicom_file to $checking_dir (Patient ID: $patient_id)"
        else
          log_message "Error: Failed to move $dicom_file to $checking_dir. Skipping this file."
        fi
      else
        log_message "No matching Patient ID in CSV for: $dicom_file"
      fi
    else
      log_message "Skipping $dicom_file due to missing or invalid Patient ID."
    fi

    ((count++))  # Increment the file counter
  done

  log_message "Processed $count file(s) out of the $FILE_LIMIT limit."
}

# Start processing the DICOM files
process_files

log_message "DICOM file exploration completed successfully."

# End of script