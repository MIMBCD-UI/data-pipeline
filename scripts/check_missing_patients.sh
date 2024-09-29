#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-28
# Revised Date: 2024-09-29  # Improved directory modularization and file handling
# Version: 1.5.4
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./check_missing_patients.sh
# Example: ./scripts/check_missing_patients.sh
# Description: This script checks whether anonymized Patient IDs from the CSV file exist in any DICOM files
#              located in the "unexplored" folder. It logs all steps and handles large datasets.

# Exit the script immediately if any command fails
set -e

#############################
# Directory and File Setup
#############################

# Define the home directory using the system's HOME environment variable
home="$HOME"

# Modular directory structure (one level per variable for flexibility)
git_dir="$home/Git"                               # Git root directory
project_name="dataset-multimodal-breast"          # Project folder name
project_dir="$git_dir/$project_name"              # Full project directory

data_name="data"                                  # Data folder name
data_dir="$project_dir/$data_name"                # Full data directory

curation_name="curation"                          # Curation folder name
curation_dir="$data_dir/$curation_name"           # Full curation directory

unexplored_name="unexplored"                      # Folder containing unexplored DICOM files
unexplored_dir="$curation_dir/$unexplored_name"   # Full unexplored DICOM folder path

birads_name="birads"                              # BIRADS folder name
birads_dir="$data_dir/$birads_name"               # Full BIRADS directory

csv_filename="anonymized_patients_birads_curation.csv"  # CSV file name
csv_file="$birads_dir/$csv_filename"              # Full CSV file path

logs_name="logs"                                  # Logs folder name
logs_dir="$data_dir/$logs_name"                   # Full logs directory

# Log filename with a timestamp to keep logs unique
log_filename="check_missing_patients_$(date +'%Y%m%d_%H%M%S').log"
log_file="$logs_dir/$log_filename"                # Full log file path

# Ensure the log directory exists (create if necessary)
mkdir -p "$logs_dir"

#############################
# Logging Function
#############################

# Function to log messages with timestamps for better visibility
# Arguments:
#   $1: Message to log
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$log_file"
}

#############################
# Path Validation Function
#############################

# Function to validate that directories or files exist
# Arguments:
#   $1: Path to validate
#   $2: Friendly name for the error message
validate_path() {
  if [ ! -e "$1" ]; then
    log_message "Error: $2 ($1) does not exist. Exiting."
    exit 1  # Exit if the path is missing
  fi
}

# Ensure that the necessary directories and files exist
validate_path "$unexplored_dir" "Unexplored DICOM folder"
validate_path "$csv_file" "CSV file containing patient data"

#############################
# Initialize Arrays
#############################

# Arrays to store unique and missing Patient IDs
unique_patients=()     # To store unique Patient IDs from the CSV
not_found_patients=()  # To store Patient IDs not found in DICOM files

#############################
# Array Element Check Function
#############################

# Function to check if an element exists in an array
# Arguments:
#   $1: Element to search for
#   $2: Array to search within
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

#############################
# Patient ID Check Function
#############################

# Function to check whether a given Patient ID exists in DICOM filenames
# Arguments:
#   $1: Anonymized Patient ID to search for
check_patient_in_dicom_files() {
  local patient_id="$1"
  
  # Search for the Patient ID in DICOM filenames
  if find "$unexplored_dir" -type f -name "*.dcm" | grep -q "$patient_id"; then
    log_message "Patient ID: $patient_id found in DICOM files."
  else
    log_message "Patient ID: $patient_id NOT found in any DICOM file."
    not_found_patients+=("$patient_id")  # Add the missing Patient ID to the array
  fi
}

#############################
# CSV Processing Function
#############################

# Function to process the CSV and check for unique Patient IDs
process_csv() {
  log_message "Starting to process the CSV file: $csv_file"
  
  # Read the CSV, assuming the Patient IDs are in the second column
  while IFS=',' read -r _ patient_id _; do
    if [ -n "$patient_id" ]; then  # Ensure the Patient ID is not empty
      # Check for unique Patient IDs
      if ! element_in_array "$patient_id" "${unique_patients[@]}"; then
        unique_patients+=("$patient_id")  # Add unique Patient ID to the array
        log_message "Checking Patient ID: $patient_id from the CSV"
        check_patient_in_dicom_files "$patient_id"  # Check if the Patient ID exists in DICOM files
      else
        log_message "Skipping duplicate Patient ID: $patient_id"
      fi
    fi
  done < "$csv_file"
}

#############################
# Begin CSV Processing
#############################

process_csv

#############################
# Summarize Missing Patient IDs
#############################

# Summarize missing Patient IDs if any were not found in DICOM files
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

# Completion log message
log_message "Patient ID check completed successfully."

# End of script