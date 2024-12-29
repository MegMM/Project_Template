import os, sys
from pathlib import WindowsPath, PureWindowsPath, Path
import atexit
import datetime
import json
import logging
import logging.config
import logging.handlers
from typing import override

###
# Add line to launch.json:
#     "cwd": "${fileDirname}",
#

test_key = "test key"


rec = logging.LogRecord('',0,None,0,'',[],None) # create a minimal LogRecord
all_attributes = dir(rec)
LOG_RECORD_BUILTIN_ATTRS = [a for a in all_attributes if '__' not in a]
# for a in all_attributes:
#     if '__' not in a:
#         print(f"{a = }")
# LOG_RECORD_BUILTIN_ATTRS = {a for a in all_attributes if '__' not in a}


class BaseConfig:
    def __init__(self):
        pass


# class SimpleLogger(BaseConfig):
class SimpleLogger:
    def __init__(self, pkg=None, name=None):
        setattr(self, 'pkg', pkg if pkg is not None else (WindowsPath(__file__)).anchor)
        if name is not None:
            setattr(self, 'name', name)
        else:
            raise ValueError

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(module)s.%(funcName)s, line %(lineno)s: %(message)s')
        # add formatter to ch
        console.setFormatter(formatter)
        # add ch to logger
        self.logger.addHandler(console)
        file_log = logging.handlers.RotatingFileHandler(os.path.abspath(os.path.join(os.getcwd(), "simplelog.log")), encoding= "utf-8", mode="w+", maxBytes=100000, backupCount=3)
        file_log.setLevel(logging.DEBUG)
        file_log.setFormatter(formatter)
        self.logger.addHandler(file_log)

    def get_logger(self):
        return self.logger

    
class StandardLogger(BaseConfig):
    """
    Called as:
        logger = StandardLogger(__package__, __name__)
        logger.get_logger()
    """
    def __init__(self, pkg=None, name=None):
        super().__init__()
        setattr(self, 'pkg', pkg if pkg is not None else (WindowsPath(__file__)).anchor)
        if name is not None:
            setattr(self, 'name', name)
        else:
            raise ValueError
        
        self.logger = logging.getLogger("archive_tool")
        try:
            with open(os.path.abspath("standard_logging.json"), 'r', encoding='utf-8') as conf:
                logconfig = json.load(conf)
            logconfig['handlers']['file_handler']['filename'] = os.path.abspath('log.log')
            logging.config.dictConfig(logconfig)
        except:
            pass

    def get_logger(self):
        return self.logger


class JSONLogger(BaseConfig):
    """ 
        Origin: mCoding, @mCoding on Youtube 
        https://www.youtube.com/watch?v=9L77QExPmI0
        
        Called as: 
            logger = JSONLogger(__package__, __name__)
            logger.get_logger()
    """
    def __init__(self, pkg=None, name=None, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)

        setattr(self, 'pkg', pkg if pkg is not None else (WindowsPath(__file__)).anchor)
        if name is not None:
            setattr(self, 'name', name)
        else:
            raise ValueError
        self.logger = logging.getLogger(name)
        # with open(r"log_config.json", 'r') as conf_file:
        with open(self.LOGCONFIG, 'r') as conf_file:
            log_config = json.load(conf_file)
        # print(log_config)
        # log_config['handlers']['file_handler']['filename'] = r"log.json"
        log_config['handlers']['file_handler']['filename'] = self.LOGFILE
        print(f"{log_config = }")
        # refactored 'json_logging.json'
        #     "()": "archive_tool.utils.logging_config.CustomJSONFormatter"
        # to
        #     "()": "config.CustomJSONFormatter",
        logging.config.dictConfig(log_config)
        queue_handler = logging.getHandlerByName("queue_handler")
        if queue_handler is not None:
            queue_handler.listener.start()
            atexit.register(queue_handler.listener.stop)

    def get_logger(self):
        return self.logger


class CustomJSONFormatter(logging.Formatter):
    """ 
        Origin: mCoding, @mCoding on Youtube 
        https://www.youtube.com/watch?v=9L77QExPmI0
    """
    def __init__(self, *, fmt_keys: dict[str, str] | None = None):
        super().__init__() # init logging.Formatter

        # If `fmt_keys` is not None, return it; otherwise, return an empty dictionary.
        self.fmt_keys = fmt_keys if fmt_keys is not None else {} 

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": datetime.datetime.fromtimestamp(
                record.created, tz=datetime.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)
        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


class NonErrorFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno <= logging.INFO