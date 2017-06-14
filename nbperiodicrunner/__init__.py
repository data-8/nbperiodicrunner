from nbperiodicrunner.periodic_runner import PeriodicRunner

def _jupyter_server_extension_paths():
    return [{
        'module': 'nbperiodicrunner',
    }]


def load_jupyter_server_extension(nbapp):
    runner = PeriodicRunner(nbapp.config)
    runner.start()
