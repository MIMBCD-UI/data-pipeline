#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-11
# Revised Date: 2024-09-22  # Updated to reflect improvements
# Version: 1.2  # Incremented version to reflect further optimizations for large datasets
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./birads_to_server.sh
# Example: ./script/birads_to_server.sh
# Description: This script copies files from a local directory to a remote server using scp.
# It includes error handling, path validation, and optimizations for transferring large datasets.

# Exit the script if any command fails to ensure safe execution
set -e

# Define the home directory using the system's HOME environment variable
home="$HOME"

# Source directory on your macOS system (using realpath for robustness)
# 'realpath' ensures the path is absolute and valid
SOURCE_DIR="$(realpath "$home/Git/dataset-multimodal-breast/data/birads/")"

# Define the target directory path on the remote server
TARGET_PATH="/data/datasets/dataset-multimodal-breast/data/birads/"

# Define batch size for handling large datasets
BATCH_SIZE=100  # Number of files to process in each batch

# Function to log messages to the terminal for better visibility
log_message() {
  echo "$1"
}

# Prompt for the server's username and store it in the 'username' variable
read -p "Enter the server's username: " username

# Prompt for the server's IP address and store it in the 'server_ip' variable
read -p "Enter the server's IP address: " server_ip

# Handle IPv6 addresses by enclosing them in square brackets to form the full target directory
if [[ "$server_ip" == *":"* ]]; then
  TARGET_DIR="${username}@[$server_ip]:${TARGET_PATH}"
else
  TARGET_DIR="${username}@${server_ip}:${TARGET_PATH}"
fi

# Prompt for the server's password and hide the input for security
read -s -p "Enter the server's password: " password
echo  # Move to a new line after the password input

# Check if the source directory exists and is not empty
if [ ! -d "$SOURCE_DIR" ]; then
  log_message "Error: Source directory $SOURCE_DIR does not exist. Exiting."
  exit 1
elif [ -z "$(ls -A "$SOURCE_DIR")" ]; then
  log_message "Error: Source directory $SOURCE_DIR is empty. Exiting."
  exit 1
fi

# Check if sshpass is installed (required for password-based scp)
if ! command -v sshpass &> /dev/null; then
  log_message "Error: sshpass could not be found. Please install it and try again."
  exit 1
fi

# Function to copy files to the remote server using scp and sshpass
copy_files_to_server() {
  local file="$1"
  log_message "Copying $file to $TARGET_DIR..."
  
  # Copy the file using scp and sshpass for password-based authentication
  sshpass -p "$password" scp "$file" "$TARGET_DIR"
  
  # Check if the file copy was successful
  if [ $? -eq 0 ]; then
    log_message "Successfully copied $file."
  else
    log_message "Error: Failed to copy $file. Continuing with next file."
  fi
}

# Function to process files in batches
# This is important to prevent memory or performance issues when dealing with large datasets.
process_files_in_batches() {
  local file_count=0
  local files_to_copy=()
  
  # Loop through all files in the source directory
  for file in "$SOURCE_DIR"*; do
    if [ -f "$file" ]; then
      files_to_copy+=("$file")  # Add file to the batch
      file_count=$((file_count + 1))

      # Process the batch if we reach the BATCH_SIZE limit
      if [ "$file_count" -ge "$BATCH_SIZE" ]; then
        log_message "Processing batch of $BATCH_SIZE files..."
        for batch_file in "${files_to_copy[@]}"; do
          copy_files_to_server "$batch_file"
        done
        # Reset the batch
        file_count=0
        files_to_copy=()
      fi
    else
      log_message "No files found in $SOURCE_DIR. Skipping."
    fi
  done

  # Process any remaining files that didn't fill the last batch
  if [ "${#files_to_copy[@]}" -gt 0 ]; then
    log_message "Processing remaining ${#files_to_copy[@]} files..."
    for batch_file in "${files_to_copy[@]}"; do
      copy_files_to_server "$batch_file"
    done
  fi
}

# Call the batch processing function to start transferring files
process_files_in_batches

# Final message indicating the script has completed successfully
log_message "All files have been copied to the server successfully."

# End of script