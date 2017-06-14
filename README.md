# nbperiodicrunner
Simple Jupyter extension to periodically runs cli apps for a certain time interval.

nbperiodicrunner may be configured using the following traitlets:
```
c.PeriodicRunner.periodic_time_interval = 5  # in seconds
c.PeriodicRunner.periodic_cli_name = 'touch test-file.txt'
```

nbperiodicrunner will attempt to read the config file `~/.jupyter/nbperiodicrunner_config.py`

If `nbperiodicrunner_config.py` is not found, nbperiodicrunner can be configured from the default NotebookApp config file.
