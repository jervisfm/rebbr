#!/bin/bash


set -x # Enable logging of executed commands.
set -e # Stop if any error occurs.

# This script simple installs needed depends on GCloud VM.


echo "Installing Python PIP"
sudo apt-get update
sudo apt-get install -y python-pip

echo "Installing Python TK for graph plotting"
sudo apt-get install -y python-tk
pip install matplotlib


# Install Mahimahi
echo "Installing Mahimahi"
sudo add-apt-repository -y ppa:keithw/mahimahi
sudo apt-get update
sudo apt-get install -y mahimahi
