"""Helper functions
"""

import pathlib
from configparser import ConfigParser

def read_config():
    # Grab configuration values.
    config = ConfigParser()
    file_path = pathlib.Path('config/config.ini').resolve()
    config.read(file_path)
    return config
