#!/bin/bash

set -x # Enable logging of executed commands.
set -e # Stop if any error occurs.

# This script simple runs a handful of experiments.

./run_figure8_experiment.sh $@
./run_experiment1.sh $@
./run_experiment2.sh $@
./run_experiment3.sh $@
./run_experiment4.sh $@
