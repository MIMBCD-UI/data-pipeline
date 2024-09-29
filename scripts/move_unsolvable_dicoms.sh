#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-29
# Revised Date: 2024-09-29  # Fully modular directory and file handling with split variables
# Version: 1.9.3
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./move_unsolvable_dicoms.sh
# Description: Reads DICOM files from the "checking" folder, extracts anonymized Patient ID, 
#              and moves the file to the "unsolvable" folder if no match is found in the CSV.

set -e  # Exit the script if any command fails

#############################
# Modular Directory Setup (One Level Per Variable)
#############################

home="$HOME"                  # User's home directory
git_folder="Git"              # Git folder name
project_folder="dataset-multimodal-breast"  # Project folder
data_folder="data"            # Data folder inside the project
curation_folder="curation"    # Curation folder inside data
birads_folder="birads"        # Birads folder inside data

# Full path construction using split variables
root_dir="$home/$git_folder"  # Root project directory
project_dir="$root_dir/$project_folder"  # Full path to project directory
data_dir="$project_dir/$data_folder"  # Full path to data directory
curation_dir="$data_dir/$curation_folder"  # Full path to curation directory
birads_dir="$data_dir/$birads_folder"  # Full path to Birads directory

# DICOM directories
checking_folder="checking"    # Checking folder name
unsolvable_folder="unsolvable"  # Unsolvable folder name
checking_dir="$curation_dir/$checking_folder"  # Full path to checking directory
unsolvable_dir="$curation_dir/$unsolvable_folder"  # Full path to unsolvable directory

#############################
# Modular File Setup (CSV and Log File)
#############################

csv_file_name="anonymized_patients_birads_curation.csv"  # CSV file name
csv_file="$birads_dir/$csv_file_name"  # Full path to CSV file

# Log file setup
log_folder="logs"  # Logs folder name
logs_dir="$curation_dir/$log_folder"  # Full path to logs directory
log_file_name="move_unsolvable_dicoms_$(date +'%Y%m%d_%H%M%S').log"  # Log filename with timestamp
log_file="$logs_dir/$log_file_name"  # Full path to log file

# Create necessary directories if they don't exist
mkdir -p "$logs_dir" "$unsolvable_dir"

#############################
# Logging and Validation Functions
#############################

# Function to log messages with timestamps
# Logs both to the console and the log file
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$log_file"
}

# Function to validate that a directory or file exists
# Arguments:
#   $1: Path to validate
#   $2: Description for logging purposes
validate_path() {
  if [ ! -e "$1" ]; then
    log_message "Error: $2 ($1) does not exist. Exiting."
    exit 1  # Exit if the path does not exist
  else
    log_message "$2 exists: $1"
  fi
}

# Validate critical directories and the CSV file
validate_path "$checking_dir" "Checking folder (DICOM files)"
validate_path "$csv_file" "CSV file (Patient data)"
validate_path "$unsolvable_dir" "Unsolvable folder"

#############################
# Patient ID Extraction and Processing Functions
#############################

# Function to extract the Patient ID from a DICOM file
# Arguments:
#   $1: Full path to the DICOM file
extract_patient_id() {
  local dicom_file="$1"
  
  log_message "Attempting to extract Patient ID from: $dicom_file"
  
  # Use `dcmdump` to extract the Patient ID (0010,0020) from the DICOM file
  local patient_id=$(dcmdump +P PatientID "$dicom_file" 2>/dev/null | awk -F'[][]' '{print $2}' | tr -d '[:space:]')
  
  # Check if extraction was successful
  if [ -n "$patient_id" ]; then
    log_message "Successfully extracted Patient ID: $patient_id"
    echo "$patient_id"  # Return the extracted Patient ID
  else
    log_message "Error: Failed to extract Patient ID from: $dicom_file"
    echo ""  # Return an empty string if extraction fails
  fi
}

# Function to sanitize the Patient ID by removing unnecessary characters
# Arguments:
#   $1: The raw Patient ID
sanitize_patient_id() {
  local id="$1"
  echo "$id" | tr -d '[:space:]' | tr -d '\r' | tr -d '\n'  # Remove any extraneous characters
}

# Function to check if the Patient ID exists in the CSV file
# Arguments:
#   $1: The sanitized Patient ID
patient_id_in_csv() {
  local patient_id="$1"
  
  log_message "Checking if Patient ID: $patient_id exists in the CSV..."

  # Use `awk` to check if the Patient ID exists in the second column of the CSV
  if awk -F',' -v id="$patient_id" 'tolower($2) == tolower(id)' "$csv_file" > /dev/null; then
    log_message "Patient ID: $patient_id found in the CSV."
    return 0  # Return success if the Patient ID is found
  else
    log_message "Patient ID: $patient_id NOT found in the CSV."
    return 1  # Return failure if the Patient ID is not found
  fi
}

#############################
# Main Processing Function
#############################

# Function to process all DICOM files in the checking directory
process_dicom_files() {
  local file_count=0  # Initialize counter for the number of processed files

  log_message "Starting to process DICOM files from: $checking_dir"

  # Find all DICOM files in the checking directory
  find "$checking_dir" -type f -name "*.dcm" | while IFS= read -r dicom_file; do
    file_count=$((file_count + 1))  # Increment the file counter
    log_message "Processing DICOM file #$file_count: $dicom_file"  # Log the file number and path
    
    # Extract the Patient ID from the DICOM file
    patient_id=$(extract_patient_id "$dicom_file")
    
    # Check if a valid Patient ID was extracted
    if [ -n "$patient_id" ]; then
      # Sanitize the Patient ID before checking it in the CSV
      sanitized_id=$(sanitize_patient_id "$patient_id")
      
      # Check if the sanitized Patient ID exists in the CSV
      if patient_id_in_csv "$sanitized_id"; then
        log_message "Patient ID $sanitized_id found in CSV. No action required for $dicom_file."
      else
        # If not found, move the file to the unsolvable folder
        if mv "$dicom_file" "$unsolvable_dir"; then
          log_message "Moved $dicom_file to unsolvable folder (Patient ID: $sanitized_id not found in CSV)."
        else
          log_message "Error: Failed to move $dicom_file to unsolvable folder."
        fi
      fi
    else
      log_message "Skipping $dicom_file due to missing or invalid Patient ID."
    fi

    echo "Processed DICOM file count: $file_count"  # Print a live count of processed files
  done

  log_message "Finished processing $file_count DICOM files."
}

#############################
# Start Processing
#############################

# Execute the main DICOM file processing function
process_dicom_files

# Log completion of the script execution
log_message "Script execution completed successfully."

# End of script