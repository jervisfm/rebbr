#!/bin/bash

set +x
# This script simple runs an experiment for looking at effect of
# various bandwidth between CUBIC and BBR.

LOSS_RATES="0.001 0.01 0.1 1 2 5 10 15 20 25 30 40 50"
BW_MBPS="0.01 0.1 1 10 100"
LOG_FILE=experiment1.csv

# Clear any existing data.
rm -f $LOG_FILE

# Run experiment.
echo "Running  experiment 1: effect of bandwidth"

for loss_rate in $LOSS_RATES; do
  for bw in $BW_MBPS; do
    echo "Executing trial with Loss rate: $loss_rate Bandwidth: $bw ..."
    ./bbr_experiment.py --loss=$loss_rate --bw=$bw >> $LOG_FILE
  done
done

