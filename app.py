#!/usr/bin/env python3
"""
Flask Web Application for Raspberry Pi Incubator Controller

This module provides a web interface for monitoring and controlling
the incubator system with temperature and humidity control.
"""

import os
import json
import time
import threading
from flask import Flask, render_template, request, jsonify
from sht30_sensor import SHT30Sensor
from relay_controller import RelayController
from temperature_controller import TemperatureController
from humidity_controller import HumidityController

# Create Flask application
app = Flask(__name__)

# Initialize controllers
sensor = SHT30Sensor()
relay = RelayController()
temp_controller = TemperatureController()
humidity_controller = HumidityController()

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

# Default settings
DEFAULT_SETTINGS = {
    'temperature': {
        'target': 99.8,
        'min': 99.6,
        'max': 100.2,
        'safety_cutoff': 100.3,
        'sensor_timeout': 30,
        'enabled': False
    },
    'humidity': {
        'target': 60,
        'min': 55,
        'max': 65,
        'enabled': False
    }
}

# Global variables
settings = DEFAULT_SETTINGS.copy()
system_running = False
lock = threading.Lock()

# Load settings from file
def load_settings():
    global settings
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                loaded_settings = json.load(f)
                settings.update(loaded_settings)
                print("Settings loaded from file")
        else:
            save_settings()  # Create default settings file
            print("Default settings saved to file")
    except Exception as e:
        print(f"Error loading settings: {e}")

# Save settings to file
def save_settings():
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
            print("Settings saved to file")
    except Exception as e:
        print(f"Error saving settings: {e}")

# Apply settings to controllers
def apply_settings():
    with lock:
        # Apply temperature settings
        temp_controller.update_settings(
            target_temp=settings['temperature']['target'],
            min_temp=settings['temperature']['min'],
            max_temp=settings['temperature']['max'],
            safety_cutoff=settings['temperature']['safety_cutoff'],
            sensor_timeout=settings['temperature']['sensor_timeout']
        )
        
        # Apply humidity settings
        humidity_controller.update_settings(
            target_humidity=settings['humidity']['target'],
            min_humidity=settings['humidity']['min'],
            max_humidity=settings['humidity']['max']
        )
        
        # Start or stop controllers based on enabled settings
        if settings['temperature']['enabled'] and not temp_controller.is_running:
            temp_controller.start()
        elif not settings['temperature']['enabled'] and temp_controller.is_running:
            temp_controller.stop()
            
        if settings['humidity']['enabled'] and not humidity_controller.is_running:
            humidity_controller.start()
        elif not settings['humidity']['enabled'] and humidity_controller.is_running:
            humidity_controller.stop()

# Routes
@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html', settings=settings)

