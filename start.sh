#!/bin/bash
# Incubator Controller Startup Script
# This script starts the incubator controller web application

# Navigate to the incubator controller directory
cd /home/pi/incubator_controller

# Activate the virtual environment
source venv/bin/activate

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the Flask application
python app.py >> logs/incubator.log 2>&1 &

# Log the startup
echo "$(date): Incubator controller started" >> logs/startup.log
