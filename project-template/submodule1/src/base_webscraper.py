from pathlib import WindowsPath
from project_config import Config, JSONLogger

#
#  project_config:  
#           - contains project file directory structure and key files.
#           - Config() inherits UserValidationError()
#           - JSONLogger is imported from logging_config.py afterward
configs = Config()
logger = JSONLogger(__package__, __name__, **configs.__dict__)

