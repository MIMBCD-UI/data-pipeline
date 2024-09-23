#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-04
# Revised Date: 2024-09-22  # Updated to reflect improvements
# Version: 1.2  # Incremented version to reflect further optimizations
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./clean_tests.sh
# Example: ./script/clean_tests.sh
# Description: This script clears all files from specified test and data directories.
# It checks for directory existence, file removal permissions, and reports any errors.

# Exit the script if any command fails to ensure safe execution
set -e

# Define the home directory using the system's HOME environment variable
home="$HOME"

# Define base directories relative to the home directory using absolute paths for consistency
dataset_multimodal_breast="$home/Git/dataset-multimodal-breast"
dicom_images_breast="$home/Git/dicom-images-breast"

# Define an array of directories to clear; these are paths where files will be deleted
directories=(
  "$dataset_multimodal_breast/tests/dicom/"
  "$dataset_multimodal_breast/tests/test001/"
  "$dataset_multimodal_breast/tests/test002/"
  "$dataset_multimodal_breast/tests/test003/"
  "$dataset_multimodal_breast/tests/test004/"
  "$dataset_multimodal_breast/tests/test005/"
  "$dicom_images_breast/data/meta/pre/"
  "$dicom_images_breast/data/meta/post/"
  "$dicom_images_breast/data/logs/"
)

# Function to remove files from a directory and handle permission errors
# Arguments:
#   $1: Directory from which to remove all files
remove_files() {
  local dir="$1"  # Directory path passed as argument

  # Log the directory being processed
  echo "Attempting to remove all files in $dir..."

  # Check if the directory exists
  if [ -d "$dir" ]; then
    # Try to remove files from the directory, suppressing error messages if none exist
    if rm -f "${dir}"* 2>/dev/null; then
      echo "Files in $dir removed successfully."
    else
      echo "Error removing files from $dir. Checking permissions..."

      # Check if the directory is writable
      if [ -w "$dir" ]; then
        echo "You have write permissions for $dir, but there was an error removing files."
      else
        echo "No write permission for $dir. Please check permissions or run the script as a user with the appropriate permissions."
      fi
    fi
  else
    # Log a message if the directory does not exist
    echo "Directory $dir does not exist. Skipping..."
  fi
}

# Loop through the array of directories and attempt to remove all files from each
for dir in "${directories[@]}"; do
  remove_files "$dir"
done

# Final log message indicating the script has completed its work
echo "All specified directories have been processed and cleaned."

# End of script