#!/bin/bash

# Define directories to clear
directories=(
  "/Users/francisco/Git/dataset-multimodal-breast/tests/dicom/"
  "/Users/francisco/Git/dataset-multimodal-breast/tests/test001/"
  "/Users/francisco/Git/dataset-multimodal-breast/tests/test002/"
  "/Users/francisco/Git/dataset-multimodal-breast/tests/test003/"
  "/Users/francisco/Git/dataset-multimodal-breast/tests/test004/"
  "/Users/francisco/Git/dicom-images-breast/data/meta/pre/"
  "/Users/francisco/Git/dicom-images-breast/data/meta/post/"
  "/Users/francisco/Git/dicom-images-breast/data/mapping/"
)

# Loop through each directory and remove its contents
for dir in "${directories[@]}"; do
  echo "Removing all files in $dir"
  rm -f "${dir}"*
done

echo "All specified directories have been cleared."
