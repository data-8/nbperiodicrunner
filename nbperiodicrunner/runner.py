import subprocess
from nbperiodicrunner.config import config_for_env


class Runner(object):

    #ENV_NAME = 'production'
    ENV_NAME = 'development'
    config = None

    def __init__(self):
        self.init_config()

    def init_config(self):
        self.config = config_for_env(self.ENV_NAME)

    def start(self):
        pass

