from nbperiodicrunner.runner import Runner

def _jupyter_server_extension_paths():
    return [{
        'module': 'nbperiodicrunner',
    }]


def load_jupyter_server_extension(nbapp):
    runner = Runner()
    runner.start()
