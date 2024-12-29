import os, sys
from pathlib import WindowsPath
import atexit
import datetime
import json
import logging
import logging.config
import logging.handlers
from typing import override

from src.setup import BaseConfig


### Logging ###
rec = logging.LogRecord('',0,None,0,'',[],None) # create a minimal LogRecord
all_attributes = dir(rec)
LOG_RECORD_BUILTIN_ATTRS = {a for a in all_attributes if '__' not in a}
# print(f"{LOG_RECORD_BUILTIN_ATTRS}")


class BasicLogger(BaseConfig):
    def __init__(self, pkg=None, name=None):
        super().__init__()
        setattr(self, 'pkg', pkg if pkg is not None else (WindowsPath(__file__)).anchor)
        if name is not None:
            setattr(self, 'name', name)
        else:
            raise ValueError
        self.logger = logging.getLogger(name)


class JSONLogger(BasicLogger):
    def __init__(self, pkg=None, name=None):
        super().__init__(pkg, name)
        # setattr(self, 'pkg', pkg if pkg is not None else (WindowsPath(__file__)).anchor)
        # if name is not None:
        #     setattr(self, 'name', name)
        # else:
        #     raise ValueError
        # self.logger = logging.getLogger(name)
        # config_path = self.LOGPATH/"configs"
        with open(self.CONFIGPATH/"config_json_logging.json", 'r') as f_in:
            config = json.load(f_in)
        config['handlers']['file_handler']['filename'] = f"{self.LOGPATH}/archive_shelf.log"
        config['handlers']['json_handler']['filename'] = f"{self.LOGPATH}/archive_shelf.jsonl"
        logging.config.dictConfig(config)
        queue_handler = logging.getHandlerByName("queue_handler")
        if queue_handler is not None:
            queue_handler.listener.start()
            atexit.register(queue_handler.listener.stop)

    def get_logger(self):
        return self.logger


class CustomJSONFormatter(logging.Formatter):
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


if __name__=='__main__':
    json_logger = JSONLogger()(__package__, __name__)
    json_logger.get_logger()

