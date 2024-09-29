#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-22
# Revised Date: 2024-09-29  # Added enhanced file processing, logging, and error handling
# Version: 1.3.0  # Incremented version to reflect new optimizations and logging improvements
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./move_back_to_unexplored.sh
# Example: ./scripts/move_back_to_unexplored.sh
# Description: This script moves a limited number of DICOM files from the "checking" folder 
# to the "unexplored" folder. It includes error handling, logging, and batch file processing 
# for large datasets with a configurable file limit.

set -e  # Exit the script immediately if any command fails

#############################
# Configuration: Directories and File Limit
#############################

# Define the home directory using the system's HOME environment variable
home="$HOME"

# Define the file limit: The maximum number of files to move in one run (configurable)
FILE_LIMIT=10  # You can adjust this value for different batch sizes

# Define the source and destination directories, modularly split into levels for flexibility
git_dir="$home/Git"                               # Root Git directory
project_name="dataset-multimodal-breast"          # Project name
project_dir="$git_dir/$project_name"              # Project directory

data_name="data"                                  # Data folder name
curation_name="curation"                          # Curation folder name
checking_name="checking"                          # Checking subfolder name
unexplored_name="unexplored"                      # Unexplored subfolder name
logs_name="logs"                                  # Logs folder name

# Build full paths for the source, destination, and log directories
src_dir="$(realpath "$project_dir/$data_name/$curation_name/$checking_name")"  # Source: "checking"
dest_dir="$(realpath "$project_dir/$data_name/$curation_name/$unexplored_name")"  # Destination: "unexplored"
log_dir="$(realpath "$project_dir/$data_name/$curation_name/$logs_name")"      # Logs directory

#############################
# Logging Setup
#############################

# Ensure the logs directory exists, create it if necessary
mkdir -p "$log_dir"

# Create a timestamped log file to avoid overwriting previous logs
log_filename="move_back_$(date +'%Y%m%d_%H%M%S').log"
log_file="$log_dir/$log_filename"

# Function to log messages with timestamps to both terminal and log file
# Arguments:
#   $1: The message to log
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$log_file"
}

#############################
# Directory Validation Function
#############################

# Function to validate if a directory exists
# Arguments:
#   $1: Directory path to validate
#   $2: Friendly name for logging purposes
validate_directory() {
  local dir="$1"
  local dir_name="$2"
  
  # Check if the directory exists, if not, log an error and exit
  if [ ! -d "$dir" ]; then
    log_message "Error: $dir_name directory ($dir) does not exist. Exiting."
    exit 1
  fi
}

#############################
# File Moving Function
#############################

# Function to move DICOM files from the source to the destination directory, respecting the file limit
# Arguments:
#   $1: Source directory
#   $2: Destination directory
#   $3: File limit
move_files() {
  local src="$1"
  local dest="$2"
  local limit="$3"
  local count=0  # Counter to track how many files have been moved

  log_message "Moving up to $limit DICOM files from $src to $dest..."

  # Use 'find' to locate DICOM files (with .dcm extension) and process up to the specified file limit
  find "$src" -type f -name "*.dcm" | while IFS= read -r file; do
    if [ -f "$file" ] && (( count < limit )); then
      mv "$file" "$dest"  # Move the file to the destination
      log_message "Moved file: $file"
      ((count++))  # Increment the counter after each file is moved
    fi
  done

  log_message "Moved $count DICOM file(s) from $src to $dest."
}

#############################
# Script Execution: Main Process
#############################

# Validate that both the source and destination directories exist
validate_directory "$src_dir" "Checking"
validate_directory "$dest_dir" "Unexplored"

# Move the files, respecting the specified file limit
move_files "$src_dir" "$dest_dir" "$FILE_LIMIT"

# Final log message indicating the script completed successfully
log_message "File move operation completed successfully. Logs are saved to $log_file."

# End of script