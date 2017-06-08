import subprocess
import time
from threading import Thread, Event
from nbperiodicrunner.config import config_for_env


class Runner(object):

    #ENV_NAME = 'production'
    ENV_NAME = 'development'
    config = None
    thread = None
    stop_event = None


    def __init__(self):
        self._init_config()


    def _init_config(self):
        self.config = config_for_env(self.ENV_NAME)


    def start(self):
        if self.config['PERIODIC_CLI_NAME']:
            self._loop_command_on_interval(self.config['PERIODIC_CLI_NAME'])


    def stop(self):
        if self.thread and self.stop_event:
            self.stop_event.set()


    def _loop_command_on_interval(self, command):
        self.stop_event = Event()
        self.thread = Thread(target=self._loop_command, args=(command,))
        self.thread.daemon = True
        self.thread.start()


    def _loop_command(self, command):
        while not self.stop_event.is_set():
            time.sleep(self.config['PERIODIC_TIME_INTERVAL'])
            subprocess.check_call(command.split(' '))
