import os
import unittest
import subprocess
import time
from nbperiodicrunner.runner import Runner


class TestRunner(unittest.TestCase):

    BUFFER_TIME = 0.5     # in seconds
    TICK_TIME = 0.2       # in seconds
    NUM_OF_LOOPS = 3
    TEST_FILE_NAME = "test-file.txt"
    runner = None
    command_name = ''
    condition = None

    def setUp(self):
        Runner.ENV_NAME = "testing"
        self.runner = Runner()
        self.command_name = 'touch {}'.format(self.TEST_FILE_NAME)

        def condition():
            return os.path.exists(self.TEST_FILE_NAME)

        self.condition = condition

    def tearDown(self):
        self.runner.stop()
        self.delete_test_file()
        os.environ['NB_PERIODIC_CLI_NAME'] = ''

    def test_init_config(self):
        self.runner.config = None
        self.runner._init_config()
        self.assertIsNotNone(self.runner.config)
        self.assertTrue(self.runner.config['PERIODIC_CLI_NAME'])
        self.assertTrue(self.runner.config['PERIODIC_TIME_INTERVAL'])

    def test_constructor(self):
        self.assertIsNotNone(self.runner.config)
        self.assertTrue(self.runner.config['PERIODIC_CLI_NAME'])
        self.assertTrue(self.runner.config['PERIODIC_TIME_INTERVAL'])

    def test_notebook_install(self):
        subprocess.check_call(['pip', 'install', '--upgrade', '.'])
        subprocess.check_call(['jupyter', 'serverextension', 'enable', '--py', 'nbperiodicrunner'])

    def test_run_interval_command(self):
        self.delete_test_file()

        def command():
            self.runner._loop_command_on_interval(self.command_name)

        self.command_runs_on_time(self.NUM_OF_LOOPS, command, self.condition, self.delete_test_file)

    def test_start(self):
        self.delete_test_file()
        self.runner = Runner()
        self.assertEqual(self.runner.config['PERIODIC_CLI_NAME'], self.command_name)

        def command():
            self.runner.start()

        self.command_runs_on_time(self.NUM_OF_LOOPS, command, self.condition, self.delete_test_file)

    def is_within_buffer_time(self, duration):
        return abs(duration - (self.runner.config['PERIODIC_TIME_INTERVAL'])) < self.BUFFER_TIME

    def is_timing_out(self, start_time):
        return time.time() - start_time > self.runner.config['PERIODIC_TIME_INTERVAL'] + self.BUFFER_TIME

    def delete_test_file(self):
        if os.path.exists(self.TEST_FILE_NAME):
            subprocess.check_call(['rm', self.TEST_FILE_NAME])

    def command_runs_on_time(self, num, command, condition, clean_up):
        command()
        for _ in range(num):
            duration = self.get_time_to_meet_condition(condition)
            print("The loop took", duration, "seconds to run.")
            self.assertTrue(self.is_within_buffer_time(duration))
            clean_up()

    def get_time_to_meet_condition(self, condition):
        start_time = time.time()

        # Set the default end_time to be a timeout, so fails test if times out.
        end_time = start_time + self.runner.config['PERIODIC_TIME_INTERVAL'] + self.BUFFER_TIME + 1

        # check if file is created with `touch` cli in interval time
        while not self.is_timing_out(start_time):
            time.sleep(self.TICK_TIME)
            if condition():
                end_time = time.time()
                break

        return end_time - start_time
