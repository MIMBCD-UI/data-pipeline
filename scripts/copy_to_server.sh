#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-04-11
# Revised Date: 2024-09-29  # Improved modularity and logging for massive datasets
# Version: 1.5.2  # Version increment reflecting modularity and performance enhancements
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./copy_to_server.sh
# Example: ./scripts/copy_to_server.sh
# Description: This script copies files from a local directory to a remote server using rsync.
#              Supports password-based authentication (sshpass) and SSH key-based authentication.
#              Optimized for large datasets with parallel processing and error handling.

set -e  # Exit immediately if any command fails for safety

#############################
# Directory Structure Modularity
#############################

# Define the home directory using the system's HOME environment variable
home="$HOME"

# Modular directory components
git_root="$home/Git"                             # Base directory for all Git projects
project_folder="dataset-multimodal-breast"       # Project directory
data_folder="data"                               # Data folder
curation_folder="curation"                       # Curation subdirectory within the data folder

# Full source directory path combining all modular components
source_dir_path="$git_root/$project_folder/$data_folder/$curation_folder"
source_dir="$(realpath "$source_dir_path")"  # Ensure the path is absolute

# Remote server configuration: Modular components for the server paths
server_root="/data"
datasets_folder="datasets"
remote_project_folder="$project_folder"
remote_data_folder="$data_folder"
remote_curation_folder="$curation_folder"

# Full remote target path on the server
target_dir_path="$server_root/$datasets_folder/$remote_project_folder/$remote_data_folder/$remote_curation_folder"
target_dir="${server_username}@${server_ip}:${target_dir_path}"

#############################
# Logging Function
#############################

# Function to log messages with timestamps for better tracking and debugging
# Arguments:
#   $1: The message to log
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

#############################
# Server Configuration
#############################

# Prompt the user for the server's username and store it in the 'server_username' variable
read -p "Enter the server's username: " server_username

# Prompt the user for the server's IP address and store it in the 'server_ip' variable
read -p "Enter the server's IP address: " server_ip

# Handle IPv6 addresses by enclosing them in square brackets for the target directory
if [[ "$server_ip" == *":"* ]]; then
  target_dir="${server_username}@[$server_ip]:${target_dir_path}"
else
  target_dir="${server_username}@${server_ip}:${target_dir_path}"
fi

# Prompt for the server's password (optional if SSH keys are used) and hide input for security
read -s -p "Enter the server's password (press Enter if using SSH keys): " server_password
echo  # Move to a new line after the password input

#############################
# Pre-Execution Checks
#############################

# Check if the source directory exists and is not empty
if [ ! -d "$source_dir" ] || [ -z "$(ls -A "$source_dir")" ]; then
  log_message "Error: Source directory $source_dir does not exist or is empty. Exiting."
  exit 1
fi

# Ensure rsync is installed, and exit with a message if not
if ! command -v rsync &> /dev/null; then
  log_message "Error: rsync is not installed. Please install it and try again."
  exit 1
fi

#############################
# Ensure Remote Directory Exists
#############################

# Function to ensure the target directory exists on the remote server
# Supports both password-based authentication (using sshpass) and SSH key-based authentication
ensure_remote_directory_exists() {
  log_message "Ensuring target directory $target_dir_path exists on the remote server..."

  if [ -n "$server_password" ]; then
    # Use sshpass for password-based authentication
    sshpass -p "$server_password" ssh -o StrictHostKeyChecking=no "${server_username}@${server_ip}" "mkdir -p $target_dir_path"
  else
    # Use SSH key-based authentication
    ssh -o StrictHostKeyChecking=no "${server_username}@${server_ip}" "mkdir -p $target_dir_path"
  fi

  # Check if the directory creation succeeded
  if [ $? -ne 0 ]; then
    log_message "Error: Failed to create target directory $target_dir_path on the remote server. Exiting."
    exit 1
  fi
}

# Call the function to create the remote directory if it doesn't exist
ensure_remote_directory_exists

#############################
# Batch File Transfer Function
#############################

# Function to process files in batches and transfer them using parallel rsync
# This function uses xargs for parallelism to improve performance for large datasets
batch_process_files() {
  log_message "Starting batch file transfer from $source_dir to $target_dir..."

  # Find all files in the source directory and use xargs to execute multiple rsync processes in parallel
  find "$source_dir" -type f | xargs -P 4 -I {} bash -c '
    if [ -n "$server_password" ]; then
      # Use sshpass with rsync for password-based authentication
      sshpass -p "$server_password" rsync -avz --progress -e "ssh" "{}" "$target_dir"
    else
      # Use SSH key-based authentication with rsync
      rsync -avz --progress -e "ssh" "{}" "$target_dir"
    fi
  '
}

# Start the batch file transfer process
batch_process_files

# Check if rsync was successful for the last batch
if [ $? -eq 0 ]; then
  log_message "Files transferred successfully."
else
  log_message "Error: File transfer failed. Exiting."
  exit 1
fi

# Final log message indicating successful completion of the file transfer
log_message "File transfer completed successfully."

# End of script