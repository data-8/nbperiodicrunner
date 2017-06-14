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

    runner = None
    command_name = ''
    condition = None
    thread = None
    notebook_process = None

    def setUp(self):
        PeriodicRunner.CONFIG_FILE_PATH = "./"
        PeriodicRunner.CONFIG_FILE_NAMES = [self.TEST_CONFIG_FILE_NAME]
        self.create_test_config_file()
        self.runner = PeriodicRunner()
        self.command_name = 'touch {}'.format(self.TEST_FILE_NAME)

        def condition():
            return os.path.exists(self.TEST_FILE_NAME)

        self.condition = condition

    def tearDown(self):
        self.runner.stop()
        self.delete_test_file()
        self.delete_test_config_file()
        self.kill_notebook()

    def test_notebook_install(self):
        subprocess.check_call(['pip3', 'install', '--upgrade', '.'])
        subprocess.check_call(['jupyter', 'serverextension', 'enable', '--py', 'nbperiodicrunner'])

        def run_notebook():
            try:
                self.notebook_process = subprocess.Popen([
                    'jupyter-notebook',
                    '--debug',
                    '--no-browser',
                    '--PeriodicRunner.periodic_time_interval=1',
                    '--PeriodicRunner.periodic_cli_name="{}"'.format(self.command_name)])
            except Exception as e:
                # ignore any errors the notebook cli throws
                # b/c it will usually run the notebook anyways
                # and the errors do not concern nbperiodicrunner
                pass

        self.command_runs_on_time(
            self.NUM_OF_LOOPS,
            run_notebook,
            self.condition,
            self.delete_test_file)

    def test_init_config(self):
        self.runner._init_config()
        self.assertTrue(self.runner.periodic_time_interval)
        self.assertTrue(self.runner.periodic_cli_name)
        self.assertTrue(self.runner.cli_name_list)

    def test_constructor(self):
        self.assertTrue(self.runner.periodic_time_interval)
        self.assertTrue(self.runner.periodic_cli_name)
        self.assertTrue(self.runner.cli_name_list)

    def test_seonds_to_milliseconds(self):
        list_of_seconds = [1, 5, 20, 4, 6, 9, 3.8]
        list_of_milliseconds = []
        for sec in list_of_seconds:
            list_of_milliseconds.append(self.runner._seconds_to_milliseconds(sec))

        expected_list_of_milliseconds = [1000, 5000, 20000, 4000, 6000, 9000, 3800]
        self.assertListEqual(list_of_milliseconds, expected_list_of_milliseconds)

    def test_init_periodic_callback(self):
        self.runner.periodic_callback = None
        self.runner._init_periodic_callback()
        self.assertTrue(self.runner.periodic_callback)

    def test_start(self):
        self.assertEqual(self.runner.periodic_cli_name, self.command_name)

        def command():
            self.runner.start()

        self.command_runs_on_time(self.NUM_OF_LOOPS, command, self.condition, self.delete_test_file)
        self.assertTrue(self.runner.is_running())

    def is_within_buffer_time(self, duration):
        return abs(duration - (self.runner.periodic_time_interval)) < self.BUFFER_TIME

    def is_timing_out(self, start_time):
        return time.time() - start_time > self.runner.periodic_time_interval + self.BUFFER_TIME

    def delete_test_file(self):
        if os.path.exists(self.TEST_FILE_NAME):
            subprocess.check_call(['rm', self.TEST_FILE_NAME])

    def delete_test_config_file(self):
        if os.path.exists(self.TEST_CONFIG_FILE_NAME):
            subprocess.check_call(['rm', self.TEST_CONFIG_FILE_NAME])

    def create_test_config_file(self):
        with open(self.TEST_CONFIG_FILE_NAME, 'w') as config_file:
            config_file.write(self.TEST_CONFIG_FILE_CONTENTS)

    def start_thread(self, command):
        self.thread = Thread(target=command)
        self.thread.daemon = True
        self.thread.start()

    def kill_notebook(self):
        if self.notebook_process:
            subprocess.check_call(['kill', '-9', str(self.notebook_process.pid)])
        else:
            logger.info("No process is set")

    def command_runs_on_time(self, num, command, condition, clean_up):
        self.start_thread(command)
        self.wait_until_startup_done(condition)

        for _ in range(num):
            clean_up()
            duration = self.get_time_to_meet_condition(condition)
            logger.info("The loop took {} seconds to run.".format(duration))
            self.assertTrue(self.is_within_buffer_time(duration))

    def get_time_to_meet_condition(self, condition):
        start_time = time.time()

        # Set the default end_time to be a timeout, so fails test if times out.
        end_time = start_time + self.get_timeout_time()

        # check if file is created with `touch` cli in interval time
        while not self.is_timing_out(start_time):
            time.sleep(self.TICK_TIME)
            if condition():
                end_time = time.time()
                break

        return end_time - start_time

    def wait_until_startup_done(self, condition):
        logger.info("Waiting for startup...")
        total_startup_duration = 0
        duration = self.get_timeout_time()

        while duration >= self.get_timeout_time() and total_startup_duration < self.STARTUP_TIMEOUT:
            duration = self.get_time_to_meet_condition(condition)
            total_startup_duration += duration
        logger.info("Startup took {} seconds".format(total_startup_duration))

    def get_timeout_time(self):
        return self.runner.periodic_time_interval + self.BUFFER_TIME + 1
