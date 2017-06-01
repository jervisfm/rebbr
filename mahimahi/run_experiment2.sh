#!/bin/bash

# This script simple runs an experiment for looking at
# different congestion control algorithms.

set -x # Enable logging of executed commands.
set -e # Stop if any error occurs.
mkdir -p data

LOSS_RATES="0.001 0.01 0.1 1 2 5 10 15 20 25 30 40 50"
CONGESTION_CONTROL="cubic bbr bic vegas westwood reno"
LOG_FILE=data/experiment2.csv

# Clear any existing data.
rm -f $LOG_FILE

# Run experiment.
echo "Running experiment 2: Effect of different Congestion Control Algorithms."
for cc in $CONGESTION_CONTROL; do
  for loss_rate in $LOSS_RATES; do
    echo "Executing trial with cc=$cc Loss rate: $loss_rate ..."
    ./bbr_experiment.py --cc=$cc --loss=$loss_rate --time 30 --output_file=$LOG_FILE $@
  done
done
