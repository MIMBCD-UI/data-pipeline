#!/bin/bash
#
# Author: Francisco Maria Calisto
# Maintainer: Francisco Maria Calisto
# Email: francisco.calisto@tecnico.ulisboa.pt
# License: ACADEMIC & COMMERCIAL
# Created Date: 2024-09-22
# Revised Date: 2024-09-22  # First version of this shell script
# Version: 1.0
# Status: Development
# Credits:
#   - Carlos Santiago
#   - Catarina Barata
#   - Jacinto C. Nascimento
#   - Diogo Araújo
# Usage: ./explorer.sh
# Example: ./script/explorer.sh
# Description: This script reads DICOM files from the "unexplored" folder, extracts the Patient ID from the DICOM metainformation, 
# checks if the Patient ID exists in the second column of the 'anonymized_patients_birads_curation.csv' file.
# If a match is found, the DICOM file is moved to the "checking" folder. The script processes up to 10 files.

# Exit the script if any command fails
set -e

# Limit for the number of files to process
FILE_LIMIT=10

# Define root directory relative to this script's location
home="$HOME"
root_dir="$home/Git/dataset-multimodal-breast"
unexplored_dir="$root_dir/data/curation/unexplored"
checking_dir="$root_dir/data/curation/checking"
csv_file="$root_dir/data/birads/anonymized_patients_birads_curation.csv"
LOG_DIR="$root_dir/data/logs"
LOG_FILE="$LOG_DIR/explorer_$(date +'%Y%m%d_%H%M%S').log"

# Create log directory if it does not exist
mkdir -p "$LOG_DIR"

# Log messages to both the console and the log file
log_message() {
  echo "$1" | tee -a "$LOG_FILE"
}

# Validate directory existence
validate_directory() {
  local dir_path="$1"
  local dir_name="$2"
  if [ ! -d "$dir_path" ]; then
    log_message "Error: $dir_name directory $dir_path does not exist. Exiting."
    exit 1
  fi
}

# Validate that all directories exist
validate_directory "$unexplored_dir" "Unexplored"
validate_directory "$checking_dir" "Checking"
validate_directory "$(dirname "$csv_file")" "CSV"

# Load Patient IDs from the CSV file into a set (hashmap equivalent in shell)
declare -A patient_ids
log_message "Loading Patient IDs from CSV file..."

while IFS=, read -r col1 col2; do
  patient_ids["$col2"]=1  # Use patient ID from the second column
done < <(tail -n +2 "$csv_file")  # Skip the header row

log_message "Loaded ${#patient_ids[@]} Patient IDs from the CSV."

# Move files to the "checking" directory if their Patient ID is found in the CSV
process_files() {
  local count=0
  log_message "Processing DICOM files from $unexplored_dir..."

  find "$unexplored_dir" -type f -name "*.dcm" | while IFS= read -r dicom_file; do
    if (( count >= FILE_LIMIT )); then
      log_message "Reached file limit of $FILE_LIMIT."
      break
    fi

    # Extract Patient ID using `dcmdump` (DCMTK package required)
    patient_id=$(dcmdump +P PatientID "$dicom_file" 2>/dev/null | awk -F'\\' '{print $2}')

    if [ -n "$patient_id" ]; then
      if [ "${patient_ids[$patient_id]+exists}" ]; then
        mv "$dicom_file" "$checking_dir"
        log_message "Moved $dicom_file to $checking_dir (Patient ID: $patient_id)"
        ((count++))
      else
        log_message "Patient ID $patient_id not found in CSV. File remains in unexplored."
      fi
    else
      log_message "No Patient ID found for $dicom_file."
    fi
  done

  log_message "Processed $count files."
}

# Call the function to process files
process_files

log_message "DICOM file exploration complete."

# End of script