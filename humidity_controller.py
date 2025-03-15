#!/usr/bin/env python3
"""
Humidity Control Module for Raspberry Pi Incubator Controller

This module provides humidity control logic for an incubator,
maintaining humidity within a specified range.
"""

import time
import threading
from sht30_sensor import SHT30Sensor
from relay_controller import RelayController

class HumidityController:
    """Class to control humidity for an incubator."""
    
    def __init__(self, target_humidity=60, min_humidity=55, max_humidity=65, 
                 humidifier_relay=2):
        """
        Initialize the humidity controller.
        
        Args:
            target_humidity: Target humidity percentage (default: 60%)
            min_humidity: Minimum acceptable humidity percentage (default: 55%)
            max_humidity: Maximum acceptable humidity percentage (default: 65%)
            humidifier_relay: Relay number for humidifier (default: 2)
        """
        # Humidity settings
        self.target_humidity = target_humidity
        self.min_humidity = min_humidity
        self.max_humidity = max_humidity
        
        # Relay number for humidifier
        self.humidifier_relay = humidifier_relay
        
        # Initialize sensor and relay controller
        self.sensor = SHT30Sensor()
        self.relay = RelayController()
        
        # Control variables
        self.is_running = False
        self.control_thread = None
        self.lock = threading.Lock()
        
        # Status variables
        self.current_humidity = None
        self.current_temp = None
        self.humidifier_status = False
        self.last_reading_time = None
        
        # Check if hardware is properly initialized
        self.is_initialized = self.sensor.is_connected and self.relay.is_initialized
        if self.is_initialized:
            print("Humidity controller initialized successfully")
        else:
            print("Error initializing humidity controller: Hardware not properly connected")
    
    def start(self, interval=10):
        """
        Start the humidity control loop.
        
        Args:
            interval: Control loop interval in seconds (default: 10)
            
        Returns:
            bool: True if started successfully, False otherwise
        """
        if not self.is_initialized:
            print("Humidity controller not initialized")
            return False
            
        if self.is_running:
            print("Humidity controller already running")
            return False
            
        try:
            self.is_running = True
            
            # Start control thread
            self.control_thread = threading.Thread(
                target=self._control_loop,
                args=(interval,),
                daemon=True
            )
            self.control_thread.start()
            
            print(f"Humidity controller started (Target: {self.target_humidity}%, Range: {self.min_humidity}% - {self.max_humidity}%)")
            return True
        except Exception as e:
            print(f"Error starting humidity controller: {e}")
            self.is_running = False
            return False
    
    def stop(self):
        """
        Stop the humidity control loop.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        if not self.is_running:
            print("Humidity controller not running")
            return False
            
        try:
            self.is_running = False
            
            # Wait for control thread to terminate
            if self.control_thread and self.control_thread.is_alive():
                self.control_thread.join(timeout=10)
            
            # Turn off humidifier
            with self.lock:
                self.relay.turn_off(self.humidifier_relay)
                self.humidifier_status = False
            
            print("Humidity controller stopped")
            return True
        except Exception as e:
            print(f"Error stopping humidity controller: {e}")
            return False
    
    def _control_loop(self, interval):
        """
        Internal humidity control loop.
        
        Args:
            interval: Control loop interval in seconds
        """
        while self.is_running:
            try:
                # Read temperature and humidity
                _, temp_f, humidity = self.sensor.read_temperature_humidity()
                
                # Update status variables
                with self.lock:
                    self.current_humidity = humidity
                    self.current_temp = temp_f
                    self.last_reading_time = time.time()
                
                # Check if humidity reading is valid
                if humidity is None:
                    print("Invalid humidity reading, skipping control cycle")
                    time.sleep(interval)
                    continue
                
                # Humidity control logic
                with self.lock:
                    # If humidity is below minimum, turn on humidifier
                    if humidity < self.min_humidity:
                        if not self.humidifier_status:
                            self.relay.turn_on(self.humidifier_relay)
                            self.humidifier_status = True
                            print(f"Humidity {humidity}% below minimum {self.min_humidity}%, humidifier ON")
                    
                    # If humidity is above maximum, turn off humidifier
                    elif humidity > self.max_humidity:
                        if self.humidifier_status:
                            self.relay.turn_off(self.humidifier_relay)
                            self.humidifier_status = False
                            print(f"Humidity {humidity}% above maximum {self.max_humidity}%, humidifier OFF")
                    
                    # If humidity is within range but below target, turn on humidifier
                    elif humidity < self.target_humidity:
                        if not self.humidifier_status:
                            self.relay.turn_on(self.humidifier_relay)
                            self.humidifier_status = True
                            print(f"Humidity {humidity}% within range but below target {self.target_humidity}%, humidifier ON")
                    
                    # If humidity is within range but above target, turn off humidifier
                    else:
                        if self.humidifier_status:
                            self.relay.turn_off(self.humidifier_relay)
                            self.humidifier_status = False
                            print(f"Humidity {humidity}% within range but above target {self.target_humidity}%, humidifier OFF")
            
            except Exception as e:
                print(f"Error in humidity control loop: {e}")
            
            # Wait for next control cycle
            time.sleep(interval)
    
    def get_status(self):
        """
        Get the current status of the humidity controller.
        
        Returns:
            dict: Status information
        """
        with self.lock:
            return {
                "is_running": self.is_running,
                "current_humidity": self.current_humidity,
                "current_temp": self.current_temp,
                "target_humidity": self.target_humidity,
                "min_humidity": self.min_humidity,
                "max_humidity": self.max_humidity,
                "humidifier_status": self.humidifier_status,
                "last_reading_time": self.last_reading_time
            }
    
    def update_settings(self, target_humidity=None, min_humidity=None, max_humidity=None):
        """
        Update humidity control settings.
        
        Args:
            target_humidity: New target humidity percentage
            min_humidity: New minimum humidity percentage
            max_humidity: New maximum humidity percentage
            
        Returns:
            bool: True if settings updated successfully, False otherwise
        """
        try:
            with self.lock:
                if target_humidity is not None:
                    self.target_humidity = float(target_humidity)
                if min_humidity is not None:
                    self.min_humidity = float(min_humidity)
                if max_humidity is not None:
                    self.max_humidity = float(max_humidity)
                
                print(f"Humidity settings updated: Target={self.target_humidity}%, Range={self.min_humidity}%-{self.max_humidity}%")
                return True
        except Exception as e:
            print(f"Error updating humidity settings: {e}")
            return False
    
    def cleanup(self):
        """
        Clean up resources.
        
        Returns:
            bool: True if cleaned up successfully, False otherwise
        """
        try:
            # Stop control loop if running
            if self.is_running:
                self.stop()
            
            # Clean up relay controller
            if self.relay.is_initialized:
                self.relay.cleanup()
            
            print("Humidity controller cleaned up")
            return True
        except Exception as e:
            print(f"Error cleaning up humidity controller: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create humidity controller with default settings
    controller = HumidityController()
    
    # Check if controller is initialized
    if controller.is_initialized:
        try:
            # Start humidity control
            controller.start(interval=10)
            
            # Run for 60 seconds
            print("Running humidity control for 60 seconds...")
            time.sleep(60)
            
            # Get status
            status = controller.get_status()
            print("\nCurrent Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            
            # Stop humidity control
            controller.stop()
            
            # Clean up
            controller.cleanup()
            
        except KeyboardInterrupt:
            # Clean up on Ctrl+C
            print("\nStopping humidity control...")
            controller.cleanup()
    else:
        print("Failed to initialize humidity controller. Check hardware connections.")
