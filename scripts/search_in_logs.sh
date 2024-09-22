#!/bin/bash
#
# Author: Francisco Maria Calisto
# Created Date: 2024-04-10
# Revised Date: 2024-09-22  # Updated date to reflect revisions
# Version: 1.1  # Incremented version to reflect improvements
# Usage: ./search_in_logs.sh
# Example: ./script/search_in_logs.sh
# Description: This script searches for a specified word within .log files
# and outputs the file names and matching lines. It handles large datasets
# efficiently and ensures directories and paths are handled properly.

# Set the script to exit immediately if any command fails
set -e

# Define home directory using the system's HOME environment variable
home="$HOME"

# Directory containing the .log files to be searched (using realpath for absolute paths)
LOG_DIR="$(realpath "$home/Git/dicom-images-breast/data/logs/processed")"

# Word to search for in the log files, can be changed as needed
SEARCH_WORD="0af800"

# Ensure the log directory exists, exit if not
if [ ! -d "$LOG_DIR" ]; then
  echo "Directory does not exist: $LOG_DIR"
  exit 1
fi

# Function to log messages to the terminal
# Arguments:
#   $1: The message to log
log_message() {
  echo "$1"
}

# Function to search for the specified word in each log file
# Arguments:
#   $1: The file in which to search
#   $2: The word to search for
search_in_file() {
  local file="$1"
  local search_word="$2"

  # Log the file being processed
  log_message "Searching in $file..."

  # Search for the word in the file, showing file name and line number for matches
  # -H: Print file name
  # -n: Print line number
  grep -Hin "$search_word" "$file" | while read -r line; do
    echo "$file: $line"
  done
}

# Main loop: find all .log files in the directory and search for the specified word
log_message "Searching for '$SEARCH_WORD' in logs located at $LOG_DIR..."
find "$LOG_DIR" -type f -name "*.log" | while read -r file; do
  search_in_file "$file" "$SEARCH_WORD"
done

log_message "Search complete."

# End of script