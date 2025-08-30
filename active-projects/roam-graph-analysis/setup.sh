#!/bin/bash
# Quick setup script for Roam link counter

echo "Setting up Roam link counter..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Install msgpack if needed
echo "Installing required library (msgpack)..."
pip3 install msgpack

echo "Setup complete!"
echo ""
echo "To analyze your Roam export, run:"
echo "python3 roam_link_counter.py backup-Rodney_Graph_1-2024-12-29-20-08-24.msgpack"
