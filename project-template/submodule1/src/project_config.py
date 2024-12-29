from pathlib import WindowsPath

class UserValidationError(Exception):
    pass


class Config(UserValidationError):
    def __init__(self):
        super().__init__()
        self.ROOT = WindowsPath(r"C:\MyProjects\Webscrapers")
        self.run()

    def run(self):
        project_dir = WindowsPath(__file__).parent.name
        name = input(f"Project name: [{project_dir}]: ") or project_dir
        self.PROJECT =  self.ROOT / name / name
        self.STORIES = self.PROJECT/"stories"
        self.HTML_FILES = self.STORIES/"html_files"
        self.SOUP_FILES = self.STORIES/"soup_files"
        self.LOGCONFIG = self.PROJECT/"log_config.json"
        self.LOGFILE = self.PROJECT/"log.json"
        print(self)

    def __repr__(self):
        return '\n'.join([f"{k}: {v}" for k, v in self.__dict__.items() \
                            if "__" not in k])


from logging_config import JSONLogger

if "__main__" in __name__:
    Config()