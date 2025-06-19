#!/bin/bash

# Navigate to the project directory
cd /os/opt/conveyor-belt-dobots

# Check if virtual environment exists and activate it
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    
    Install required packages
    pip install -r requirements.txt
fi

# Script to home the loader robot
python3 /os/opt/conveyor-belt-dobots/scripts/home.py --robot loader
