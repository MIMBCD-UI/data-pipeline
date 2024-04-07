#!/bin/bash
#
# Author: Francisco Maria Calisto
# Date: 2024-04-07
# Usage: ./copy_testing_files.sh
# Example: ./script/copy_testing_files.sh
# Description: This script reads a list of file paths
# from a text file and copy them to a directory.

# Define home directory
home="$HOME"

# Define the source file containing file paths
source_file="$home/Git/dicom-images-breast/data/logs/test005.txt"

# Define the destination folder where files will be copied
destination_folder="$home/Git/dicom-images-breast/tests/testing_data-pipeline_t005/"

echo "Copying files from $source_file to $destination_folder"

# Check if the destination folder exists, if not create it
if [ ! -d "$destination_folder" ]; then
    mkdir -p "$destination_folder"
fi

# Initialize counter
counter=1

# Read each line from test005.txt
while IFS= read -r file_path; do
    # Check if the file exists
    if [ -f "$file_path" ]; then
        # Extract the filename from the file path
        filename=$(basename "$file_path")
        # Construct new filename with counter
        new_filename="file_${counter}_${filename}"
        # Copy the file to the destination folder with the new filename
        cp "$file_path" "$destination_folder/$new_filename"
        echo "Copied $filename to $destination_folder as $new_filename"
        # Increment counter
        ((counter++))
    else
        echo "File not found: $file_path"
    fi
done < "$source_file"

# End of script