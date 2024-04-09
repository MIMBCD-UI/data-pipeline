#!/bin/bash
#
# Author: Francisco Maria Calisto
# Created Date: 2024-04-04
# Revised Date: 2024-04-09
# Usage: ./clean_tests.sh
# Example: ./script/clean_tests.sh
# Description: This script is used to clear all files in the specified directories

# Define home directory
home="$HOME"

# Define base directories relative to the home directory
dataset_multimodal_breast="$home/Git/dataset-multimodal-breast"
dicom_images_breast="$home/Git/dicom-images-breast"

# Define directories to clear
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

# Function to remove files from a directory and handle permission errors
remove_files() {
  local dir="$1"
  echo "Removing all files in $dir"
  if [ -d "$dir" ]; then
    if rm -f "${dir}"* 2>/dev/null; then
      echo "Files in $dir removed successfully"
    else
      echo "Failed to remove files in $dir. Checking permissions..."
      if [ -w "$dir" ]; then
        echo "You have write permission for $dir, but there was an error removing files."
      else
        echo "You do not have write permission for $dir. Please check permissions."
      fi
    fi
  else
    echo "$dir does not exist."
  fi
}

# Loop through each directory and remove its contents
for dir in "${directories[@]}"; do
  remove_files "$dir"
done

echo "All specified directories have been cleared."

# End of script