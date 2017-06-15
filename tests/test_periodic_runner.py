import os
import unittest
import subprocess
import time
from threading import Thread
from nbperiodicrunner.periodic_runner import PeriodicRunner
from nbperiodicrunner.util import logger


class TestPeriodicRunner(unittest.TestCase):

    BUFFER_TIME = 0.5     # in seconds
    TICK_TIME = 0.2       # in seconds
    STARTUP_TIMEOUT = 5   # in seconds
    NUM_OF_LOOPS = 3
    TEST_FILE_NAME = "test-file.txt"
    TEST_CONFIG_FILE_NAME = "nbperiodicrunner_config.py"
    TEST_CONFIG_FILE_CONTENTS = """
c.PeriodicRunner.periodic_time_interval = 1
c.PeriodicRunner.periodic_cli_name = 'touch test-file.txt'"""

    _runner = None
    _command_name = ''
    _condition = None
    _thread = None
    _notebook_process = None

    def setUp(self):
        PeriodicRunner.CONFIG_FILE_PATH = "./"
        PeriodicRunner.CONFIG_FILE_NAMES = [self.TEST_CONFIG_FILE_NAME]
        self._create_test_config_file()
        self._runner = PeriodicRunner()
        self._command_name = 'touch {}'.format(self.TEST_FILE_NAME)

        def condition():
            return os.path.exists(self.TEST_FILE_NAME)

        self._condition = condition

    def tearDown(self):
        self._runner.stop()
        self._delete_test_file()
        self._delete_test_config_file()
        self._kill_notebook()

    def test_notebook_install(self):
        subprocess.check_call(['pip3', 'install', '--upgrade', '.'])
        subprocess.check_call(['jupyter', 'serverextension', 'enable', '--py', 'nbperiodicrunner'])

        def run_notebook():
            try:
                self._notebook_process = subprocess.Popen([
                    'jupyter-notebook',
                    '--debug',
                    '--no-browser',
                    '--PeriodicRunner.periodic_time_interval=1',
                    '--PeriodicRunner.periodic_cli_name="{}"'.format(self._command_name)])
            except Exception as e:
                # ignore any errors the notebook cli throws
                # b/c it will usually run the notebook anyways
                # and the errors do not concern nbperiodicrunner
                pass

        self._command_runs_on_time(
            self.NUM_OF_LOOPS,
            run_notebook,
            self._condition,
            self._delete_test_file)

    def test_init_config(self):
        self._delete_test_config_file()
        self._runner = PeriodicRunner()
        self.assertEqual(self._runner.periodic_time_interval, 5)
        self.assertEqual(self._runner.periodic_cli_name, u'')

        self._create_test_config_file()
        self._runner._init_config()
        self.assertEqual(self._runner.periodic_time_interval, 1)
        self.assertEqual(self._runner.periodic_cli_name, self._command_name)
        self.assertTrue(self._runner._cli_name_list)

    def test_constructor(self):
        self.assertEqual(self._runner.periodic_time_interval, 1)
        self.assertEqual(self._runner.periodic_cli_name, self._command_name)
        self.assertEqual(self._runner._cli_name_list, self._command_name.split(' '))
        self.assertTrue(self._runner._periodic_callback)

    def test_seonds_to_milliseconds(self):
        list_of_seconds = [1, 5, 20, 4, 6, 9, 3.8]
        list_of_milliseconds = []
        for sec in list_of_seconds:
            list_of_milliseconds.append(self._runner._seconds_to_milliseconds(sec))

        expected_list_of_milliseconds = [1000, 5000, 20000, 4000, 6000, 9000, 3800]
        self.assertListEqual(list_of_milliseconds, expected_list_of_milliseconds)

    def test_init_periodic_callback(self):
        self._runner._periodic_callback = None
        self._runner._init_periodic_callback()
        self.assertTrue(self._runner._periodic_callback)

    def test_start(self):
        self.assertEqual(self._runner.periodic_cli_name, self._command_name)

        def command():
            self._runner.start()

        self._command_runs_on_time(self.NUM_OF_LOOPS, command, self._condition, self._delete_test_file)
        self.assertTrue(self._runner.is_running())

    def _is_within_buffer_time(self, duration):
        return abs(duration - (self._runner.periodic_time_interval)) < self.BUFFER_TIME

    def _is_timing_out(self, start_time):
        return time.time() - start_time > self._runner.periodic_time_interval + self.BUFFER_TIME

    def _delete_test_file(self):
        if os.path.exists(self.TEST_FILE_NAME):
            subprocess.check_call(['rm', self.TEST_FILE_NAME])

    def _delete_test_config_file(self):
        if os.path.exists(self.TEST_CONFIG_FILE_NAME):
            subprocess.check_call(['rm', self.TEST_CONFIG_FILE_NAME])

    def _create_test_config_file(self):
        with open(self.TEST_CONFIG_FILE_NAME, 'w') as config_file:
            config_file.write(self.TEST_CONFIG_FILE_CONTENTS)

    def _start_thread(self, command):
        self._thread = Thread(target=command)
        self._thread.daemon = True
        self._thread.start()

    def _kill_notebook(self):
        if self._notebook_process:
            subprocess.check_call(['kill', '-9', str(self._notebook_process.pid)])
        else:
            logger.info("No process is set")

    def _command_runs_on_time(self, num, command, condition, clean_up):
        self._start_thread(command)
        self._wait_until_startup_done(condition)

        for _ in range(num):
            clean_up()
            duration = self._get_time_to_meet_condition(condition)
            logger.info("The loop took {} seconds to run.".format(duration))
            self.assertTrue(self._is_within_buffer_time(duration))

    def _get_time_to_meet_condition(self, condition):
        start_time = time.time()

        # Set the default end_time to be a timeout, so fails test if times out.
        end_time = start_time + self._get_timeout_time()

        # check if file is created with `touch` cli in interval time
        while not self._is_timing_out(start_time):
            time.sleep(self.TICK_TIME)
            if condition():
                end_time = time.time()
                break

        return end_time - start_time

    def _wait_until_startup_done(self, condition):
        logger.info("Waiting for startup...")
        total_startup_duration = 0
        duration = self._get_timeout_time()

        while duration >= self._get_timeout_time() and total_startup_duration < self.STARTUP_TIMEOUT:
            duration = self._get_time_to_meet_condition(condition)
            total_startup_duration += duration
        logger.info("Startup took {} seconds".format(total_startup_duration))

    def _get_timeout_time(self):
        return self._runner.periodic_time_interval + self.BUFFER_TIME + 1
