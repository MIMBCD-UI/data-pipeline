#!/bin/bash
#
# Author: Francisco Maria Calisto
# Created Date: 2024-04-10
# Revised Date: 2024-04-10
# Usage: ./search_in_logs.sh
# Example: ./script/search_in_logs.sh
# Description: This script splits large
# log files into smaller ones based on
# a specified word.

# Define home directory
home="$HOME"

# Hardcoded directory containing the .log files
LOG_DIR="$home/Git/dicom-images-breast/data/logs/processed"

# Hardcoded word to search for in the log files
SEARCH_WORD="(tudo bem)"

# Ensure the directory exists
if [ ! -d "$LOG_DIR" ]; then
    echo "Directory does not exist: $LOG_DIR"
    exit 1
fi

# Search the specified word in all .log files within the directory
echo "Searching for '$SEARCH_WORD' in logs located at $LOG_DIR..."
find "$LOG_DIR" -type f -name "*.log" | while read -r FILE; do
    echo "Searching in $FILE..."
    # Use grep to search for the word, displaying the file name and line number
    grep -Hin "$SEARCH_WORD" "$FILE" | while read -r LINE; do
        echo "$FILE: $LINE"
    done
done

echo "Search complete."

# End of script