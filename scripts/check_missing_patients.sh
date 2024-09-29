#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-28
# Revised Date: 2024-09-28
# Version: 1.3
# Status: Development
# Usage: ./check_missing_patients.sh
# Description: This script checks whether each anonymized Patient ID from the CSV file exists in any DICOM file within the "unexplored" folder.

# Exit script immediately if any command fails
set -e

# Configuration: Define key directories and file paths
home="$HOME"  # User's home directory
root_dir="$home/Git"  # Root directory where the project is located
# unchecked_dir="$root_dir/dataset-multimodal-breast/data/curation/unexplored"  # Directory with unprocessed DICOM files
unchecked_dir="$root_dir/dataset-multimodal-breast/data/curation/checking"  # TO DELETE
csv_file="$root_dir/dataset-multimodal-breast/data/birads/anonymized_patients_birads_curation.csv"  # CSV file with anonymized patient IDs
LOG_DIR="$root_dir/dataset-multimodal-breast/data/logs"  # Directory for log files
LOG_FILE="$LOG_DIR/check_missing_patients_$(date +'%Y%m%d_%H%M%S').log"  # Unique log file with timestamp

# Ensure the log directory exists (if not, create it)
mkdir -p "$LOG_DIR"

# Function to log messages to both the console and log file with a timestamp
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to validate the existence of required paths (directories or files)
# Arguments:
#   $1: Path to validate
#   $2: Friendly name for the error message
validate_path() {
  if [ ! -e "$1" ]; then
    log_message "Error: $2 ($1) does not exist. Exiting."
    exit 1  # Terminate script if the path is missing
  fi
}

# Ensure essential directories and CSV file exist before continuing
validate_path "$unchecked_dir" "Unchecked folder (DICOM directory)"
validate_path "$csv_file" "CSV file (Patient data)"

# Initialize arrays to store unique Patient IDs and Patient IDs not found in DICOM files
unique_patients=()  # Array to store unique Patient IDs
not_found_patients=()  # Array to store Patient IDs not found in DICOM files

# Function to check if an element exists in an array
# Arguments:
#   $1: Element to search
#   $2: Array to search in
element_in_array() {
  local element="$1"
  shift
  for item in "$@"; do
    if [[ "$item" == "$element" ]]; then
      return 0  # Element found
    fi
  done
  return 1  # Element not found
}

# Function to check if a given Patient ID exists in any DICOM file within the "unexplored" directory
# Arguments:
#   $1: The anonymized Patient ID to search for in the DICOM files
check_patient_in_dicom_files() {
  local patient_id="$1"

  # Search for the Patient ID in the filenames of the DICOM files
  if find "$unchecked_dir" -type f -name "*.dcm" | grep -q "$patient_id"; then
    log_message "Patient ID: $patient_id found in DICOM files."
  else
    log_message "Patient ID: $patient_id NOT found in any DICOM file."
    not_found_patients+=("$patient_id")  # Add to the list of missing Patient IDs
  fi
}

# Function to process the CSV and check for Patient IDs
process_csv() {
  log_message "Starting to process the CSV file: $csv_file"

  # Read the CSV file line by line, assuming Patient ID is in the second column
  while IFS=',' read -r col1 patient_id rest; do
    if [ -n "$patient_id" ]; then  # Ensure the Patient ID is not empty
      # Only process if the Patient ID is unique (not already in the array)
      if ! element_in_array "$patient_id" "${unique_patients[@]}"; then
        unique_patients+=("$patient_id")  # Add to unique list
        log_message "Checking Patient ID: $patient_id from CSV"
        check_patient_in_dicom_files "$patient_id"  # Call function to check if the Patient ID exists in DICOM files
      else
        log_message "Skipping duplicate Patient ID: $patient_id"
      fi
    fi
  done < "$csv_file"
}

# Start the process of checking Patient IDs from the CSV
process_csv

# After checking all Patient IDs, report any that were not found
if [ ${#not_found_patients[@]} -ne 0 ]; then
  log_message "Summary: The following Patient IDs were NOT found in any DICOM files:"
  for patient_id in "${not_found_patients[@]}"; do
    log_message "$patient_id"
  done
else
  log_message "All Patient IDs from the CSV were found in the DICOM files."
fi

# Log the total number of unique Patient IDs processed
log_message "Total number of unique Patient IDs processed: ${#unique_patients[@]}"

log_message "Patient ID check completed successfully."

# End of script