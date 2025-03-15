#!/usr/bin/env python3
"""
Temperature Control Module for Raspberry Pi Incubator Controller

This module provides temperature control logic for an incubator,
maintaining temperature within a specified range and implementing
safety cutoffs.
"""

import time
import threading
from sht30_sensor import SHT30Sensor
from relay_controller import RelayController

class TemperatureController:
    """Class to control temperature for an incubator."""
    
    def __init__(self, target_temp=99.8, min_temp=99.6, max_temp=100.2, safety_cutoff=100.3,
                 heater1_relay=0, heater2_relay=1):
        """
        Initialize the temperature controller.
        
        Args:
            target_temp: Target temperature in Fahrenheit (default: 99.8°F)
            min_temp: Minimum acceptable temperature in Fahrenheit (default: 99.6°F)
            max_temp: Maximum acceptable temperature in Fahrenheit (default: 100.2°F)
            safety_cutoff: Safety cutoff temperature in Fahrenheit (default: 100.3°F)
            heater1_relay: Relay number for heater 1 (default: 0)
            heater2_relay: Relay number for heater 2 (default: 1)
        """
        # Temperature settings
        self.target_temp = target_temp
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.safety_cutoff = safety_cutoff
        
        # Relay numbers for heaters
        self.heater1_relay = heater1_relay
        self.heater2_relay = heater2_relay
        
        # Initialize sensor and relay controller
        self.sensor = SHT30Sensor()
        self.relay = RelayController()
        
        # Control variables
        self.is_running = False
        self.control_thread = None
        self.lock = threading.Lock()
        
        # Status variables
        self.current_temp = None
        self.current_humidity = None
        self.heater1_status = False
        self.heater2_status = False
        self.last_reading_time = None
        self.safety_triggered = False
        
        # Check if hardware is properly initialized
        self.is_initialized = self.sensor.is_connected and self.relay.is_initialized
        if self.is_initialized:
            print("Temperature controller initialized successfully")
        else:
            print("Error initializing temperature controller: Hardware not properly connected")
    
    def start(self, interval=5):
        """
        Start the temperature control loop.
        
        Args:
            interval: Control loop interval in seconds (default: 5)
            
        Returns:
            bool: True if started successfully, False otherwise
        """
        if not self.is_initialized:
            print("Temperature controller not initialized")
            return False
            
        if self.is_running:
            print("Temperature controller already running")
            return False
            
        try:
            self.is_running = True
            self.safety_triggered = False
            
            # Start control thread
            self.control_thread = threading.Thread(
                target=self._control_loop,
                args=(interval,),
                daemon=True
            )
            self.control_thread.start()
            
            print(f"Temperature controller started (Target: {self.target_temp}°F, Range: {self.min_temp}°F - {self.max_temp}°F)")
            return True
        except Exception as e:
            print(f"Error starting temperature controller: {e}")
            self.is_running = False
            return False
    
    def stop(self):
        """
        Stop the temperature control loop.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        if not self.is_running:
            print("Temperature controller not running")
            return False
            
        try:
            self.is_running = False
            
            # Wait for control thread to terminate
            if self.control_thread and self.control_thread.is_alive():
                self.control_thread.join(timeout=10)
            
            # Turn off heaters
            with self.lock:
                self.relay.turn_off(self.heater1_relay)
                self.relay.turn_off(self.heater2_relay)
                self.heater1_status = False
                self.heater2_status = False
            
            print("Temperature controller stopped")
            return True
        except Exception as e:
            print(f"Error stopping temperature controller: {e}")
            return False
    
    def _control_loop(self, interval):
        """
        Internal temperature control loop.
        
        Args:
            interval: Control loop interval in seconds
        """
        while self.is_running:
            try:
                # Read temperature and humidity
                _, temp_f, humidity = self.sensor.read_temperature_humidity()
                
                # Update status variables
                with self.lock:
                    self.current_temp = temp_f
                    self.current_humidity = humidity
                    self.last_reading_time = time.time()
                
                # Check if temperature reading is valid
                if temp_f is None:
                    print("Invalid temperature reading, skipping control cycle")
                    time.sleep(interval)
                    continue
                
                # Safety cutoff check
                if temp_f >= self.safety_cutoff:
                    print(f"SAFETY CUTOFF TRIGGERED: Temperature {temp_f}°F exceeds safety limit {self.safety_cutoff}°F")
                    with self.lock:
                        self.relay.turn_off(self.heater1_relay)
                        self.relay.turn_off(self.heater2_relay)
                        self.heater1_status = False
                        self.heater2_status = False
                        self.safety_triggered = True
                    
                    # Wait for temperature to drop below safety cutoff
                    while self.is_running and self.safety_triggered:
                        _, temp_f, _ = self.sensor.read_temperature_humidity()
                        if temp_f is not None and temp_f < self.safety_cutoff - 0.3:  # 0.3°F hysteresis
                            print(f"Temperature dropped to {temp_f}°F, resuming normal operation")
                            with self.lock:
                                self.safety_triggered = False
                        time.sleep(interval)
                    
                    continue
                
                # Normal temperature control
                if not self.safety_triggered:
                    with self.lock:
                        # If temperature is below minimum, turn on heaters
                        if temp_f < self.min_temp:
                            # Turn on both heaters if we're significantly below target
                            if temp_f < self.min_temp - 0.3:
                                if not self.heater1_status:
                                    self.relay.turn_on(self.heater1_relay)
                                    self.heater1_status = True
                                if not self.heater2_status:
                                    self.relay.turn_on(self.heater2_relay)
                                    self.heater2_status = True
                                print(f"Temperature {temp_f}°F below minimum {self.min_temp}°F, both heaters ON")
                            # Turn on just one heater if we're close to target
                            else:
                                if not self.heater1_status:
                                    self.relay.turn_on(self.heater1_relay)
                                    self.heater1_status = True
                                if self.heater2_status:
                                    self.relay.turn_off(self.heater2_relay)
                                    self.heater2_status = False
                                print(f"Temperature {temp_f}°F slightly below minimum {self.min_temp}°F, heater 1 ON")
                        
                        # If temperature is above maximum, turn off heaters
                        elif temp_f > self.max_temp:
                            if self.heater1_status:
                                self.relay.turn_off(self.heater1_relay)
                                self.heater1_status = False
                            if self.heater2_status:
                                self.relay.turn_off(self.heater2_relay)
                                self.heater2_status = False
                            print(f"Temperature {temp_f}°F above maximum {self.max_temp}°F, both heaters OFF")
                        
                        # If temperature is within range but below target, use one heater
                        elif temp_f < self.target_temp:
                            if not self.heater1_status:
                                self.relay.turn_on(self.heater1_relay)
                                self.heater1_status = True
                            if self.heater2_status:
                                self.relay.turn_off(self.heater2_relay)
                                self.heater2_status = False
                            print(f"Temperature {temp_f}°F within range but below target {self.target_temp}°F, heater 1 ON")
                        
                        # If temperature is within range but above target, turn off heaters
                        else:
                            if self.heater1_status:
                                self.relay.turn_off(self.heater1_relay)
                                self.heater1_status = False
                            if self.heater2_status:
                                self.relay.turn_off(self.heater2_relay)
                                self.heater2_status = False
                            print(f"Temperature {temp_f}°F within range but above target {self.target_temp}°F, both heaters OFF")
            
            except Exception as e:
                print(f"Error in temperature control loop: {e}")
            
            # Wait for next control cycle
            time.sleep(interval)
    
    def get_status(self):
        """
        Get the current status of the temperature controller.
        
        Returns:
            dict: Status information
        """
        with self.lock:
            return {
                "is_running": self.is_running,
                "current_temp": self.current_temp,
                "current_humidity": self.current_humidity,
                "target_temp": self.target_temp,
                "min_temp": self.min_temp,
                "max_temp": self.max_temp,
                "safety_cutoff": self.safety_cutoff,
                "heater1_status": self.heater1_status,
                "heater2_status": self.heater2_status,
                "safety_triggered": self.safety_triggered,
                "last_reading_time": self.last_reading_time
            }
    
    def update_settings(self, target_temp=None, min_temp=None, max_temp=None, safety_cutoff=None):
        """
        Update temperature control settings.
        
        Args:
            target_temp: New target temperature in Fahrenheit
            min_temp: New minimum temperature in Fahrenheit
            max_temp: New maximum temperature in Fahrenheit
            safety_cutoff: New safety cutoff temperature in Fahrenheit
            
        Returns:
            bool: True if settings updated successfully, False otherwise
        """
        try:
            with self.lock:
                if target_temp is not None:
                    self.target_temp = float(target_temp)
                if min_temp is not None:
                    self.min_temp = float(min_temp)
                if max_temp is not None:
                    self.max_temp = float(max_temp)
                if safety_cutoff is not None:
                    self.safety_cutoff = float(safety_cutoff)
                
                print(f"Temperature settings updated: Target={self.target_temp}°F, Range={self.min_temp}°F-{self.max_temp}°F, Safety={self.safety_cutoff}°F")
                return True
        except Exception as e:
            print(f"Error updating temperature settings: {e}")
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
            
            print("Temperature controller cleaned up")
            return True
        except Exception as e:
            print(f"Error cleaning up temperature controller: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create temperature controller with default settings
    controller = TemperatureController()
    
    # Check if controller is initialized
    if controller.is_initialized:
        try:
            # Start temperature control
            controller.start(interval=5)
            
            # Run for 60 seconds
            print("Running temperature control for 60 seconds...")
            time.sleep(60)
            
            # Get status
            status = controller.get_status()
            print("\nCurrent Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            
            # Stop temperature control
            controller.stop()
            
            # Clean up
            controller.cleanup()
            
        except KeyboardInterrupt:
            # Clean up on Ctrl+C
            print("\nStopping temperature control...")
            controller.cleanup()
    else:
        print("Failed to initialize temperature controller. Check hardware connections.")
