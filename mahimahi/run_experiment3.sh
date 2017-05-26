#!/bin/bash

set +x
# This script simple runs experiments to look at
# effect of RTT.

LOSS_RATES="0.001 0.01 0.1 1 2 5 10 15 20 25 30 40 50"
RTTS_MS="1 10 100 1000 10000 30000 60000 100000"
CONGESTION_CONTROL="cubic bbr"
LOG_FILE=experiment3.csv

# Clear any existing data.
rm -f $LOG_FILE

# Run experiment.
echo "Running  experiment 3: effect of RTT"

for cc in $CONGESTION_CONTROL; do
  for loss_rate in $LOSS_RATES; do
    for rtt in $RTT_MS; do
      echo "Executing trial with cc=$cc Loss rate: $loss_rate RTT (ms): $rtt ..."
      ./bbr_experiment.py --cc=$cc --loss=$loss_rate --rtt=$rtt >> $LOG_FILE
    done
  done
done

