import subprocess
import time
from .util import logger
from tornado.ioloop import PeriodicCallback, IOLoop
from nbperiodicrunner.config import config_for_env


class Runner(object):

    #ENV_NAME = 'production'
    ENV_NAME = 'development'
    config = None
    thread = None
    stop_event = None
    periodic_callback = None
    cli_name_list = None


    def __init__(self):
        self._init_config()
        self._init_periodic_callback()


    def _init_config(self):
        self.config = config_for_env(self.ENV_NAME)
        self.cli_name_list = self.config['PERIODIC_CLI_NAME'].split(' ')


    def start(self):
        if self.periodic_callback:
            self.periodic_callback.start()
            IOLoop.current().start()
            logger.info('Started runner loop')
        else:
            logger.info('Did not start loop: No periodic callback exists.')


    def stop(self):
        if self.periodic_callback:
            self.periodic_callback.stop()
            logger.info('Stopped runner loop')
        else:
            logger.info('Did not stop loop: No periodic callback exists.')


    def is_running(self):
        return self.periodic_callback and self.periodic_callback.is_running()


    def _init_periodic_callback(self):
        if self.config['PERIODIC_CLI_NAME']:
            def _command_wrapper():
                subprocess.check_call(self.cli_name_list)
                logger.info("Ran command: \"{}\"".format(self.config['PERIODIC_CLI_NAME']))

            time_interval = self._seconds_to_milliseconds(self.config['PERIODIC_TIME_INTERVAL'])

            self.periodic_callback = PeriodicCallback(_command_wrapper, time_interval)
            logger.info('Initialized periodic callback on IOLoop: {}'.format(str(IOLoop.current())))
        else:
            logger.info('Did not initialize periodic callback since no command specified.')


    def _seconds_to_milliseconds(self, seconds):
        return seconds * 1000
