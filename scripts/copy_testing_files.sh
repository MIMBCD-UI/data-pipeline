#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-07
# Revised Date: 2024-09-22  # Updated to reflect improvements
# Version: 1.3  # Incremented version to reflect further optimizations
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./copy_testing_files.sh
# Example: ./script/copy_testing_files.sh
# Description: This script reads a list of file paths from a text file and copies them
# to a destination directory. Each file is renamed using a counter to avoid name conflicts.
# The script includes error handling, path management, and logging.

# Exit immediately if any command fails to ensure safe execution
set -e

# Define the home directory using the system's HOME environment variable
home="$HOME"

# Define the source file containing the list of file paths (using realpath for robustness)
# 'realpath' ensures that paths are absolute, avoiding issues when running the script from different directories.
source_file="$(realpath "$home/Git/dicom-images-breast/data/logs/test005.txt")"

# Define the destination folder where the files will be copied (also using realpath for consistency)
destination_folder="$(realpath "$home/Git/dicom-images-breast/tests/testing_data-pipeline_t005/")"

# Log a message indicating the source file and destination folder to provide feedback to the user
echo "Starting the copy process. Copying files from $source_file to $destination_folder"

# Check if the source file exists; if not, exit with an error message
if [ ! -f "$source_file" ]; then
  echo "Error: Source file $source_file does not exist. Exiting."
  exit 1
fi

# Check if the destination folder exists, and create it if it doesn't
if [ ! -d "$destination_folder" ]; then
  echo "Destination folder $destination_folder does not exist. Creating it..."
  mkdir -p "$destination_folder"
fi

# Initialize a counter variable for uniquely naming copied files to prevent conflicts
counter=1

# Function to handle the copying of each file
# Arguments:
#   $1: The full path of the file to copy
copy_file() {
  local file_path="$1"
  
  # Trim leading and trailing whitespace from the file path
  file_path="$(echo -e "${file_path}" | sed -e 's/^[[:space:]]*//;s/[[:space:]]*$//')"

  # Skip if the file path is empty (for example, a blank line in the source file)
  if [ -z "$file_path" ]; then
    echo "Warning: Empty file path found, skipping..."
    return
  fi

  # Check if the file exists before attempting to copy it
  if [ -f "$file_path" ]; then
    # Extract the filename from the file path
    filename=$(basename "$file_path")

    # Construct a new filename using the counter to avoid conflicts in the destination
    new_filename="file_${counter}_${filename}"

    # Copy the file to the destination folder with the new filename
    cp "$file_path" "$destination_folder/$new_filename"

    # Log the successful copy action
    echo "Successfully copied $filename to $destination_folder as $new_filename"

    # Increment the counter for the next file
    ((counter++))
  else
    # Log an error message if the file is not found
    echo "Error: File not found: $file_path. Skipping this file."
  fi
}

# Read the source file line by line, copying each file listed in the source file
# The 'IFS=' ensures that leading/trailing whitespace is preserved when reading lines.
while IFS= read -r file_path; do
  copy_file "$file_path"
done < "$source_file"  # Redirect input from the source file

# Log the completion of the file copy operation
echo "File copy operation completed successfully."

# End of script