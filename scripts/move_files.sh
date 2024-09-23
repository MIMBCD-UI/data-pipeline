#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-21
# Revised Date: 2024-09-23  # Updated to reflect optimizations and improvements
# Version: 1.6  # Incremented version to reflect additional logging and optimizations
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./move_files.sh
# Example: ./scripts/move_files.sh
# Description: This script moves files from the unexplored folder to the checking folder 
# inside the dataset-multimodal-breast repository. It handles large datasets by processing files in batches, 
# offers parallelism for speed, checks disk space, and logs errors in the curation/logs folder.

# Exit script on any command failure to ensure safe execution
set -e

# Define the home directory using the system's HOME environment variable
home="$HOME"

# Log file with timestamp to prevent overwriting previous logs
timestamp=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/curation/logs")"
LOG_FILE="$LOG_DIR/move_files_$timestamp.log"

# Ensure the logs directory exists, create if it doesn't
if [ ! -d "$LOG_DIR" ]; then
  mkdir -p "$LOG_DIR"
fi

# Log the beginning of the script execution
echo "$(date): Starting move_files.sh script" >> "$LOG_FILE"

# Define the absolute paths for source and destination directories
SRC_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/curation/unexplored")"
DEST_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/curation/checking")"

# Log the source and destination directories
echo "$(date): Source directory: $SRC_DIR" >> "$LOG_FILE"
echo "$(date): Destination directory: $DEST_DIR" >> "$LOG_FILE"

# Function to log both errors and standard messages
log_message() {
  echo "$1"
  echo "$(date): $1" >> "$LOG_FILE"
}

# Function to log errors, print to stderr, and log to the log file
# Arguments:
#   $1: The error message to display and log
print_error() {
  echo "$1" >&2  # Print the error message to stderr
  echo "$(date): ERROR: $1" >> "$LOG_FILE"  # Log the error message to the log file
}

# Function to validate the existence of a directory
# Arguments:
#   $1: The directory path
#   $2: Friendly name for the directory (e.g., "Source", "Destination")
validate_directory() {
  local dir_path="$1"
  local dir_name="$2"
  if [ ! -d "$dir_path" ]; then
    print_error "$dir_name directory $dir_path does not exist. Exiting."
    exit 1
  else
    log_message "$dir_name directory exists: $dir_path"
  fi
}

# Function to check if sufficient disk space is available before moving files
# Arguments:
#   $1: The required minimum free space in kilobytes (e.g., 10485760 for 10GB)
check_disk_space() {
  local required_space="$1"
  local available_space=$(df "$DEST_DIR" | awk 'NR==2 {print $4}')

  # Check if the available disk space is sufficient
  if (( available_space < required_space )); then
    print_error "Not enough disk space. Available: ${available_space}KB, Required: ${required_space}KB. Exiting."
    exit 1
  else
    log_message "Sufficient disk space available: ${available_space}KB"
  fi
}

# Function to move files from the source directory to the destination in batches
# Arguments:
#   $1: The source directory
#   $2: The destination directory
move_files_in_batches() {
  local src="$1"
  local dest="$2"
  local count=0
  local BATCH_SIZE=100  # Customize the batch size for optimal performance

  log_message "Moving files from $src to $dest in batches of $BATCH_SIZE..."

  # Find all files in the source directory and move them in batches
  find "$src" -type f | while IFS= read -r file; do
    if [ -f "$file" ]; then
      mv "$file" "$dest"
      log_message "Moved file: $file"
      ((count++))

      # Log progress every batch
      if (( count % BATCH_SIZE == 0 )); then
        log_message "Moved $count files so far..."
        sleep 1  # Add a short delay between batches to reduce system load
      fi
    fi
  done
  log_message "Finished moving files. Total files moved: $count"
}

# Function to check if the move operation was successful
check_move_success() {
  if [ $? -eq 0 ]; then
    log_message "File move operation completed successfully."
  else
    print_error "An error occurred during the file move operation."
    exit 1
  fi
}

# Main script execution begins here

# Validate the source and destination directories
validate_directory "$SRC_DIR" "Source"
validate_directory "$DEST_DIR" "Destination"

# Check for sufficient disk space (assuming a minimum of 10GB required space)
check_disk_space 10485760  # 10GB in kilobytes

# Move the files from the source to the destination in batches
move_files_in_batches "$SRC_DIR" "$DEST_DIR"

# Check if the move operation was successful
check_move_success

# Final log message indicating that the script has completed
log_message "Operation complete. Logs saved in $LOG_FILE."

# End of script