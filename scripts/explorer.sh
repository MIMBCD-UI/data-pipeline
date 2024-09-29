#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-22
# Revised Date: 2024-09-29  # Modularized directory structure with enhanced logging
# Version: 2.2.11  # Version increment for modularity and handling massive datasets
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./explorer.sh
# Example: ./scripts/explorer.sh
# Description: Processes DICOM files, extracts Patient IDs, compares them with a CSV file, and moves matching files to the "checking" folder.

# Exit script immediately if any command fails
set -e

# Configuration: Set the maximum number of DICOM files to process in one run
FILE_LIMIT=50000  # Adjust for production or testing needs

#############################
# Modular Directory Structure
#############################

# Define user and project directories
home="$HOME"  # User's home directory
git_root="$home/Git"  # Root directory for Git projects
dataset_project="dataset-multimodal-breast"  # Project name

# Define the structure of the directories using modular components
data_dir="$git_root/$dataset_project/data"  # Data folder within the project
curation_dir="$data_dir/curation"  # Curation folder within the data directory
unchecked_dir="$curation_dir/unexplored"  # Directory for unprocessed DICOM files
checking_dir="$curation_dir/checking"  # Directory to move files with matching Patient IDs
birads_dir="$data_dir/birads"  # BIRADS-related data directory

# Define the CSV file and log paths
csv_filename="anonymized_patients_birads_curation.csv"  # Name of the CSV file containing anonymized Patient IDs
csv_file="$birads_dir/$csv_filename"  # Full path to the CSV file
log_dir="$data_dir/logs"  # Log directory
log_file="$log_dir/explorer_$(date +'%Y%m%d_%H%M%S').log"  # Log file with a timestamp for uniqueness

# Ensure the log directory exists; create it if it does not
mkdir -p "$log_dir"

#############################
# Logging Function
#############################

# Function to log messages with timestamps to both console and log file
# Arguments:
#   $1: Message to log
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$log_file"
}

#############################
# Path Validation Function
#############################

# Function to validate that directories or files exist before proceeding
# Arguments:
#   $1: Path to validate
#   $2: Friendly name to display in case of an error
validate_path() {
  if [ ! -e "$1" ]; then
    log_message "Error: $2 ($1) does not exist. Exiting."
    exit 1  # Exit the script if the path is invalid
  fi
}

# Validate that all required paths (directories and the CSV file) exist before proceeding
validate_path "$unchecked_dir" "Unchecked DICOM folder"
validate_path "$checking_dir" "Checking folder"
validate_path "$csv_file" "CSV file"

#############################
# DICOM Processing Functions
#############################

# Function to extract the Patient ID from a DICOM file using dcmdump
# Arguments:
#   $1: Full path to the DICOM file
extract_patient_id() {
  local dicom_file="$1"
  
  log_message "Attempting to extract Patient ID from: $dicom_file"
  
  # Use dcmdump to extract the Patient ID from tag (0010,0020), clean the output, and remove extra spaces
  local patient_id=$(dcmdump +P PatientID "$dicom_file" 2>/dev/null | awk -F'[][]' '{print $2}' | tr -d '[:space:]')
  
  if [ -n "$patient_id" ]; then
    log_message "Successfully extracted Patient ID: $patient_id"
    echo "$patient_id"  # Return the extracted Patient ID
  else
    log_message "No Patient ID found in DICOM file: $dicom_file"
    echo ""  # Return an empty string if extraction fails
  fi
}

# Function to check if a given Patient ID exists in the CSV file
# Arguments:
#   $1: The Patient ID to search for
patient_id_in_csv() {
  local patient_id="$1"
  
  log_message "Checking if Patient ID: $patient_id exists in the CSV file..."
  
  # Search for the Patient ID in the CSV, ensuring an exact match in the second column
  if grep -q ",${patient_id}," "$csv_file"; then
    log_message "Patient ID: $patient_id found in the CSV."
    return 0  # Patient ID found
  else
    log_message "Patient ID: $patient_id not found in the CSV."
    return 1  # Patient ID not found
  fi
}

#############################
# Main File Processing Function
#############################

# Function to process DICOM files and check Patient IDs against the CSV
process_files() {
  local count=0  # Initialize a counter for processed files

  log_message "Starting to process DICOM files from: $unchecked_dir"
  
  # Find all DICOM files in the unexplored folder, limiting to the FILE_LIMIT
  find "$unchecked_dir" -type f -name "*.dcm" | head -n "$FILE_LIMIT" | while IFS= read -r dicom_file; do
    # Stop processing if the file limit is reached
    if (( count >= FILE_LIMIT )); then
      log_message "File limit of $FILE_LIMIT reached. Stopping."
      break
    fi

    # Extract the Patient ID from the DICOM file
    patient_id=$(extract_patient_id "$dicom_file")
    
    # If a valid Patient ID is extracted, check if it exists in the CSV
    if [ -n "$patient_id" ]; then
      if patient_id_in_csv "$patient_id"; then
        # Move the DICOM file to the checking folder if the Patient ID matches
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