#!/bin/bash

# This script is to initialize the varoius congestion controls
# algorithms once so that they are available for use.
# You need to run this script only once.
set -e

echo "We need sudo so you'll be prompted for your password"

CONGESTION_CONTROL="bbr bic vegas westwood reno cubic"

for cc in $CONGESTION_CONTROL; do
  echo "Initializing $cc"
  sudo sysctl -w net.ipv4.tcp_congestion_control=$cc
done

echo "Enabling IP Forwarding"
sudo sysctl -w net.ipv4.ip_forward=1


echo "Increase maximum buffer sizes."
sudo sysctl -w net.core.rmem_max=16777216
sudo sysctl -w net.core.wmem_max=16777216
sudo sysctl -w net.core.rmem_default=65536
sudo sysctl -w net.core.wmem_default=65536
sudo sysctl -w net.ipv4.tcp_rmem='4096 87380 16777216'
sudo sysctl -w net.ipv4.tcp_wmem='4096 65536 16777216'
sudo sysctl -w net.ipv4.tcp_mem='16777216 16777216 16777216'
sudo sysctl -w net.ipv4.route.flush=1

echo "Initialization complete"
