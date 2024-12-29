
import logging
from src.setup import BaseConfig
from src.configs.loggers import JSONLogger

print(BaseConfig.PROJECTPATH)
logger = JSONLogger(__package__, __name__)
logger.get_logger()
logging.info(f"testing")

