#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-11
# Revised Date: 2024-09-29  # Directory modularization and enhanced batch processing for large datasets
# Version: 1.4.2
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./birads_to_server.sh
# Example: ./script/birads_to_server.sh
# Description: This script copies files from a local directory to a remote server in batches using `scp`.
# It handles massive datasets, includes detailed logging, and ensures safe execution with password-based authentication.

# Exit immediately if any command fails to ensure safe execution
set -e

#############################
# Directory Structure Setup
#############################

# Define the home directory using the system's HOME environment variable
home="$HOME"

# Root directory for Git projects
git_root="$home/Git"

# Project-specific directory
project_name="dataset-multimodal-breast"
project_dir="$git_root/$project_name"

# Data directory inside the project
data_dir="$project_dir/data"

# Subdirectory for BIRADS data
birads_dir="$data_dir/birads"

# Set the source directory to the BIRADS folder for the copy operation
source_dir="$(realpath "$birads_dir")"

# Remote server directory structure split into modular parts
server_protocol="scp"  # Protocol used for copying
server_base="/data"  # Base directory on the server
server_datasets="datasets"  # Datasets directory on the server
server_project="$project_name"  # Project directory on the server
server_data="data"  # Data directory inside the project on the server
server_birads="birads"  # BIRADS data subdirectory

# Combine all parts to form the full remote target directory
target_dir="$server_base/$server_datasets/$server_project/$server_data/$server_birads/"

#############################
# Batch Processing Setup
#############################

# Define the batch size for handling large datasets
BATCH_SIZE=100  # Number of files to process in each batch

#############################
# Logging Function
#############################

# Function to log messages with timestamps for better visibility
# Arguments:
#   $1: Message to log
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

#############################
# User Inputs and Setup
#############################

# Prompt for the server's username and IP address
read -p "Enter the server's username: " username
read -p "Enter the server's IP address: " server_ip

# Handle IPv6 addresses by enclosing them in square brackets
if [[ "$server_ip" == *":"* ]]; then
  remote_target="${username}@[$server_ip]:$target_dir"
else
  remote_target="${username}@${server_ip}:$target_dir"
fi

# Prompt for the server's password (optional if using SSH keys), and hide the input for security
read -s -p "Enter the server's password: " password
echo  # Move to a new line after password input

#############################
# Pre-execution Validations
#############################

# Check if the source directory exists and is not empty
if [ ! -d "$source_dir" ]; then
  log_message "Error: Source directory $source_dir does not exist. Exiting."
  exit 1
elif [ -z "$(ls -A "$source_dir")" ]; then
  log_message "Error: Source directory $source_dir is empty. Exiting."
  exit 1
fi

# Ensure sshpass is installed for password-based scp
if ! command -v sshpass &> /dev/null; then
  log_message "Error: sshpass is required but not installed. Please install sshpass and try again."
  exit 1
fi

#############################
# File Transfer Function
#############################

# Function to copy a file to the remote server using scp and sshpass for password authentication
# Arguments:
#   $1: Full path of the file to be copied
copy_files_to_server() {
  local file="$1"
  log_message "Copying $file to $remote_target..."

  # Use sshpass to handle password-based scp file transfers
  sshpass -p "$password" scp "$file" "$remote_target"

  # Verify if the file was copied successfully
  if [ $? -eq 0 ]; then
    log_message "Successfully copied $file."
  else
    log_message "Error: Failed to copy $file. Continuing with the next file."
  fi
}

#############################
# Batch Processing Function
#############################

# Function to process files in batches to prevent overloading system resources
process_files_in_batches() {
  local file_count=0  # Counter for files processed
  local files_to_copy=()  # Array to store files in batches

  log_message "Starting to process files from $source_dir and transfer them to $remote_target"

  # Loop through each file in the source directory
  for file in "$source_dir"/*; do
    if [ -f "$file" ]; then
      files_to_copy+=("$file")  # Add the file to the batch
      file_count=$((file_count + 1))  # Increment file count

      # Process the batch once it reaches the defined BATCH_SIZE
      if [ "$file_count" -ge "$BATCH_SIZE" ]; then
        log_message "Processing a batch of $BATCH_SIZE files..."
        for batch_file in "${files_to_copy[@]}"; do
          copy_files_to_server "$batch_file"
        done
        # Reset the batch after processing
        file_count=0
        files_to_copy=()
      fi
    fi
  done

  # Process any remaining files that didn't fill the last batch
  if [ "${#files_to_copy[@]}" -gt 0 ]; then
    log_message "Processing remaining ${#files_to_copy[@]} files..."
    for batch_file in "${files_to_copy[@]}"; do
      copy_files_to_server "$batch_file"
    done
  fi

  log_message "File transfer completed successfully."
}

#############################
# Execution: Start Batch Processing
#############################

process_files_in_batches

# Final log message indicating the script completed successfully
log_message "All files have been successfully transferred to the server."

# End of script