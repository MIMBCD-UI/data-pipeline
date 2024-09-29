#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-04
# Revised Date: 2024-09-29  # Improved logging, modularity, and batch file removal for large datasets
# Version: 1.4.0  # Incremented version to reflect new improvements
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./clean_tests.sh
# Example: ./scripts/clean_tests.sh
# Description: This script removes files from specified directories, handling massive datasets. 
#              It checks for directory existence, handles permissions, and logs all actions.

set -e  # Exit immediately if a command fails for safe execution

#############################
# Directory Structure Modularity
#############################

# Define base home and git directories for modularity and reusability
home="$HOME"
git_root="$home/Git"  # Root directory for all Git projects

# Define main project directories (split by each directory level)
dataset_multimodal_breast_project="dataset-multimodal-breast"
dicom_images_breast_project="dicom-images-breast"

# Define subdirectory components
tests_subdir="tests"
dicom_subdir="dicom"
test001_subdir="test001"
test002_subdir="test002"
test003_subdir="test003"
test004_subdir="test004"
test005_subdir="test005"
data_subdir="data"
meta_subdir="meta"
logs_subdir="logs"
pre_subdir="pre"
post_subdir="post"

# Full paths constructed using the modular components
dataset_multimodal_tests="$git_root/$dataset_multimodal_breast_project/$tests_subdir"
dicom_images_data="$git_root/$dicom_images_breast_project/$data_subdir"
dicom_images_meta="$dicom_images_data/$meta_subdir"
dicom_images_logs="$dicom_images_data/$logs_subdir"
meta_pre_dir="$dicom_images_meta/$pre_subdir"
meta_post_dir="$dicom_images_meta/$post_subdir"

#############################
# Directory List for Cleaning
#############################

# Define directories that need to be cleaned, using individual variables for each directory
dir_dicom="$dataset_multimodal_tests/$dicom_subdir"
dir_test001="$dataset_multimodal_tests/$test001_subdir"
dir_test002="$dataset_multimodal_tests/$test002_subdir"
dir_test003="$dataset_multimodal_tests/$test003_subdir"
dir_test004="$dataset_multimodal_tests/$test004_subdir"
dir_test005="$dataset_multimodal_tests/$test005_subdir"
dir_meta_pre="$meta_pre_dir"
dir_meta_post="$meta_post_dir"
dir_logs="$dicom_images_logs"

# Array of directories to be processed, referencing the individual directory variables
directories=(
  "$dir_dicom"
  "$dir_test001"
  "$dir_test002"
  "$dir_test003"
  "$dir_test004"
  "$dir_test005"
  "$dir_meta_pre"
  "$dir_meta_post"
  "$dir_logs"
)

#############################
# Logging and Output
#############################

# Log file setup with a timestamp to create a unique log for each execution
log_filename="clean_tests_$(date +'%Y%m%d_%H%M%S').log"
log_file="$dicom_images_logs/$log_filename"

# Ensure the log directory exists (create it if not)
mkdir -p "$dicom_images_logs"

# Function to log messages with timestamps to both the terminal and the log file
# Arguments:
#   $1: The message to log
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$log_file"
}

#############################
# File Removal Functionality
#############################

# Function to remove files from a directory and handle errors
# Arguments:
#   $1: The directory to clean
remove_files() {
  local dir="$1"  # Directory passed as an argument

  log_message "Starting file removal process for directory: $dir"

  # Check if the directory exists
  if [ -d "$dir" ]; then
    # Attempt to remove files, handle potential errors gracefully
    if rm -f "${dir}"* 2>/dev/null; then
      log_message "Successfully removed files from $dir."
    else
      log_message "Error removing files from $dir. Checking directory permissions..."

      # Check if the directory is writable
      if [ -w "$dir" ]; then
        log_message "Write permission exists, but an error occurred while removing files from $dir."
      else
        log_message "No write permission for $dir. Please verify permissions or run the script as a different user."
      fi
    fi
  else
    # Log and skip the directory if it doesn't exist
    log_message "Directory $dir does not exist. Skipping..."
  fi
}

#############################
# Main Execution Loop
#############################

# Loop through the directories and attempt to remove files from each one
for dir in "${directories[@]}"; do
  remove_files "$dir"
done

# Final log message indicating the script has completed successfully
log_message "All specified directories have been cleaned."

# End of script