#!/bin/bash

set +x
# This script simple runs experiment to reproduce figure 8
# in the original paper.

LOSS_RATES="0.001 0.01 0.1 1 2 5 10 15 20 25 30 40 50"
LOG_FILE=figure8_experiment.csv

# Clear any existing data.
rm -f $LOG_FILE

# Run experiment.
echo "Running Figure 8 experiment."
for loss_rate in $LOSS_RATES; do
  echo "Executing trial with Loss rate: $loss_rate ..."
  ./bbr_experiment.py --loss=$loss_rate >> $LOG_FILE
done