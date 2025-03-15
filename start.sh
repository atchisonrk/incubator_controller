#!/bin/bash
# Incubator Controller Startup Script
# This script starts the incubator controller web application

# Navigate to the incubator controller directory
cd /home/pi/incubator_controller

# Activate the virtual environment
source venv/bin/activate

# Start the Flask application
python app.py &

# Log the startup
echo "$(date): Incubator controller started" >> /home/pi/incubator_controller/logs/startup.log
