#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-04
# Revised Date: 2024-09-22  # Updated to reflect optimizations and improvements
# Version: 1.1  # Incremented version to reflect the additional changes
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./clean_batches.sh
# Example: ./script/clean_batches.sh
# Description: This script clears files in specified directories by removing them in batches.
# It's optimized for directories containing a large number of files by batching removals to minimize
# memory usage and ensure efficient file handling, especially for systems under heavy load.

# Exit the script if any command fails to ensure safe execution
set -e

# Define the home directory using the system's HOME environment variable
home="$HOME"

# Define base directories relative to the home directory using absolute paths for consistency
dataset_multimodal_breast="$home/Git/dataset-multimodal-breast"
dicom_images_breast="$home/Git/dicom-images-breast"

# Define the directories to clear; these are paths where files will be deleted in batches
directories=(
  "$dataset_multimodal_breast/tests/dicom/"
  "$dataset_multimodal_breast/tests/test001/"
  "$dataset_multimodal_breast/tests/test002/"
  "$dataset_multimodal_breast/tests/test003/"
  "$dataset_multimodal_breast/tests/test004/"
  "$dataset_multimodal_breast/tests/test005/"
  "$dicom_images_breast/data/meta/pre/"
  "$dicom_images_breast/data/meta/post/"
  "$dicom_images_breast/data/mapping/"
  "$dicom_images_breast/data/logs/"
)

# Function to remove files from a directory in batches
# Arguments:
#   $1: Directory from which to remove files in batches
remove_files_in_batches() {
  local dir="$1"  # Directory path passed as an argument

  # Log the directory being processed
  echo "Starting batch removal in $dir"

  # Check if the directory exists before proceeding
  if [ ! -d "$dir" ]; then
    echo "Directory $dir does not exist. Skipping..."
    return
  fi

  # Count and log the number of files before removal
  local file_count
  file_count=$(find "$dir" -type f | wc -l)
  echo "Number of files in $dir before removal: $file_count"

  # Use find with -print0 and xargs -0 to efficiently handle many files (including files with special characters)
  # The -n100 option processes files in batches of 100 to optimize memory usage and performance
  echo "Removing files in batches of 100..."
  find "$dir" -type f -print0 | xargs -0 -n100 rm -f

  # Count and log the number of files after removal
  file_count=$(find "$dir" -type f | wc -l)
  echo "Number of files in $dir after removal: $file_count"
}

# Loop through the array of directories and remove files from each in batches
for dir in "${directories[@]}"; do
  remove_files_in_batches "$dir"
done

# Final log message indicating the script has completed its work
echo "All specified directories have been cleared."

# End of script