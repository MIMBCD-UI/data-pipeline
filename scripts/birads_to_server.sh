#!/bin/bash
#
# Author: Francisco Maria Calisto
# Created Date: 2024-04-11
# Revised Date: 2024-04-11
# Usage: ./birads_to_server.sh
# Example: ./script/birads_to_server.sh
# Description: Adjusted for macOS and
# Ubunto servers. Copies files from a
# local directory to a remote server
# using scp.

# Define home directory
home="$HOME"

# Source directory on your macOS
SOURCE_DIR="$home/Git/dataset-multimodal-breast/data/birads/"

# Define the target directory path as a variable
TARGET_PATH="/data/datasets/dataset-multimodal-breast/data/birads/"

# Prompt for the server's username
read -p "Enter the server's username: " username

# Prompt for the server's IP address
read -p "Enter the server's IP address: " server_ip

# Combine username, server IP, and target path
# to form the full target directory
TARGET_DIR="${username}@[${server_ip}]:${TARGET_PATH}"

# Prompt for the server's password
read -s -p "Enter the server's password: " password
echo

for file in "${SOURCE_DIR}"*
do
  echo "Copying $file to $TARGET_DIR"
  sshpass -p "$password" scp "$file" "$TARGET_DIR"
  echo
done

echo "Files copied successfully."

# End of script