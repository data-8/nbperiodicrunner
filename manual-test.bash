#!/bin/bash

pip3 install --upgrade .
jupyter serverextension enable --py nbperiodicrunner
jupyter-notebook
