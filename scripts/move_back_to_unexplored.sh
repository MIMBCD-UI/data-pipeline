#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-22
# Revised Date: 2024-09-22  # Updated to reflect file limit via variable
# Version: 1.2  # Incremented version to reflect changes for variable-based file limit
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./move_back_to_unexplored.sh
# Example: ./script/move_back_to_unexplored.sh
# Description: This script moves a limited number of DICOM files from the "checking" folder 
# to the "unexplored" folder in the dataset-multimodal-breast repository. It includes error 
# handling, logging, and batch file processing with a configurable file limit.

# Exit script on any command failure to ensure safe execution
set -e

# Define the home directory using the system's HOME environment variable
home="$HOME"

# Define the file limit for the number of DICOM files to move
FILE_LIMIT=10  # You can adjust this value to change the file limit

# Define source and destination directories (using realpath for absolute paths)
SRC_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/curation/checking")"
DEST_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/curation/unexplored")"
LOG_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/curation/logs")"

# Ensure the logs directory exists, create it if necessary
if [ ! -d "$LOG_DIR" ]; then
  mkdir -p "$LOG_DIR"
fi

# Create a timestamp for the log file to avoid overwriting previous logs
LOG_FILE="$LOG_DIR/move_back_$(date +'%Y%m%d_%H%M%S').log"

# Function to log messages to both the terminal and log file
log_message() {
  echo "$1" | tee -a "$LOG_FILE"
}

# Function to validate directory existence
# Arguments:
#   $1: Directory path to validate
#   $2: Directory name for logging purposes
validate_directory() {
  local dir="$1"
  local dir_name="$2"

  if [ ! -d "$dir" ]; then
    log_message "Error: $dir_name directory $dir does not exist. Exiting."
    exit 1
  fi
}

# Function to move DICOM files from source to destination, respecting the file limit
# Arguments:
#   $1: Source directory
#   $2: Destination directory
#   $3: File limit
move_files() {
  local src="$1"
  local dest="$2"
  local limit="$3"
  local count=0

  log_message "Moving up to $limit DICOM files from $src to $dest..."

  # Find and move only DICOM files (.dcm extension), limit to the specified number
  find "$src" -type f -name "*.dcm" | while IFS= read -r file; do
    if [ -f "$file" ] && (( count < limit )); then
      mv "$file" "$dest"
      log_message "$(date): Moved $file"
      ((count++))
    fi
  done

  log_message "Moved $count DICOM files from $src to $dest."
}

# Main execution begins here

# Validate that both source and destination directories exist
validate_directory "$SRC_DIR" "Checking"
validate_directory "$DEST_DIR" "Unexplored"

# Move DICOM files from the "checking" folder to the "unexplored" folder, respecting the file limit
move_files "$SRC_DIR" "$DEST_DIR" "$FILE_LIMIT"

# Log completion message
log_message "File move operation completed successfully. Logs are saved to $LOG_FILE."

# End of script