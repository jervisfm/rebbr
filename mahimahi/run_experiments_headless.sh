#!/bin/bash

set -x # Enable logging of executed commands.
set -e # Stop if any error occurs.

# This script simple runs all experiments with headless mode enabled.

./run_experiments.sh --headless=True
