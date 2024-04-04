# Data Pipeline

This repository contains a data pipeline for processing medical imaging data. It includes modules for anonymizing DICOM files, encrypting patient IDs, extracting metadata, and processing the data.

## Modules

- `anonymizer.py`: Module for anonymizing DICOM files by removing patient-related information and renaming them according to a specified format.
- `encryption.py`: Module for encrypting patient IDs.
- `extractor.py`: Module for extracting metadata from DICOM files.
- `main.py`: Main script for executing the data processing pipeline.
- `processor.py`: Module for processing medical imaging data.

## Usage

To use the data pipeline, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/MIMBCD-UI/data-pipeline.git
```

2. Install the required dependencies by creating a virtual environment and installing the packages listed in `requirements.txt`:

```bash
cd data-pipeline
pip install -r requirements.txt
```

3. Run the main script to execute the data processing pipeline:

```bash
python main.py
```

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit a pull request with your proposed changes.

## License

This project is licensed under the [MIT License](LICENSE).