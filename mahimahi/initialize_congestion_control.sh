#!/bin/bash

set +x
# This script is to initialize the varoius congestion controls
# algorithms once so that they are available for use.
# You need to run this script only once.

echo "We need sudo so you'll be prompted for your password"

CONGESTION_CONTROL="bbr bic vegas westwood reno cubic"


for cc in $CONGESTION_CONTROL; do    
  echo "Initializing $cc"
  sudo sysctl -w net.ipv4.tcp_congestion_control=$cc
done

echo "Initialization complete"
