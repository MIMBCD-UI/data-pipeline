#!/bin/bash
#
# Author: Francisco Maria Calisto
# Created Date: 2024-04-11
# Revised Date: 2024-05-18
# Usage: ./copy_to_server.sh
# Example: ./script/copy_to_server.sh
# Description: Adjusted for macOS and
# Ubuntu servers. Copies files from a
# local directory to a remote server
# using rsync.

# Define home directory
home="$HOME"

# Source directory on your macOS
SOURCE_DIR="$home/Git/dataset-multimodal-breast/"

# Define the target directory path as a variable
TARGET_PATH="/data/datasets/dataset-multimodal-breast/"

# Prompt for the server's username
read -p "Enter the server's username: " username

# Prompt for the server's IP address
read -p "Enter the server's IP address: " server_ip

# Combine username, server IP, and target path to form the full target directory
if [[ "$server_ip" == *":"* ]]; then
  TARGET_DIR="${username}@[$server_ip]:${TARGET_PATH}"
else
  TARGET_DIR="${username}@${server_ip}:${TARGET_PATH}"
fi

# Check if SOURCE_DIR exists and is not empty
if [ ! -d "$SOURCE_DIR" ] || [ -z "$(ls -A "$SOURCE_DIR")" ]; then
  echo "Source directory does not exist or is empty. Exiting."
  exit 1
fi

# Check if rsync is installed
if ! command -v rsync &> /dev/null; then
  echo "rsync could not be found. Please install it and try again."
  exit 1
fi

# Prompt for the server's password (if needed, can be automated with SSH keys)
read -s -p "Enter the server's password (or press enter if using SSH keys): " password
echo

# Ensure target directory exists on the server
if [ -n "$password" ]; then
  sshpass -p "$password" ssh "${username}@$server_ip" "mkdir -p $TARGET_PATH"
else
  ssh "${username}@$server_ip" "mkdir -p $TARGET_PATH"
fi

# Check if the target directory creation succeeded
if [ $? -ne 0 ]; then
  echo "Failed to create target directory $TARGET_PATH on remote server. Exiting."
  exit 1
fi

# Use rsync to copy files
if [ -n "$password" ]; then
  sshpass -p "$password" rsync -avz --progress -e "ssh" "$SOURCE_DIR" "$TARGET_DIR"
else
  rsync -avz --progress -e "ssh" "$SOURCE_DIR" "$TARGET_DIR"
fi

if [ $? -eq 0 ]; then
  echo "Files copied successfully."
else
  echo "Failed to copy files."
fi

# End of script