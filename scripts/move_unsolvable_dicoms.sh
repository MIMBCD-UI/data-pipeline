#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-29
# Revised Date: 2024-09-30  # Enhanced logging and optimized per-DICOM processing
# Version: 1.8
# Status: Development
# Usage: ./move_unsolvable_dicoms.sh
# Description: Reads DICOM files from the "checking" folder, extracts anonymized Patient ID, and moves the file to the "unsolvable" folder if no match is found in the CSV.

set -e  # Exit the script if any command fails

# Configuration: Define important directories and file paths
home="$HOME"  # User's home directory
root_dir="$home/Git"  # Root project directory
checking_dir="$root_dir/dataset-multimodal-breast/data/curation/checking"  # Folder with DICOM files to check
unsolvable_dir="$root_dir/dataset-multimodal-breast/data/curation/unsolvable"  # Folder for DICOM files with unmatched Patient IDs
csv_file="$root_dir/dataset-multimodal-breast/data/birads/anonymized_patients_birads_curation.csv"  # CSV file with anonymized Patient IDs

# Logging setup: Create a timestamped log file in the log directory
LOG_DIR="$root_dir/dataset-multimodal-breast/data/logs"
LOG_FILE="$LOG_DIR/move_unsolvable_dicoms_$(date +'%Y%m%d_%H%M%S').log"
mkdir -p "$LOG_DIR" "$unsolvable_dir"  # Ensure log and unsolvable directories exist

# Function to log messages with timestamps to both console and log file
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Validate critical file paths exist before proceeding
# Arguments:
#   $1: Path to validate
#   $2: Human-readable name of the path for error messages
validate_path() {
  if [ ! -e "$1" ]; then
    log_message "Error: $2 ($1) does not exist. Exiting."
    exit 1  # Exit if the path does not exist
  fi
}

# Ensure required paths exist
validate_path "$checking_dir" "Checking folder (DICOM files)"
validate_path "$csv_file" "CSV file (Patient data)"
validate_path "$unsolvable_dir" "Unsolvable folder"

# Function to extract the Patient ID from a DICOM file using `dcmdump`
# Arguments:
#   $1: Path to the DICOM file
extract_patient_id() {
  local dicom_file="$1"
  
  log_message "Extracting Patient ID from: $dicom_file"
  
  # Extract the Patient ID using dcmdump, format the result and remove extra spaces
  local patient_id=$(dcmdump +P PatientID "$dicom_file" 2>/dev/null | awk -F'[][]' '{print $2}' | tr -d '[:space:]')
  
  if [ -n "$patient_id" ]; then
    log_message "Successfully extracted Patient ID: $patient_id"
    echo "$patient_id"  # Return the Patient ID
  else
    log_message "Failed to extract Patient ID from: $dicom_file"
    echo ""  # Return an empty string if extraction fails
  fi
}

# Function to sanitize the Patient ID by removing any hidden characters or spaces
sanitize_patient_id() {
  local id="$1"
  echo "$id" | tr -d '[:space:]' | tr -d '\r' | tr -d '\n'  # Clean Patient ID of all extraneous characters
}

# Function to check if the Patient ID exists in the CSV file
# Arguments:
#   $1: The Patient ID to search for in the CSV file
patient_id_in_csv() {
  local patient_id="$1"
  
  log_message "Checking if Patient ID: $patient_id exists in the CSV..."
  
  # Sanitize the Patient ID for comparison
  local sanitized_id=$(sanitize_patient_id "$patient_id")
  
  # Use awk to check if the second column of the CSV contains the sanitized Patient ID
  if awk -F',' -v id="$sanitized_id" 'tolower($2) == tolower(id)' "$csv_file" > /dev/null; then
    log_message "Patient ID: $sanitized_id found in the CSV."
    return 0  # Return success if the Patient ID was found
  else
    log_message "Patient ID: $sanitized_id NOT found in the CSV."
    return 1  # Return failure if the Patient ID was not found
  fi
}

# Main function to process all DICOM files in the "checking" directory
process_dicom_files() {
  local file_count=0  # Initialize a counter for processed DICOM files
  
  log_message "Starting to process DICOM files from: $checking_dir"

  # Find all DICOM files in the checking directory
  find "$checking_dir" -type f -name "*.dcm" | while IFS= read -r dicom_file; do
    file_count=$((file_count + 1))  # Increment the file counter
    log_message "Processing DICOM file #$file_count: $dicom_file"  # Log file count and path
    
    # Extract the Patient ID from the DICOM file
    patient_id=$(extract_patient_id "$dicom_file")
    
    # If a valid Patient ID is extracted, check if it exists in the CSV
    if [ -n "$patient_id" ]; then
      sanitized_id=$(sanitize_patient_id "$patient_id")
      if patient_id_in_csv "$sanitized_id"; then
        log_message "Patient ID $sanitized_id found in CSV. No action needed for $dicom_file."
      else
        # Move file to the unsolvable folder if the Patient ID is not in the CSV
        if mv "$dicom_file" "$unsolvable_dir"; then
          log_message "Moved $dicom_file to the unsolvable folder (Patient ID: $sanitized_id not found in CSV)."
        else
          log_message "Error: Failed to move $dicom_file to the unsolvable folder."
        fi
      fi
    else
      log_message "Skipping $dicom_file due to missing Patient ID."
    fi

    echo "Processed DICOM file count: $file_count"  # Print the live count of processed files
  done

  log_message "Finished processing $file_count DICOM files."
}

# Start the DICOM file processing
process_dicom_files

log_message "Script execution completed successfully."

# End of script