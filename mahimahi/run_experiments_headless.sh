#!/bin/bash

set -x # Enable logging of executed commands.
set -e # Stop if any error occurs.

# This script simple runs all experiments with headless mode enabled.

./run_experiments.sh --headless

# Then, serve the content on http
echo "Open a browser and navigate to http://<ip_address>/figures/ to view the figures."
sudo python -m SimpleHTTPServer 80
