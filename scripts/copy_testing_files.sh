#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-07
# Revised Date: 2024-09-29  # Refactored for enhanced modularity with split directory variables
# Version: 1.4.2  # Incremented version to reflect improved modular structure and better handling
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./copy_testing_files.sh
# Example: ./scripts/copy_testing_files.sh
# Description: This script reads a list of file paths from a text file and copies them
#              to a destination directory. Each file is renamed with a counter to avoid conflicts.
#              Logs the process and ensures robustness for handling massive datasets.

set -e  # Exit immediately if any command fails for safe execution

#############################
# Directory Structure Modularity
#############################

# Define home directory and Git root
home="$HOME"
git_root="$home/Git"  # Base directory for all Git projects

# Split project directory variables into modular components
dicom_images_breast_project="dicom-images-breast"

# Subdirectory level variables (split by one level)
data_subdir="data"
logs_subdir="logs"
tests_subdir="tests"
testing_data_subdir="testing_data-pipeline_t005"

# Full path to data, logs, and tests directories using modular components
dicom_images_breast="$git_root/$dicom_images_breast_project"
dicom_images_logs="$dicom_images_breast/$data_subdir/$logs_subdir"
dicom_images_tests="$dicom_images_breast/$tests_subdir/$testing_data_subdir"

#############################
# File Variables
#############################

# Define source file containing the list of file paths
source_filename="test005.txt"
source_file="$dicom_images_logs/$source_filename"  # Full path to source file

# Define destination folder for file copying
destination_folder="$dicom_images_tests"  # Already constructed as a full path

# Log file for the current execution (timestamped)
log_filename="copy_testing_files_$(date +'%Y%m%d_%H%M%S').log"
log_file="$dicom_images_logs/$log_filename"  # Full path to log file

#############################
# Logging Function
#############################

# Function to log messages with timestamps for better tracking
# Arguments:
#   $1: The message to log
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$log_file"
}

#############################
# Pre-Execution Checks
#############################

# Log the start of the copy process with source and destination details
log_message "Starting the copy process from $source_file to $destination_folder"

# Check if the source file exists and is readable; exit with an error if not
if [ ! -f "$source_file" ]; then
  log_message "Error: Source file $source_file does not exist or is not accessible. Exiting."
  exit 1
fi

# Check if the destination folder exists; if not, create it
if [ ! -d "$destination_folder" ]; then
  log_message "Destination folder $destination_folder does not exist. Creating it..."
  mkdir -p "$destination_folder"
fi

#############################
# File Copy Function
#############################

# Initialize a counter variable for uniquely naming copied files to avoid conflicts
counter=1

# Function to copy each file, handling errors and renaming files to prevent conflicts
# Arguments:
#   $1: The full path of the file to be copied
copy_file() {
  local file_path="$1"
  
  # Trim leading and trailing whitespace from the file path (handle potential formatting issues)
  file_path="$(echo -e "${file_path}" | sed -e 's/^[[:space:]]*//;s/[[:space:]]*$//')"

  # Skip empty file paths (e.g., blank lines in the source file)
  if [ -z "$file_path" ]; then
    log_message "Warning: Empty file path found. Skipping this entry..."
    return
  fi

  # Check if the file exists before attempting to copy
  if [ -f "$file_path" ]; then
    # Extract the filename from the file path (basename strips the directory part)
    filename=$(basename "$file_path")

    # Create a new filename using the counter to avoid conflicts in the destination directory
    new_filename="file_${counter}_${filename}"

    # Attempt to copy the file to the destination with the new filename, logging success or failure
    if cp "$file_path" "$destination_folder/$new_filename"; then
      log_message "Successfully copied $filename to $destination_folder as $new_filename"
    else
      log_message "Error: Failed to copy $filename. Skipping this file."
    fi

    # Increment the counter for the next file to ensure unique naming
    ((counter++))
  else
    # Log an error if the file doesn't exist
    log_message "Error: File not found at path: $file_path. Skipping this file."
  fi
}

#############################
# File Processing Loop
#############################

# Process each line in the source file, copying each file listed
# The 'IFS=' preserves leading/trailing whitespace when reading lines
while IFS= read -r file_path; do
  copy_file "$file_path"  # Call the copy_file function for each file path
done < "$source_file"  # Redirect input from the source file

#############################
# Completion Log
#############################

# Log the completion of the copy process
log_message "File copy operation completed successfully."

# End of script