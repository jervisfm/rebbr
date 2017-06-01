#!/bin/bash

# This script simple runs experiment to reproduce figure 8
# in the original paper.

set -x # Enable logging of executed commands.
set -e # Stop if any error occurs.
mkdir -p data

LOSS_RATES="0.001 0.01 0.1 1 2 5 10 15 20 25 30 40 50"
CONGESTION_CONTROL="cubic bbr"
LOG_FILE=data/figure8.csv

# Clear any existing data.
rm -f $LOG_FILE

# Run experiment.
echo "Running Figure 8 experiment."
for cc in $CONGESTION_CONTROL; do
  for loss_rate in $LOSS_RATES; do
    echo "Executing trial with cc=$cc Loss rate: $loss_rate ..."
    ./bbr_experiment.py --cc=$cc --loss=$loss_rate --output_file=$LOG_FILE $@
  done
done
