#!/usr/bin/env bash

# Create directories for logs and metrics if they don't already exist
mkdir -p logs metrics

# Enable BCP38 and start Ryu controller in the background
BCP38_ENABLED=1 ryu-manager ryu_controller.py &> logs/ryu-controller.log &

# Capture the Ryu process ID for cleanup later
RYU_PID=$!

# Run the Mininet simulation script
python3 mininet-sim.py

# Run the network metrics script after the simulation
# Adjust interface, timeout, and CSV file name as needed
METRICS_SCRIPT="network_metrics_to_csv.py"
INTERFACE="s1-eth1"  # Example interface name
CAPTURE_DURATION=30  # Duration of the capture in seconds
CSV_FILE="metrics/network_metrics_$(date +%Y%m%d_%H%M%S).csv"

echo "Running network metrics script..."
python3 $METRICS_SCRIPT -i $INTERFACE -t $CAPTURE_DURATION -o $CSV_FILE

echo "Metrics saved to $CSV_FILE"

# Cleanup: Stop the Ryu controller and clear logs
kill $RYU_PID
rm logs/*

echo "Simulation and metrics collection completed."

