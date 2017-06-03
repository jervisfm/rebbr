#!/bin/bash

set -x # Enable logging of executed commands.
set -e # Stop if any error occurs.

cd mahimahi
# First, install all dependencies
./init_deps.sh

echo $(date)
# This script simply runs all experiments with headless mode enabled.
./run_experiments_headless.sh
echo $(date)
