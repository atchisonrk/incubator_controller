#!/bin/bash
# Incubator Controller Installation Script
# This script installs the incubator controller on a Raspberry Pi

# Create logs directory
mkdir -p logs

# Make the start script executable
chmod +x start.sh

# Display installation instructions
echo "===== Raspberry Pi Incubator Controller Installation ====="
echo ""
echo "To complete the installation on your Raspberry Pi, follow these steps:"
echo ""
echo "1. Copy the entire incubator_controller directory to your Raspberry Pi:"
echo "   scp -r incubator_controller pi@your-pi-ip-address:/home/pi/"
echo ""
echo "2. Install required packages on your Raspberry Pi:"
echo "   sudo apt update"
echo "   sudo apt install -y python3-venv python3-dev build-essential"
echo ""
echo "3. Set up the Python virtual environment on your Raspberry Pi:"
echo "   cd /home/pi/incubator_controller"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install flask adafruit-circuitpython-sht31d RPi.GPIO"
echo ""
echo "4. Install the systemd service for auto-start on boot:"
echo "   sudo cp /home/pi/incubator_controller/incubator-controller.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable incubator-controller.service"
echo "   sudo systemctl start incubator-controller.service"
echo ""
echo "5. Access the web interface:"
echo "   Open a web browser and navigate to http://your-pi-ip-address:5000"
echo ""
echo "6. Check service status if needed:"
echo "   sudo systemctl status incubator-controller.service"
echo ""
echo "===== Installation Instructions Complete ====="
