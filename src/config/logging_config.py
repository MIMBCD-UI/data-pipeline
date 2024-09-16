# logging_config.py

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