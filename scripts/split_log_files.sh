#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-10
# Revised Date: 2024-09-29  # Modularized log_file variable by splitting directory levels
# Version: 1.3.3  # Incremented version to reflect directory splitting for the log variable
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./split_log_files.sh
# Example: ./scripts/split_log_files.sh
# Description: This script splits large .log files into smaller parts based on a maximum 
#              file size and renames split parts with a sortable numeric sequence. It captures
#              operations and errors in a log file, ensuring directories exist. Optimized for
#              large datasets on Unix-based systems.

set -e  # Exit script on any command failure

#############################
# Directory and File Setup
#############################

# Modularize the directory levels for both source and output directories

home="$HOME"                                # Home directory
git_dir="Git"                               # Git directory level
project_dir="dicom-images-breast"           # Project directory
data_dir="data"                             # Data folder inside project
logs_dir="logs"                             # Logs folder inside data

toprocess_dir="toprocess"                   # Subfolder for logs to process
processed_dir="processed"                   # Subfolder for processed/split logs
splits_dir="splits"                         # Subfolder for storing log files from the script itself

# Build full paths from the modular directory components
LOG_DIR="$home/$git_dir/$project_dir/$data_dir/$logs_dir/$toprocess_dir"      # Directory with log files to be processed
OUTPUT_DIR="$home/$git_dir/$project_dir/$data_dir/$logs_dir/$processed_dir"   # Directory for split log files
SPLIT_LOG_DIR="$home/$git_dir/$project_dir/$data_dir/$logs_dir/$splits_dir"   # Directory for the script's own log file

# Ensure output and log directories exist
mkdir -p "$OUTPUT_DIR" "$SPLIT_LOG_DIR"

# Modularize the log file path by splitting the filename
timestamp=$(date +"%Y%m%d_%H%M%S")      # Generate timestamp for the log file
log_filename="split_log_files_$timestamp.log"  # Log file name with timestamp
log_file="$SPLIT_LOG_DIR/$log_filename"       # Full path to the log file using modular components

# Maximum file size for splitting (e.g., "40m" for 40MB)
MAX_SIZE="40m"

# Initialize the log file with a session start message
echo "Starting new splitting session: $(date)" > "$log_file"

#############################
# Logging and Error Handling
#############################

# Function to log messages to both the terminal and the log file
# Arguments:
#   $1: The message to log
log_message() {
  local message="$1"
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $message" | tee -a "$log_file"
}

# Function to handle errors and log them
# Arguments:
#   $1: The error message to log
handle_error() {
  log_message "Error: $1"
  exit 1  # Exit the script immediately on error
}

#############################
# File Splitting Function
#############################

# Function to split and rename log files
# Arguments:
#   $1: The full path of the log file to split
split_log_file() {
  local file="$1"
  local base_name=$(basename "$file" .log)  # Extract base file name without .log extension

  log_message "Processing file: $file"

  # Split the log file into parts of the specified size, using an 8-character suffix
  split -b "$MAX_SIZE" -a 8 "$file" "$OUTPUT_DIR/${base_name}_"

  # Check if the split operation was successful
  if [ $? -ne 0 ]; then
    handle_error "Error splitting $file"
  fi

  # Rename the split parts using a sortable numeric sequence
  local count=1
  for part in "$OUTPUT_DIR/${base_name}_"*; do
    # Create a new filename using a zero-padded numeric sequence (e.g., base_name_00000001.log)
    local new_name="${OUTPUT_DIR}/${base_name}_$(printf "%08d" "$count").log"

    # Rename the split part
    mv "$part" "$new_name"

    # Check if the rename operation was successful
    if [ $? -ne 0 ]; then
      handle_error "Error renaming $part to $new_name"
    fi

    log_message "Renamed $part to $new_name"
    count=$((count + 1))  # Increment counter for the next part
  done
}

#############################
# Main Script Execution
#############################

# Log the start of the process
log_message "Starting to process log files from: $LOG_DIR"

# Main loop: find all .log files in the LOG_DIR and process them
find "$LOG_DIR" -type f -name "*.log" | while read -r file; do
  split_log_file "$file" || handle_error "Failed to process $file"
done

# Log the completion of the session
log_message "Splitting session completed: $(date)"

# End of script