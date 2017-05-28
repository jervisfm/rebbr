#!/bin/bash

# This script simple copys experimental results into the data folder.
set -e
set -x

FILES="figure8_experiment.csv experiment1.csv experiment2.csv experiment3.csv"

for file in FILES; do
  echo "Copying $file..."
  cp -f $file data/$file
done

echo "Data copy complete"
