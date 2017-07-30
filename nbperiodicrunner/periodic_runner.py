import subprocess
import logging
from tornado.ioloop import PeriodicCallback, IOLoop
from traitlets.config.configurable import Configurable, Config
from traitlets import Float, Unicode
from traitlets.config.loader import load_pyconfig_files


logging.basicConfig(
    format='[%(asctime)s] %(levelname)s -- %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger('app')


class PeriodicRunner(Configurable):

    CONFIG_FILE_PATH = '~/.jupyter'
    CONFIG_FILE_NAMES = ['nbperiodicrunner_config.py']

    _periodic_callback = None
    _cli_name_list = None

    periodic_time_interval = Float(5, config=True, help="""
        Interval in seconds at which PeriodicRunner executes its command
        """)

    periodic_cli_name = Unicode(u'', config=True, help="""
        Name of the command for PeriodicRunner to execute
        """)

    def __init__(self, nbapp_config=None):
        self._init_config(nbapp_config)
        self._init_periodic_callback()

    def _init_config(self, nbapp_config=None):
        c = Config()
        if nbapp_config:
            c.merge(nbapp_config)
        nbperiodicrunner_config = load_pyconfig_files(self.CONFIG_FILE_NAMES, self.CONFIG_FILE_PATH)
        c.merge(nbperiodicrunner_config)
        self.update_config(c)
        self._cli_name_list = self.periodic_cli_name.split(' ')

    def start(self):
        if self._periodic_callback:
            self._periodic_callback.start()
            IOLoop.current().start()
            logger.info('Started runner loop')
        else:
            logger.info('Did not start loop: No periodic callback exists.')

    def stop(self):
        if self._periodic_callback:
            self._periodic_callback.stop()
            logger.info('Stopped runner loop')
        else:
            logger.info('Did not stop loop: No periodic callback exists.')

    def is_running(self):
        return self._periodic_callback and self._periodic_callback.is_running()

    def _init_periodic_callback(self):
        if self.periodic_cli_name:
            def _command_wrapper():
                subprocess.check_call(self._cli_name_list)
                logger.info("Ran command: \"{}\"".format(self.periodic_cli_name))

            time_interval = self._seconds_to_milliseconds(self.periodic_time_interval)

            self._periodic_callback = PeriodicCallback(_command_wrapper, time_interval)
            logger.info('Initialized periodic callback on IOLoop: {}'.format(str(IOLoop.current())))
        else:
            logger.info('Did not initialize periodic callback since no command specified.')

    def _seconds_to_milliseconds(self, seconds):
        return seconds * 1000
