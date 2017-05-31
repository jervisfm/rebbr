#!/bin/bash


# This script simple copys experimental results into the data folder.
set -x # Log executed commands
set -e # Stop on error.

FILES="figure8.png experiment1_figure.png experiment2_figure.png experiment3_figure.png"

for file in $FILES; do
  echo "Copying $file..."
  cp -f $file figures/$file
done
  
echo "Figure copy complete"

