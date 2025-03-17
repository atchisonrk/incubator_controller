# Raspberry Pi Incubator Controller

A complete incubator controller system using a Raspberry Pi 4B with SHT30 temperature/humidity sensor and 8-channel relay board.

## Features

- **Precise Temperature Control**: Maintains temperature between 99.6°F and 100.2°F with a target of 99.8°F
- **Safety Cutoff**: Automatically shuts off heaters if temperature exceeds 100.3°F
- **Humidity Control**: Configurable humidity control with humidifier support
- **Web Interface**: User-friendly web dashboard accessible from any device on your home network
- **Dual Heater Support**: Intelligent control of two separate heaters for optimal temperature management
- **Real-time Monitoring**: Continuous monitoring of temperature and humidity conditions
- **Auto-start on Boot**: Automatically starts when your Raspberry Pi powers on

## Hardware Requirements

- Raspberry Pi 4B (or compatible model)
- SHT30 temperature and humidity sensor
- 8-channel relay board
- Two heaters (connected to relays 1 and 2)
- Humidifier (connected to relay 3)
- Power supply for Raspberry Pi
- Appropriate wiring and connections

## Software Components

The system consists of several Python modules:

- **sht30_sensor.py**: Interface for the SHT30 temperature and humidity sensor
- **relay_controller.py**: Control system for the 8-channel relay board
- **temperature_controller.py**: Logic for maintaining temperature within specified range
- **humidity_controller.py**: Logic for maintaining humidity within specified range
- **app.py**: Flask web application for monitoring and control
- **integration.py**: Integration and testing of all components
- **start.sh**: Startup script for the application
- **install.sh**: Installation script with detailed instructions

## Installation

1. Clone or copy this repository to your Raspberry Pi:
   ```
   scp -r incubator_controller pi@your-pi-ip-address:/home/pi/
   ```

2. Run the installation script on your Raspberry Pi:
   ```
   cd /home/pi/incubator_controller
   chmod +x install.sh
   ./install.sh
   ```

3. Follow the instructions provided by the installation script to:
   - Install required packages
   - Set up the Python virtual environment
   - Install the systemd service for auto-start
   - Start the incubator controller service

## Usage

1. Access the web interface by opening a browser and navigating to:
   ```
   http://your-pi-ip-address:5000
   ```

2. The web interface allows you to:
   - Monitor current temperature and humidity
   - View heater and humidifier status
   - Enable/disable temperature and humidity control
   - Configure temperature settings (target, min, max, safety cutoff)
   - Configure humidity settings (target, min, max)
   - Reset the system if needed

## Default Settings

- **Temperature**:
  - Target: 99.8°F
  - Minimum: 99.6°F
  - Maximum: 100.2°F
  - Safety Cutoff: 100.3°F

- **Humidity**:
  - Target: 60%
  - Minimum: 55%
  - Maximum: 65%

## Testing

The system includes a comprehensive testing module (`integration.py`) that can be used to verify all components are working correctly:

```
python integration.py --test-only  # Test components without starting control
python integration.py --monitor-only  # Monitor without starting control
python integration.py --duration 300  # Run full system for 5 minutes
```

## Troubleshooting

- **Service not starting**: Check the service status with `sudo systemctl status incubator-controller.service`
- **Web interface not accessible**: Ensure the Raspberry Pi is connected to your network and check its IP address
- **Sensor readings incorrect**: Verify SHT30 sensor connections and I2C configuration
- **Relays not activating**: Check relay board connections and power supply

## System Architecture

```
+----------------+     +----------------+     +----------------+
| SHT30 Sensor   |---->| Temperature    |---->| Relay Control  |
| Interface      |     | Controller     |     | System         |
+----------------+     +----------------+     +----------------+
        |                     |                      |
        v                     v                      v
+----------------+     +----------------+     +----------------+
| Humidity       |     | Integration    |<----| Web Interface  |
| Controller     |     | Module         |     | (Flask)        |
+----------------+     +----------------+     +----------------+
```

## License

This project is open source and available for personal and educational use.

## Acknowledgments

- Adafruit for their CircuitPython libraries
- Flask web framework
- RPi.GPIO library for Raspberry Pi GPIO control