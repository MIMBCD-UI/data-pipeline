#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-10
# Revised Date: 2024-09-29  # Updated version and optimizations for large datasets and detailed logging
# Version: 1.2.0  # Incremented version to reflect improvements and optimizations
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./search_in_logs.sh
# Example: ./scripts/search_in_logs.sh
# Description: This script searches for a specified word within .log files located
#              in a specified directory. It logs each step, handles large datasets,
#              and ensures all directories and paths are handled properly.

set -e  # Exit the script immediately if any command fails

#############################
# Configuration
#############################

# Define home directory using the system's HOME environment variable
home="$HOME"

# Directory structure: split each directory level into separate variables for modularity
git_folder="Git"
project_folder="dicom-images-breast"
data_folder="data"
logs_folder="logs"
processed_folder="processed"

# Construct the full path to the log directory using the directory variables
LOG_DIR="$home/$git_folder/$project_folder/$data_folder/$logs_folder/$processed_folder"

# Define the word to search for in the log files
SEARCH_WORD="0af800"  # This can be modified to search for different words

# Log file to record the script's execution (includes a timestamp to avoid overwrites)
log_filename="search_logs_$(date +'%Y%m%d_%H%M%S').log"
log_filepath="$LOG_DIR/$log_filename"

#############################
# Logging Function
#############################

# Function to log messages to both the terminal and a log file
# Arguments:
#   $1: The message to log
log_message() {
  local message="$1"
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $message" | tee -a "$log_filepath"
}

#############################
# Validation Function
#############################

# Function to ensure the specified directory exists
# Arguments:
#   $1: The directory path to validate
validate_directory() {
  local dir="$1"
  if [ ! -d "$dir" ]; then
    log_message "Error: Directory does not exist: $dir"
    exit 1
  else
    log_message "Directory exists: $dir"
  fi
}

# Validate that the log directory exists before proceeding
validate_directory "$LOG_DIR"

#############################
# Search Function
#############################

# Function to search for the specified word in each log file
# Arguments:
#   $1: The file in which to search
#   $2: The word to search for
search_in_file() {
  local file="$1"
  local search_word="$2"

  log_message "Searching for '$search_word' in $file..."

  # Search for the word in the file, showing file name, line number, and matching content
  # -H: Print file name
  # -n: Print line number
  grep -Hin "$search_word" "$file" | while read -r line; do
    # Output both the file name and the line that matches the search term
    echo "$file: $line"
  done
}

#############################
# Main Script Execution
#############################

log_message "Starting search for the word '$SEARCH_WORD' in logs located at $LOG_DIR..."

# Find all .log files in the specified directory and search for the word in each file
find "$LOG_DIR" -type f -name "*.log" | while read -r log_file; do
  search_in_file "$log_file" "$SEARCH_WORD"
done

log_message "Search complete. Results logged to $log_filepath."

# End of script