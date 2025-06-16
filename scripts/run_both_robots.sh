#!/bin/bash
# Run the main script with both robots
# The loader robot is on ttyUSB0 and the unloader is on ttyUSB1

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

# Run both robots
python3 /os/home/baljeet/conveyor-belt-dobots/main.py --robot both
