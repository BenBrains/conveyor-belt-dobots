#!/bin/bash
# Script to update port mappings when they change
# Usage: ./scripts/update_ports.sh

cd /home/baljeet/conveyor-belt-dobots

echo "Checking current USB port assignments..."
python3 -c "from serial.tools import list_ports; print('Available ports:', [p.device for p in list_ports.comports()])"

echo ""
echo "Current port mappings:"
python3 -c "from scripts.dobot_config import PORT_MAP; print('loader:', PORT_MAP['loader']); print('unloader:', PORT_MAP['unloader'])"

echo ""
echo "To swap the port assignments, run:"
echo "nano scripts/dobot_config.py"
echo ""
echo "Change the PORT_MAP dictionary to match your current configuration."