@app.route('/api/status')
def get_status():
    """Get the current status of the incubator system."""
    with lock:
        # Get temperature controller status
        temp_status = temp_controller.get_status()
        
        # Get humidity controller status
        humidity_status = humidity_controller.get_status()
        
        # Combine status information
        status = {
            'temperature': {
                'current': temp_status['current_temp'],
                'target': temp_status['target_temp'],
                'min': temp_status['min_temp'],
                'max': temp_status['max_temp'],
                'safety_cutoff': temp_status['safety_cutoff'],
                'heater1_status': temp_status['heater1_status'],
                'heater2_status': temp_status['heater2_status'],
                'safety_triggered': temp_status['safety_triggered'],
                'sensor_failure': temp_status['sensor_failure'],
                'overheat_triggered': temp_status['overheat_triggered'],
                'is_running': temp_status['is_running'],
                'last_reading_time': temp_status['last_reading_time']
            },
            'humidity': {
                'current': humidity_status['current_humidity'],
                'target': humidity_status['target_humidity'],
                'min': humidity_status['min_humidity'],
                'max': humidity_status['max_humidity'],
                'humidifier_status': humidity_status['humidifier_status'],
                'sensor_failure': humidity_status['sensor_failure'],
                'is_running': humidity_status['is_running'],
                'last_reading_time': humidity_status['last_reading_time']
            },
            'system': {
                'time': time.time(),
                'uptime': time.time() - start_time
            }
        }
        
        return jsonify(status)

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Get or update settings."""
    global settings
    
    if request.method == 'GET':
        # Return current settings
        return jsonify(settings)
    
    elif request.method == 'POST':
        try:
            # Get settings from request
            new_settings = request.get_json()
            
            with lock:
                # Update temperature settings
                if 'temperature' in new_settings:
                    settings['temperature'].update(new_settings['temperature'])
                
                # Update humidity settings
                if 'humidity' in new_settings:
                    settings['humidity'].update(new_settings['humidity'])
                
                # Save settings to file
                save_settings()
                
                # Apply settings to controllers
                apply_settings()
            
            return jsonify({'success': True, 'message': 'Settings updated successfully'})
        
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error updating settings: {e}'})

@app.route('/api/control/<system>/<action>')
def control_system(system, action):
    """Control temperature or humidity systems."""
    try:
        with lock:
            if system == 'temperature':
                if action == 'start':
                    settings['temperature']['enabled'] = True
                    temp_controller.start()
                    message = 'Temperature control started'
                elif action == 'stop':
                    settings['temperature']['enabled'] = False
                    temp_controller.stop()
                    message = 'Temperature control stopped'
                else:
                    return jsonify({'success': False, 'message': 'Invalid action'})
            
            elif system == 'humidity':
                if action == 'start':
                    settings['humidity']['enabled'] = True
                    humidity_controller.start()
                    message = 'Humidity control started'
                elif action == 'stop':
                    settings['humidity']['enabled'] = False
                    humidity_controller.stop()
                    message = 'Humidity control stopped'
                else:
                    return jsonify({'success': False, 'message': 'Invalid action'})
            
            elif system == 'all':
                if action == 'start':
                    settings['temperature']['enabled'] = True
                    settings['humidity']['enabled'] = True
                    temp_controller.start()
                    humidity_controller.start()
                    message = 'All systems started'
                elif action == 'stop':
                    settings['temperature']['enabled'] = False
                    settings['humidity']['enabled'] = False
                    temp_controller.stop()
                    humidity_controller.stop()
                    message = 'All systems stopped'
                else:
                    return jsonify({'success': False, 'message': 'Invalid action'})
            
            else:
                return jsonify({'success': False, 'message': 'Invalid system'})
            
            # Save settings to file
            save_settings()
            
            return jsonify({'success': True, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error controlling system: {e}'})

@app.route('/api/reset')
def reset_system():
    """Reset the incubator system."""
    try:
        with lock:
            # Stop controllers
            if temp_controller.is_running:
                temp_controller.stop()
            if humidity_controller.is_running:
                humidity_controller.stop()
            
            # Turn off all relays
            relay.all_off()
            
            # Reset settings to defaults
            settings.update(DEFAULT_SETTINGS.copy())
            save_settings()
            
            # Apply default settings
            apply_settings()
            
            return jsonify({'success': True, 'message': 'System reset successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error resetting system: {e}'})

# Initialize application
def initialize():
    global start_time
    
    # Record start time
    start_time = time.time()
    
    # Load settings
    load_settings()
    
    # Apply settings
    apply_settings()
    
    print("Incubator controller web application initialized")

# Cleanup function
def cleanup():
    print("Cleaning up resources...")
    
    # Stop controllers
    if temp_controller.is_running:
        temp_controller.stop()
    if humidity_controller.is_running:
        humidity_controller.stop()
    
    # Clean up controllers
    temp_controller.cleanup()
    humidity_controller.cleanup()
    
    print("Cleanup complete")

# Main entry point
if __name__ == '__main__':
    try:
        # Initialize application
        initialize()
        
        # Run Flask application
        app.run(host='0.0.0.0', port=5000, debug=False)
    
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    
    finally:
        # Clean up resources
        cleanup()
