#!/bin/bash
# Incubator Controller Installation Script
# This script installs the incubator controller as a systemd service

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Set variables
INSTALL_DIR="/home/pi/incubator_controller"
SERVICE_NAME="incubator-controller"
SERVICE_FILE="$SERVICE_NAME.service"

# Make the start script executable
chmod +x $INSTALL_DIR/start.sh

# Copy the service file to systemd directory
cp $INSTALL_DIR/$SERVICE_FILE /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable the service to start on boot
systemctl enable $SERVICE_NAME

# Start the service
systemctl start $SERVICE_NAME

# Check status
systemctl status $SERVICE_NAME

echo "Installation complete. The incubator controller will now start automatically on boot."
echo "You can access the web interface at http://[raspberry-pi-ip]:5000"
echo ""
echo "Useful commands:"
echo "  Check status: sudo systemctl status $SERVICE_NAME"
echo "  Start service: sudo systemctl start $SERVICE_NAME"
echo "  Stop service: sudo systemctl stop $SERVICE_NAME"
echo "  Restart service: sudo systemctl restart $SERVICE_NAME"
echo "  View logs: sudo journalctl -u $SERVICE_NAME"
