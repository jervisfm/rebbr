#!/bin/bash

set -x # Enable logging of executed commands.
set -e # Stop if any error occurs.

# First, install all dependencies
./mahimahi/init_deps.sh

# This script simply runs all experiments with headless mode enabled.
./mahimahi/run_experiments_headless.sh
