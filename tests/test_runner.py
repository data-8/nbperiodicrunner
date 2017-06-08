import os
import unittest
import subprocess
import time
from nbperiodicrunner.runner import Runner


class TestRunner(unittest.TestCase):

    BUFFER_TIME = 2 # in seconds
    TICK_TIME = 1 # in seconds
    runner = None
    test_file_name = "test-file.txt"

    def setUp(self):
        self.runner = Runner()

    def tearDown(self):
        self.runner.stop()
        self.delete_test_file()

    def test_init_config(self):
        self.runner.config = None
        self.runner._init_config()
        self.assertIsNotNone(self.runner.config)
        self.assertFalse(self.runner.config['PERIODIC_CLI_NAME'])
        self.assertTrue(self.runner.config['PERIODIC_TIME_INTERVAL'])

    def test_constructor(self):
        self.assertIsNotNone(self.runner.config)
        self.assertFalse(self.runner.config['PERIODIC_CLI_NAME'])
        self.assertTrue(self.runner.config['PERIODIC_TIME_INTERVAL'])

    def test_notebook_install(self):
        subprocess.check_call(['pip', 'install', '--upgrade', '.'])
        subprocess.check_call(['jupyter', 'serverextension', 'enable', '--py', 'nbperiodicrunner'])

    def test_run_interval_command(self):
        self.delete_test_file()
        start_time = time.time()

        # Set the default end_time to be a timeout, so fails test if times out.
        end_time = start_time + self.runner.config['PERIODIC_TIME_INTERVAL'] + self.BUFFER_TIME + 1

        # check if file is created with `touch` cli in interval time
        self.runner._loop_command_on_interval('touch {}'.format(self.test_file_name))
        while not self.is_timing_out(start_time):
            time.sleep(self.TICK_TIME)
            if os.path.exists(self.test_file_name):
                end_time = time.time()
                break

        print("The loop took", end_time - start_time, "seconds to run.")
        self.assertTrue(self.is_within_buffer_time(end_time, start_time))

    def is_within_buffer_time(self, end_time, start_time):
        return abs((end_time - start_time) - (self.runner.config['PERIODIC_TIME_INTERVAL'])) < self.BUFFER_TIME

    def is_timing_out(self, start_time):
        return time.time() - start_time > self.runner.config['PERIODIC_TIME_INTERVAL'] + self.BUFFER_TIME

    def delete_test_file(self):
        if os.path.exists(self.test_file_name):
            subprocess.check_call(['rm', self.test_file_name])
