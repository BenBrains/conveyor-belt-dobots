#!/bin/bash
# Run the main script with just the loader robot

# Navigate to the project directory
cd /os/home/baljeet/conveyor-belt-dobots

# Check if virtual environment exists and activate it
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    
    # Install required packages
    pip install -r requirements.txt
fi

# Run the loader script
python3 /os/home/baljeet/conveyor-belt-dobots/main.py --robot loader
