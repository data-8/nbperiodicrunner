import unittest
import subprocess
from nbperiodicrunner.runner import Runner


class TestRunner(unittest.TestCase):

    def setUp(self):
        pass

    def test_constructor(self):
        runner = Runner()
        self.assertIsNotNone(runner.config)
        self.assertFalse(runner.config['PERIODIC_CLI_NAME'])
        self.assertTrue(runner.config['PERIODIC_TIME_INTERVAL'])

    def test_notebook_install(self):
        subprocess.check_call(['pip', 'install', '--upgrade', '.'])
        subprocess.check_call(['jupyter', 'serverextension', 'enable', '--py', 'nbperiodicrunner'])
