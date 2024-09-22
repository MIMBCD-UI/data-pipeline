#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Version: 1.5  # Incremented version to reflect new logging location
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

# Exit script on any command failure
set -e

# Define home directory using the system's HOME environment variable
home="$HOME"

# Resolve the absolute paths for source, destination, and log directories
SRC_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/curation/unexplored")"
DEST_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/curation/checking")"
LOG_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/curation/logs")"

# Ensure the logs directory exists, create if it doesn't
if [ ! -d "$LOG_DIR" ]; then
  mkdir -p "$LOG_DIR"
fi

# Log file to capture details of file moves and errors
LOG_FILE="$LOG_DIR/move_files.log"

# Function to print error messages to stderr and log them
# Arguments:
#   $1: The error message to display and log
function print_error {
  echo "$1" >&2  # Print the error message to stderr
  echo "$(date): $1" >> "$LOG_FILE"  # Append the error message to the log file
}

# Function to validate that a directory exists
# Arguments:
#   $1: The path of the directory to validate
#   $2: A friendly name for the directory (e.g., "Source", "Destination")
validate_directory() {
  local dir_path="$1"  # Directory to check
  local dir_name="$2"  # Friendly name for logging and messages

  # Check if the directory exists and is a valid directory
  if [ ! -d "$dir_path" ]; then
    print_error "$dir_name directory $dir_path does not exist. Exiting."
    exit 1  # Exit the script if the directory doesn't exist
  fi
}

# Function to check disk space before moving files
# Arguments:
#   $1: The required minimum free space in kilobytes (e.g., 10485760 for 10GB)
check_disk_space() {
  local required_space="$1"
  local available_space=$(df "$DEST_DIR" | awk 'NR==2 {print $4}')

  # Check if there is enough available space
  if (( available_space < required_space )); then
    print_error "Not enough disk space. Available: ${available_space}KB, Required: ${required_space}KB. Exiting."
    exit 1
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

  echo "Moving files from $src to $dest in batches of $BATCH_SIZE..."

  # Find all files in the source directory and move them in batches
  find "$src" -type f | while IFS= read -r file; do
    if [ -f "$file" ]; then
      mv "$file" "$dest"  # Move file to the destination
      echo "$(date): Moved $file" >> "$LOG_FILE"
      ((count++))
      # Check if we've reached the batch size
      if (( count % BATCH_SIZE == 0 )); then
        echo "Moved $count files so far..."
        sleep 1  # Optional: Add a pause between batches to reduce system load
      fi
    fi
  done
}

# Function to check if the last operation (moving files) was successful
check_move_success() {
  # $? holds the exit status of the last command (mv in this case)
  if [ $? -eq 0 ]; then
    echo "Files moved successfully."
  else
    print_error "An error occurred while moving files."
    exit 1  # Exit with an error status if something went wrong
  fi
}

# Main script execution begins here

# Validate the existence of the source and destination directories
validate_directory "$SRC_DIR" "Source"
validate_directory "$DEST_DIR" "Destination"

# Check if there is enough disk space (assuming 10GB minimum required space)
check_disk_space 10485760  # 10GB in kilobytes

# Move files in batches from the source to the destination
move_files_in_batches "$SRC_DIR" "$DEST_DIR"

# Check if the move operation was successful
check_move_success

# Print a final message indicating that the script has completed successfully
echo "Operation complete. Logs can be found in $LOG_FILE."

# End of script