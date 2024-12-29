""" Configure story_builder package """
__version__ = "0.1.0"

import ast
from pathlib import WindowsPath
from dotenv import find_dotenv, load_dotenv, dotenv_values


class UserValidationError(Exception):
    pass


class Config(UserValidationError):
    def __init__(self):
        super().__init__()
        envs = dotenv_values(find_dotenv())
        self.env_vars = {}
        for name, val in envs.items():
            if WindowsPath(val).is_dir() or WindowsPath(val).is_file() \
                or 'LOGFILE' in name:
                self.env_vars[name] = WindowsPath(val)
            elif 'HEADER' in name:
                self.env_vars[name] = ast.literal_eval(val)
            else:
                self.env_vars[name] = val

    def __repr__(self):
        return '\n'.join([f"{k}: {v}" for k, v in self.env_vars.items() \
                            if "__" not in k])

    def setup_log(self, __package__, __name__):
        from story_downloaders.configure_log import JSONLogger
        # print(self.env_vars)
        project_log = JSONLogger(__package__, __name__, **self.env_vars)
        return project_log.get_logger()



if __name__ == "__main__":
    config = Config()
    logger = config.setup_log(__package__, __name__)
    logger.debug(f"{config.env_vars}")
    