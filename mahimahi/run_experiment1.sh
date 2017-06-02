#!/bin/bash

# This script simple runs an experiment for looking at effect of
# various bandwidth between CUBIC and BBR.

set -x # Enable logging of executed commands.
set -e # Stop if any error occurs.
mkdir -p data

LOSS_RATES="0.001 0.01 0.1 1 2 5 10 15 20 25 30 40 50"
BW_MBPS="0.01 0.1 1 10 100"
CONGESTION_CONTROL="cubic bbr"
LOG_FILE=data/experiment1.csv

# Clear any existing data.
rm -f $LOG_FILE

# Run experiment.
echo "Running  experiment 1: effect of bandwidth"

for cc in $CONGESTION_CONTROL; do
  for loss_rate in $LOSS_RATES; do
    for bw in $BW_MBPS; do
      echo "Executing trial with cc=$cc Loss rate: $loss_rate Bandwidth: $bw ..."
      ./bbr_experiment.py --cc=$cc --loss=$loss_rate --bw=$bw --time 30 --output_file=$LOG_FILE $@
    done
  done
done
