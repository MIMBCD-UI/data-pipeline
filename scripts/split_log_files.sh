#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-10
# Revised Date: 2024-09-22  # Updated to reflect improvements
# Version: 1.2  # Incremented version to reflect improvements
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./split_log_files.sh
# Example: ./script/split_log_files.sh
# Description: This script splits large .log files into smaller parts based on a maximum 
# file size and renames the split parts with a sortable numeric sequence. It captures 
# operations and errors in a log file and ensures directories exist. Adjusted for handling 
# larger datasets efficiently on macOS and Unix-based systems.

# Exit script on any command failure
set -e

# Define home directory using the system's HOME environment variable
home="$HOME"

# Directory containing .log files to process (use realpath for absolute paths)
LOG_DIR="$(realpath "$home/Git/dicom-images-breast/data/logs/toprocess")"

# Directory to save the split files (ensure it exists)
OUTPUT_DIR="$(realpath "$home/Git/dicom-images-breast/data/logs/processed")"
mkdir -p "$OUTPUT_DIR"  # Create output directory if it doesn't exist

# Log file to capture script operations and errors
LOG_FILE="$(realpath "$home/Git/dicom-images-breast/data/logs/splits/split_log_files.log")"
mkdir -p "$(dirname "$LOG_FILE")"  # Ensure the log directory exists

# Maximum file size for splitting (in bytes), e.g., "40m" for 40MB
MAX_SIZE="40m"

# Initialize or clear the log file at the start of each run
echo "Starting new splitting session: $(date)" > "$LOG_FILE"

# Function to log messages to both the terminal and the log file
# Arguments:
#   $1: The message to log
log_message() {
  echo "$1" | tee -a "$LOG_FILE"
}

# Function to handle errors gracefully
# Arguments:
#   $1: The error message to log
handle_error() {
  log_message "Error: $1"
}

# Function to split and rename log files
# Arguments:
#   $1: The full path of the log file to split
split_log_file() {
  local file="$1"
  local base_name=$(basename "$file" .log)  # Extract the base name (without .log extension)
  
  log_message "Processing file: $file"

  # Split the log file into parts of the specified size, appending an 8-character suffix
  split -b "$MAX_SIZE" -a 8 "$file" "$OUTPUT_DIR/${base_name}_"

  # Check if the split operation was successful
  if [ $? -ne 0 ]; then
    handle_error "Error splitting $file"
    return 1  # Return with error code
  fi

  local count=1  # Initialize a counter for renaming the split parts
  for part in "$OUTPUT_DIR/${base_name}_"*; do
    # Create a new filename using a numeric sequence with leading zeros (e.g., 00000001)
    local new_name="${OUTPUT_DIR}/${base_name}_$(printf "%08d" "$count").log"

    # Rename the split part to the new filename
    mv "$part" "$new_name"

    # Check if the rename operation was successful
    if [ $? -ne 0 ]; then
      handle_error "Error renaming $part to $new_name"
      return 1  # Return with error code
    fi

    log_message "Renamed $part to $new_name"
    count=$((count + 1))  # Increment the counter for the next part
  done

  return 0  # Indicate success
}

# Main loop: find all .log files in the LOG_DIR and process them
find "$LOG_DIR" -type f -name "*.log" | while read -r file; do
  # Call the function to split and rename the log file
  split_log_file "$file" || handle_error "Failed to process $file"
done

# Log the completion of the session
log_message "Splitting session completed: $(date)"

# End of script