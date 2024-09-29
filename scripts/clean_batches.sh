#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-04
# Revised Date: 2024-09-29  # Fully modular directory and file handling for large datasets
# Version: 1.5.0  # Version increment for modular structure enhancements
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./clean_batches.sh
# Example: ./scripts/clean_batches.sh
# Description: This script removes files from specified directories in batches to optimize memory usage
#              and avoid overwhelming the system, especially when dealing with large datasets.

set -e  # Exit immediately if any command fails

#############################
# Directory Structure Modularity
#############################

# Base directories (split into one level per variable for modularity)
home="$HOME"
git_root="$home/Git"

# Dataset project directories split into levels
dataset_multimodal_breast="dataset-multimodal-breast"
dicom_images_breast="dicom-images-breast"

# Tests subdirectories
tests_dir="tests"
dicom_subdir="dicom"
test001_subdir="test001"
test002_subdir="test002"
test003_subdir="test003"
test004_subdir="test004"
test005_subdir="test005"

# Data subdirectories
data_subdir="data"
meta_subdir="meta"
logs_subdir="logs"
mapping_subdir="mapping"
pre_subdir="pre"
post_subdir="post"

# Full paths constructed using the modular directory components
dataset_multimodal_tests="$git_root/$dataset_multimodal_breast/$tests_dir"
dicom_images_data="$git_root/$dicom_images_breast/$data_subdir"
dicom_images_meta="$dicom_images_data/$meta_subdir"
dicom_images_logs="$dicom_images_data/$logs_subdir"
dicom_images_mapping="$dicom_images_data/$mapping_subdir"
meta_pre_dir="$dicom_images_meta/$pre_subdir"
meta_post_dir="$dicom_images_meta/$post_subdir"

#############################
# File Handling (CSV and Logs)
#############################

# Log file (constructed using modular variables)
log_filename="clean_batches_$(date +'%Y%m%d_%H%M%S').log"
log_file="$dicom_images_logs/$log_filename"

# Ensure the log directory exists (create if necessary)
mkdir -p "$dicom_images_logs"

#############################
# Directories to Clean
#############################

# Modular directories for batch cleaning
dir_dicom="$dataset_multimodal_tests/$dicom_subdir"
dir_test001="$dataset_multimodal_tests/$test001_subdir"
dir_test002="$dataset_multimodal_tests/$test002_subdir"
dir_test003="$dataset_multimodal_tests/$test003_subdir"
dir_test004="$dataset_multimodal_tests/$test004_subdir"
dir_test005="$dataset_multimodal_tests/$test005_subdir"
dir_meta_pre="$meta_pre_dir"
dir_meta_post="$meta_post_dir"
dir_mapping="$dicom_images_mapping"
dir_logs="$dicom_images_logs"

# Directories array with individual variables
directories=(
  "$dir_dicom"
  "$dir_test001"
  "$dir_test002"
  "$dir_test003"
  "$dir_test004"
  "$dir_test005"
  "$dir_meta_pre"
  "$dir_meta_post"
  "$dir_mapping"
  "$dir_logs"
)

#############################
# Batch Size for File Removal
#############################

BATCH_SIZE=100  # Define the number of files to delete in each batch

#############################
# Logging Function
#############################

# Function to log messages with timestamps
# Arguments:
#   $1: The message to log
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$log_file"
}

#############################
# Batch File Removal Function
#############################

# Function to remove files in batches from a directory
# Arguments:
#   $1: The directory from which to remove files
remove_files_in_batches() {
  local dir="$1"  # The directory to process

  log_message "Starting file removal in batches from $dir"

  # Check if the directory exists, log and skip if not
  if [ ! -d "$dir" ]; then
    log_message "Directory $dir does not exist. Skipping..."
    return  # Exit if the directory doesn't exist
  fi

  # Get and log the initial file count in the directory
  local file_count
  file_count=$(find "$dir" -type f | wc -l)
  log_message "Initial file count in $dir: $file_count"

  # Ensure there are files to delete before proceeding
  if [ "$file_count" -eq 0 ]; then
    log_message "No files to delete in $dir. Skipping..."
    return  # Exit if no files are found
  fi

  # Perform batch removal using xargs and log progress
  log_message "Removing files in batches of $BATCH_SIZE..."
  find "$dir" -type f -print0 | xargs -0 -n "$BATCH_SIZE" rm -f

  # Log the remaining file count after removal
  file_count=$(find "$dir" -type f | wc -l)
  log_message "File count after removal in $dir: $file_count"
}

#############################
# Main Execution Loop
#############################

# Iterate through each directory in the directories array and remove files in batches
for dir in "${directories[@]}"; do
  remove_files_in_batches "$dir"
done

# Final log message indicating successful script completion
log_message "File removal completed for all specified directories."

# End of script