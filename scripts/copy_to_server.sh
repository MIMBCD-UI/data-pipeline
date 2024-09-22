#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-11
# Revised Date: 2024-09-22
# Version: 1.4  # Incremented version to reflect further improvements
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./copy_to_server.sh
# Example: ./script/copy_to_server.sh
# Description: This script copies files from a local directory to a remote server using rsync.
# Supports password-based authentication (using sshpass) and SSH key-based authentication.
# Optimized for large datasets with batch processing and parallel transfers.

# Exit immediately if any command fails to ensure safe execution
set -e

# Define the home directory using the system's HOME environment variable
home="$HOME"

# Resolve the absolute path of the source directory using realpath for robustness
SOURCE_DIR="$(realpath "$home/Git/dataset-multimodal-breast/")"

# Define the target directory path on the remote server (adjust as needed)
TARGET_PATH="/data/datasets/dataset-multimodal-breast/"

# Define the maximum number of parallel rsync processes to handle large datasets efficiently
MAX_PARALLEL_PROCESSES=4  # Adjust this based on your system's resources (e.g., CPU and network capacity)

# Function to log messages to the terminal for better visibility and debugging
# Arguments:
#   $1: The message to log
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

# Check if the source directory exists and is not empty
if [ ! -d "$SOURCE_DIR" ] || [ -z "$(ls -A "$SOURCE_DIR")" ]; then
  log_message "Source directory does not exist or is empty. Exiting."
  exit 1
fi

# Check if rsync is installed, and exit with a helpful message if not
if ! command -v rsync &> /dev/null; then
  log_message "rsync is not installed. Please install it and try again."
  exit 1
fi

# Prompt for the server's password (optional if SSH keys are used) and hide the input for security
read -s -p "Enter the server's password (press Enter if using SSH keys): " password
echo  # Move to a new line after the password input

# Function to ensure the target directory exists on the remote server
# This function uses either sshpass (for password authentication) or SSH keys for authentication.
ensure_remote_directory_exists() {
  log_message "Ensuring target directory $TARGET_PATH exists on the remote server..."
  if [ -n "$password" ]; then
    # Use sshpass for password-based authentication to create the target directory
    sshpass -p "$password" ssh -o StrictHostKeyChecking=no "${username}@${server_ip}" "mkdir -p $TARGET_PATH"
  else
    # Use SSH key-based authentication to create the target directory
    ssh -o StrictHostKeyChecking=no "${username}@${server_ip}" "mkdir -p $TARGET_PATH"
  fi

  # Check if the directory creation succeeded and exit if it failed
  if [ $? -ne 0 ]; then
    log_message "Failed to create target directory $TARGET_PATH on the remote server. Exiting."
    exit 1
  fi
}

# Call the function to create the remote directory
ensure_remote_directory_exists

# Function to process files in batches using parallel rsync transfers to improve performance for large datasets
# This method uses xargs to handle parallelism.
batch_process_files() {
  log_message "Starting batch file transfer from $SOURCE_DIR to $TARGET_DIR..."

  # Use find to get all files in the source directory, and xargs to execute multiple rsync processes in parallel
  # The -P flag defines the number of parallel rsync processes (based on MAX_PARALLEL_PROCESSES)
  find "$SOURCE_DIR" -type f | xargs -P "$MAX_PARALLEL_PROCESSES" -I {} bash -c '
    if [ -n "$password" ]; then
      # Use sshpass with rsync for password-based authentication
      sshpass -p "$password" rsync -avz --progress -e "ssh" "{}" "$TARGET_DIR"
    else
      # Use SSH key-based authentication with rsync
      rsync -avz --progress -e "ssh" "{}" "$TARGET_DIR"
    fi
  '
}

# Call the batch processing function to start transferring files
batch_process_files

# Check if rsync was successful for the last batch
if [ $? -eq 0 ]; then
  log_message "Files copied successfully."
else
  log_message "Failed to copy files. Exiting."
  exit 1
fi

# Final log message indicating successful completion of the file transfer
log_message "File transfer completed successfully."

# End of script