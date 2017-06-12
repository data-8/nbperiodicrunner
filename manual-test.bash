#!/bin/bash

pip3 install --upgrade .
jupyter serverextension enable --py nbperiodicrunner
export NB_PERIODIC_CLI_NAME="touch test-file.txt"
export NB_PERIODIC_TIME_INTERVAL=5
jupyter-notebook
