import os


def config_for_env(env_name):
    """
    Takes in an environment and returns a corresponding Config object.
    """
    name_to_env = {
        'production': ProductionConfig(),
        'development': DevelopmentConfig(),
        'testing': TestConfig(),
    }

    return name_to_env[env_name]


class Config(object):
    """General configurations"""

    PERIODIC_CLI_NAME = os.environ.get('NB_PERIODIC_CLI_NAME', default='')

    # in seconds
    PERIODIC_TIME_INTERVAL = os.environ.get('NB_PERIODIC_TIME_INTERVAL', default=1)

    def __getitem__(self, attr):
        """
        Temporary hack in order to maintain Flask config-like config usage.
        TODO(sam): Replace config classes with plain dicts or attrs
        """
        return getattr(self, attr)


class ProductionConfig(Config):
    PERIODIC_CLI_NAME = os.environ.get('NB_PERIODIC_CLI_NAME', default='')

    # in seconds
    PERIODIC_TIME_INTERVAL = os.environ.get('NB_PERIODIC_TIME_INTERVAL', default=60)


class DevelopmentConfig(Config):
    PERIODIC_CLI_NAME = os.environ.get('NB_PERIODIC_CLI_NAME', default='')

    # in seconds
    PERIODIC_TIME_INTERVAL = os.environ.get('NB_PERIODIC_TIME_INTERVAL', default=1)


class TestConfig(Config):
    PERIODIC_CLI_NAME = os.environ.get('NB_PERIODIC_CLI_NAME', default='touch test-file.txt')

    # in seconds
    PERIODIC_TIME_INTERVAL = os.environ.get('NB_PERIODIC_TIME_INTERVAL', default=1)
