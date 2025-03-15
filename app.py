#!/usr/bin/env python3
"""
Flask Web Application for Raspberry Pi Incubator Controller

This module provides a web interface to monitor and control
the incubator's temperature and humidity.
"""

from flask import Flask, render_template, request, jsonify
import threading
import time
import json
import os
from sht30_sensor import SHT30Sensor
from temperature_controller import TemperatureController
from humidity_controller import HumidityController

# Create Flask application
app = Flask(__name__)

# Global variables for controllers
temp_controller = None
humidity_controller = None
sensor = None

# Lock for thread safety
lock = threading.Lock()

# Default settings
DEFAULT_TEMP_TARGET = 99.8
DEFAULT_TEMP_MIN = 99.6
DEFAULT_TEMP_MAX = 100.2
DEFAULT_TEMP_SAFETY = 100.3
DEFAULT_HUMIDITY_TARGET = 60
DEFAULT_HUMIDITY_MIN = 55
DEFAULT_HUMIDITY_MAX = 65

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

def load_settings():
    """Load settings from file or use defaults."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    # Return default settings if file doesn't exist or error occurs
    return {
        "temp_target": DEFAULT_TEMP_TARGET,
        "temp_min": DEFAULT_TEMP_MIN,
        "temp_max": DEFAULT_TEMP_MAX,
        "temp_safety": DEFAULT_TEMP_SAFETY,
        "humidity_target": DEFAULT_HUMIDITY_TARGET,
        "humidity_min": DEFAULT_HUMIDITY_MIN,
        "humidity_max": DEFAULT_HUMIDITY_MAX,
        "temp_control_enabled": False,
        "humidity_control_enabled": False
    }

def save_settings(settings):
    """Save settings to file."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def initialize_controllers():
    """Initialize sensor and controllers."""
    global sensor, temp_controller, humidity_controller
    
    # Load settings
    settings = load_settings()
    
    # Initialize sensor
    sensor = SHT30Sensor()
    
    # Initialize temperature controller
    temp_controller = TemperatureController(
        target_temp=settings["temp_target"],
        min_temp=settings["temp_min"],
        max_temp=settings["temp_max"],
        safety_cutoff=settings["temp_safety"]
    )
    
    # Initialize humidity controller
    humidity_controller = HumidityController(
        target_humidity=settings["humidity_target"],
        min_humidity=settings["humidity_min"],
        max_humidity=settings["humidity_max"]
    )
    
    # Start controllers if enabled in settings
    if settings["temp_control_enabled"]:
        temp_controller.start()
    
    if settings["humidity_control_enabled"]:
        humidity_controller.start()

@app.route('/')
def index():
    """Render the main page."""
    settings = load_settings()
    return render_template('index.html', settings=settings)

@app.route('/api/status')
def get_status():
    """Get current status of the incubator."""
    with lock:
        if sensor and temp_controller and humidity_controller:
            # Read current temperature and humidity
            temp_c, temp_f, humidity = sensor.read_temperature_humidity()
            
            # Get controller statuses
            temp_status = temp_controller.get_status()
            humidity_status = humidity_controller.get_status()
            
            # Combine status information
            status = {
                "temperature": {
                    "current": temp_f,
                    "target": temp_status["target_temp"],
                    "min": temp_status["min_temp"],
                    "max": temp_status["max_temp"],
                    "safety_cutoff": temp_status["safety_cutoff"],
                    "heater1_status": temp_status["heater1_status"],
                    "heater2_status": temp_status["heater2_status"],
                    "safety_triggered": temp_status["safety_triggered"],
                    "control_enabled": temp_status["is_running"]
                },
                "humidity": {
                    "current": humidity,
                    "target": humidity_status["target_humidity"],
                    "min": humidity_status["min_humidity"],
                    "max": humidity_status["max_humidity"],
                    "humidifier_status": humidity_status["humidifier_status"],
                    "control_enabled": humidity_status["is_running"]
                },
                "timestamp": time.time()
            }
            
            return jsonify(status)
        else:
            return jsonify({"error": "Controllers not initialized"}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Get or update settings."""
    if request.method == 'GET':
        return jsonify(load_settings())
    
    elif request.method == 'POST':
        try:
            # Get current settings
            settings = load_settings()
            
            # Update with new values from request
            data = request.get_json()
            
            # Update temperature settings
            if "temp_target" in data:
                settings["temp_target"] = float(data["temp_target"])
            if "temp_min" in data:
                settings["temp_min"] = float(data["temp_min"])
            if "temp_max" in data:
                settings["temp_max"] = float(data["temp_max"])
            if "temp_safety" in data:
                settings["temp_safety"] = float(data["temp_safety"])
            
            # Update humidity settings
            if "humidity_target" in data:
                settings["humidity_target"] = float(data["humidity_target"])
            if "humidity_min" in data:
                settings["humidity_min"] = float(data["humidity_min"])
            if "humidity_max" in data:
                settings["humidity_max"] = float(data["humidity_max"])
            
            # Update controller settings
            with lock:
                if temp_controller:
                    temp_controller.update_settings(
                        target_temp=settings["temp_target"],
                        min_temp=settings["temp_min"],
                        max_temp=settings["temp_max"],
                        safety_cutoff=settings["temp_safety"]
                    )
                
                if humidity_controller:
                    humidity_controller.update_settings(
                        target_humidity=settings["humidity_target"],
                        min_humidity=settings["humidity_min"],
                        max_humidity=settings["humidity_max"]
                    )
            
            # Save settings to file
            save_settings(settings)
            
            return jsonify({"success": True, "settings": settings})
        
        except Exception as e:
            return jsonify({"error": str(e)}), 400

@app.route('/api/control', methods=['POST'])
def control_system():
    """Start or stop temperature and humidity control."""
    try:
        data = request.get_json()
        settings = load_settings()
        
        # Handle temperature control
        if "temp_control" in data:
            temp_control = data["temp_control"]
            with lock:
                if temp_controller:
                    if temp_control and not temp_controller.is_running:
                        temp_controller.start()
                    elif not temp_control and temp_controller.is_running:
                        temp_controller.stop()
                    settings["temp_control_enabled"] = temp_control
        
        # Handle humidity control
        if "humidity_control" in data:
            humidity_control = data["humidity_control"]
            with lock:
                if humidity_controller:
                    if humidity_control and not humidity_controller.is_running:
                        humidity_controller.start()
                    elif not humidity_control and humidity_controller.is_running:
                        humidity_controller.stop()
                    settings["humidity_control_enabled"] = humidity_control
        
        # Save settings to file
        save_settings(settings)
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/reset', methods=['POST'])
def reset_system():
    """Reset the system in case of errors."""
    try:
        with lock:
            if temp_controller:
                temp_controller.stop()
                temp_controller.cleanup()
            
            if humidity_controller:
                humidity_controller.stop()
                humidity_controller.cleanup()
            
            # Reinitialize controllers
            initialize_controllers()
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cleanup():
    """Clean up resources when the application exits."""
    with lock:
        if temp_controller:
            temp_controller.cleanup()
        
        if humidity_controller:
            humidity_controller.cleanup()

# Initialize controllers when the module is imported
initialize_controllers()

# Register cleanup function to be called when the application exits
import atexit
atexit.register(cleanup)

if __name__ == '__main__':
    try:
        # Run the Flask application
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        # Clean up on Ctrl+C
        cleanup()
