#!/bin/bash
#
# Author: Francisco Maria Calisto
# Created Date: 2024-04-10
# Revised Date: 2024-04-11
# Usage: ./split_log_files.sh
# Example: ./script/split_log_files.sh
# Description: Adjusted for macOS. Splits large .log files into smaller parts based
# on a maximum file size and renames them using a specific filename pattern
# to ensure a sortable, numeric sequence.

# Define home directory
home="$HOME"

# Directory containing .log files
LOG_DIR="$home/Git/dicom-images-breast/data/logs/toprocess"

# Directory to save the split files
OUTPUT_DIR="$home/Git/dicom-images-breast/data/logs/processed"

# Maximum file size (in bytes)
# Example: 40m for 40MB files on macOS
MAX_SIZE="40m"

# Log file for capturing script operations and potential issues
LOG_FILE="$home/Git/dicom-images-breast/data/logs/splits/split_log_files.log"

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

# Initialize or clear the log file
echo "Starting new splitting session: $(date)" > "$LOG_FILE"

# Loop through each .log file in the directory
find "$LOG_DIR" -type f -name "*.log" | while read -r FILE; do
    echo "Processing file: $FILE" | tee -a "$LOG_FILE"
    BASE_NAME=$(basename "$FILE" .log)

    # Split the file into parts of the specified size and use a temporary naming scheme
    # Adjusted for macOS syntax
    split -b "$MAX_SIZE" -a 8 "$FILE" "$OUTPUT_DIR/${BASE_NAME}_"
    if [ $? -ne 0 ]; then
        echo "Error splitting $FILE" | tee -a "$LOG_FILE"
        continue  # Skip to next file in case of error
    fi

    COUNT=1
    for PART in "$OUTPUT_DIR/${BASE_NAME}_"*; do
        NEW_NAME="${OUTPUT_DIR}/${BASE_NAME}_$(printf "%08d" "$COUNT").log"
        mv "$PART" "$NEW_NAME"
        if [ $? -ne 0 ]; then
            echo "Error renaming $PART to $NEW_NAME" | tee -a "$LOG_FILE"
            continue  # Proceed to attempt to rename next part
        fi
        echo "Renamed $PART to $NEW_NAME" | tee -a "$LOG_FILE"
        let COUNT++
    done
done

echo "Splitting session completed: $(date)" | tee -a "$LOG_FILE"

# End of script