#!/bin/bash
#
# Author: Francisco Maria Calisto
# Created Date: 2024-04-04
# Revised Date: 2024-04-09
# Usage: ./clean_batches.sh
# Example: ./script/clean_batches.sh
# Description: This script efficiently clears files in specified
# directories by removing them in batches, optimized for
# directories with a very large number of files.

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

# Function to remove files from a directory in batches
remove_files_in_batches() {
  local dir="$1"
  echo "Starting batch removal in $dir"
  
  if [ ! -d "$dir" ]; then
    echo "$dir does not exist."
    return
  fi
  
  # Count files before removal
  file_count=$(find "$dir" -type f | wc -l)
  echo "Number of files in $dir before removal: $file_count"
  
  # Use find with -print0 and xargs -0 to efficiently handle many files, including those with special characters
  echo "Removing files in batches of 100..."
  find "$dir" -type f -print0 | xargs -0 -n100 rm -f
  
  # Count files after removal
  file_count=$(find "$dir" -type f | wc -l)
  echo "Number of files in $dir after removal: $file_count"
  
  # The -n100 option with xargs processes files in batches of 100 to keep memory usage low
}

# Loop through each directory and remove its contents in batches
for dir in "${directories[@]}"; do
  remove_files_in_batches "$dir"
done

echo "All specified directories have been cleared."

# End of script