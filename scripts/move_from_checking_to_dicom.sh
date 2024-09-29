#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-29
# Revised Date: 2024-09-29  # Enhanced batch processing, modular directory setup, and logging for large datasets.
# Version: 1.2.3
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./move_from_checking_to_dicom.sh
# Description: This script moves all files from the "checking" folder to the "dicom" folder in batches
#              to handle massive datasets efficiently without overwhelming the system.

set -e  # Exit script on any error

#############################
# Configuration and Setup
#############################

# Define user's home directory and base project directories
home="$HOME"                         # Home directory
git_dir="$home/Git"                  # Git projects root
project_dir="$git_dir/dataset-multimodal-breast"  # Main project directory
data_dir="$project_dir/data"         # Data directory

# Define directories for curation, checking, and dicom
curation_dir="$data_dir/curation"    # Curation folder where files are processed
checking_dir="$curation_dir/checking"  # Source directory for DICOM files to move
dicom_dir="$data_dir/dicom"          # Destination directory for DICOM files

# Log directory and file setup
logs_dir="$curation_dir/logs"                    # Directory for logs
log_filename="move_from_checking_to_dicom_$(date +'%Y%m%d_%H%M%S').log"  # Log filename with timestamp
log_file="$logs_dir/$log_filename"               # Full path to log file

# Ensure the log and dicom directories exist (create them if necessary)
mkdir -p "$logs_dir" "$dicom_dir"

# Define batch size: the number of files to move at a time to avoid overloading the system
BATCH_SIZE=500  # Adjust based on your system's performance

#############################
# Logging Function
#############################

# Function to log messages with timestamps to both console and log file
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$log_file"
}

#############################
# Validation Functions
#############################

# Function to validate if a directory exists
# Arguments:
#   $1: Path to validate
#   $2: Human-readable description of the path for error messages
validate_path() {
  if [ ! -e "$1" ]; then
    log_message "Error: $2 ($1) does not exist. Exiting."
    exit 1  # Exit if the directory does not exist to avoid further issues
  else
    log_message "$2 exists: $1"
  fi
}

# Ensure required directories exist before processing
validate_path "$checking_dir" "Checking folder (source of DICOM files)"
validate_path "$dicom_dir" "DICOM folder (destination)"

#############################
# Batch File Moving Function
#############################

# Function to move DICOM files from checking to dicom folder in batches
# Moves up to $BATCH_SIZE files at a time and logs progress
move_files_in_batches() {
  local count=0  # Initialize counter for moved files
  log_message "Starting to move files from '$checking_dir' to '$dicom_dir' in batches of $BATCH_SIZE..."

  # Find all DICOM files in the checking directory and process them in batches
  find "$checking_dir" -type f -name "*.dcm" | while IFS= read -r file; do
    # Try to move each file and log success or failure
    if mv "$file" "$dicom_dir"; then
      log_message "Moved file: $file"
      count=$((count + 1))  # Increment file counter

      # Pause after moving a batch to reduce system load
      if (( count % BATCH_SIZE == 0 )); then
        log_message "Moved $count files so far. Pausing briefly to avoid overloading the system..."
        sleep 2  # Pause to give the system time to recover between batches
      fi
    else
      log_message "Error: Failed to move file: $file"  # Log any errors during the move process
    fi
  done

  # Log final count of moved files
  log_message "Finished moving $count files from '$checking_dir' to '$dicom_dir'."
}

#############################
# Main Script Execution
#############################

# Start the file moving process in batches
move_files_in_batches

# Log completion of the script execution
log_message "Script execution completed successfully. All files moved."

# End of script