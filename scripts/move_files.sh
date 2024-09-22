#!/bin/bash
#
# Author: Francisco Maria Calisto
# Created Date: 2024-09-22
# Revised Date: 2024-09-23
# Version: 1.1
# Usage: ./move_files.sh
# Example: ./scripts/move_files.sh
# Description: This script moves files from the unexplored folder to the checking folder 
# inside the dataset-multimodal-breast repository. This version improves path handling, 
# adds more robust error checking, and provides clearer feedback during execution.
# This script is compatible with macOS systems and uses absolute paths for robustness.

# Set the script to exit immediately if any command fails
set -e

# Define home directory using the system's HOME environment variable
home="$HOME"

# Resolve the absolute paths for source and destination directories
SRC_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/curation/unexplored")"
DEST_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/curation/checking")"

# Function to print error messages to stderr
function print_error {
  echo "$1" >&2
}

# Function to validate that a directory exists
validate_directory() {
  local dir_path="$1"  # The directory to check
  local dir_name="$2"  # Friendly name for the directory (e.g., "Source", "Destination")

  # Check if the directory exists and is a valid directory
  if [ ! -d "$dir_path" ]; then
    print_error "$dir_name directory $dir_path does not exist. Exiting."
    exit 1
  fi
}

# Function to move files from the source directory to the destination
move_files() {
  local src="$1"  # Source directory
  local dest="$2" # Destination directory

  echo "Attempting to move files from $src to $dest..."

  # Loop through each file in the source directory
  for file in "$src"/*; do
    # Check if the current item is a file (not a directory)
    if [ -f "$file" ]; then
      echo "Moving $file to $dest"
      mv "$file" "$dest"
    else
      echo "No files to move from $src"  # Output if no files are found
      break
    fi
  done
}

# Function to check if the last operation was successful
check_move_success() {
  # If the previous command (move) was successful
  if [ $? -eq 0 ]; then
    echo "Files moved successfully."
  else
    print_error "An error occurred while moving files."
    exit 1
  fi
}

# Begin the script execution with directory validations
validate_directory "$SRC_DIR" "Source"
validate_directory "$DEST_DIR" "Destination"

# Perform the file move operation
move_files "$SRC_DIR" "$DEST_DIR"

# Check if the files were moved successfully
check_move_success

# Completion message
echo "Operation complete."

# End of script