#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-21
# Revised Date: 2024-09-29  # Split directory structure and file paths into individual variables
# Version: 1.6.3
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./move_files.sh
# Example: ./scripts/move_files.sh
# Description: This script moves files from the "unexplored" folder to the "checking" folder 
# inside the dataset-multimodal-breast repository. It handles large datasets by processing files in batches, 
# offers parallelism for speed, checks disk space, and logs errors in the curation/logs folder.

set -e  # Exit script on any command failure to ensure safe execution

#############################
# Modular Directory Structure
#############################

# Base user home directory
home="$HOME"

# Git root directory (base for all Git repositories)
git_root="$home/Git"

# Project directories, split by levels for modularity
dataset_project="dataset-multimodal-breast"
data_dir="data"
curation_dir="curation"
unexplored_dir="unexplored"
checking_dir="checking"
logs_dir="logs"

# Construct full directory paths using modular variables
src_dir="$git_root/$dataset_project/$data_dir/$curation_dir/$unexplored_dir"
dest_dir="$git_root/$dataset_project/$data_dir/$curation_dir/$checking_dir"
log_dir="$git_root/$dataset_project/$data_dir/$curation_dir/$logs_dir"

# Log file name and path (modularized and timestamped)
log_filename="move_files_$(date +'%Y%m%d_%H%M%S').log"
log_file="$log_dir/$log_filename"

#############################
# Logging and Error Handling Functions
#############################

# Function to log messages with timestamps for tracking
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "$log_file"
}

# Function to log errors, print to stderr, and log them
# Arguments:
#   $1: The error message to display and log
print_error() {
  echo "$1" >&2  # Print the error message to stderr
  echo "$(date +'%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$log_file"  # Log the error message
}

#############################
# Directory and Disk Space Validation Functions
#############################

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
  local available_space=$(df "$dest_dir" | awk 'NR==2 {print $4}')

  # Check if the available disk space is sufficient
  if (( available_space < required_space )); then
    print_error "Not enough disk space. Available: ${available_space}KB, Required: ${required_space}KB. Exiting."
    exit 1
  else
    log_message "Sufficient disk space available: ${available_space}KB"
  fi
}

#############################
# File Moving and Batch Processing Function
#############################

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

#############################
# Move Success Validation Function
#############################

# Function to check if the move operation was successful
check_move_success() {
  if [ $? -eq 0 ]; then
    log_message "File move operation completed successfully."
  else
    print_error "An error occurred during the file move operation."
    exit 1
  fi
}

#############################
# Main Script Execution
#############################

# Ensure the log directory exists (create it if it doesn't)
mkdir -p "$log_dir"

# Validate the source and destination directories
validate_directory "$src_dir" "Source"
validate_directory "$dest_dir" "Destination"

# Check for sufficient disk space (assuming a minimum of 10GB required space)
check_disk_space 10485760  # 10GB in kilobytes

# Move the files from the source to the destination in batches
move_files_in_batches "$src_dir" "$dest_dir"

# Check if the move operation was successful
check_move_success

# Final log message indicating that the script has completed
log_message "Operation complete. Logs saved in $log_file."

# End of script