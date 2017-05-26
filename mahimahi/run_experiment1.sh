#!/bin/bash

set +x
# This script simple runs an experiment for looking at effect of
# various bandwidth between CUBIC and BBR.


LOSS_RATES="0.001, 0.01, 0.1, 1, 2, 5, 10, 15, 20, 25, 30, 40, 50"
LOG_FILE=experiment1.csv

# Clear any existing data.
rm -f $LOG_FILE

# Run experiment.
for loss_rate in $LOSS_RATES; do
  ./bbr_experiment.py --loss=$loss_rate >> $LOG_FILE
done

