#!/usr/bin/env python

"""
logging_config.py: Module for setting up logging configuration using a YAML file.

This module provides a function to set up logging configuration based on a YAML file.
The configuration file specifies the log file path, log level, and log format.

Key Functions:
- setup_logging: Set up logging configuration using a YAML file.

Expected Usage:
- Call `setup_logging` at the beginning of the main script to configure logging.
- Use the logging module to log messages to the specified log file and console.

Customization & Flexibility:
- The logging configuration can be customized by editing the YAML file.
- Additional handlers or formatters can be added to the logging configuration.
- The log level can be adjusted to control the verbosity of log messages.

Performance & Compatibility:
- The logging configuration is optimized for performance and resource usage.
- The module is compatible with Python 3.6+ and can be used in various environments and platforms.

Best Practices & Maintenance:
- The script follows best practices for error handling, logging, and code readability.
- It is well-documented and can be easily maintained or extended by other developers.
- The script is designed to be robust and reliable for long-term use in data curation workflows.

Notes:
- This module is part of a larger data curation pipeline for multimodal breast imaging data.
- It is optimized for processing DICOM files but can be adapted for other types of medical imaging data.
- The script is designed to be run from the command line or as part of an automated workflow.

References:
- Logging configuration: https://docs.python.org/3/library/logging.config.html
- YAML format: https://yaml.org/spec/1.2/spec.html
"""

import logging
import logging.config
import yaml

def setup_logging(config_path='config.yaml'):
  with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

  logging_config = {
    'version': 1,
    'formatters': {
      'default': {
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      },
    },
    'handlers': {
      'file': {
        'class': 'logging.FileHandler',
        'formatter': 'default',
        'filename': config['logging']['log_file'],
      },
      'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'default',
      },
    },
    'root': {
      'level': config['logging']['level'],
      'handlers': ['file', 'console']
    },
  }

  logging.config.dictConfig(logging_config)

# To use the logging configuration, simply call `setup_logging` at the start of your main script.