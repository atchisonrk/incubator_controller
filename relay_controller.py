#!/usr/bin/env python3
"""
Relay Control Module for Raspberry Pi Incubator Controller

This module provides functions to control an 8-channel relay board
connected to a Raspberry Pi for controlling heaters and humidifier.
"""

import time
import RPi.GPIO as GPIO

class RelayController:
    """Class to interface with an 8-channel relay board."""
    
    def __init__(self, relay_pins=None):
        """
        Initialize the relay controller.
        
        Args:
            relay_pins: List of GPIO pins connected to relays (default: pins 4, 17, 18, 27, 22, 23, 24, 25)
        """
        # Default relay pins if none provided
        if relay_pins is None:
            self.relay_pins = [4, 17, 18, 27, 22, 23, 24, 25]
        else:
            self.relay_pins = relay_pins
            
        # Number of relays
        self.num_relays = len(self.relay_pins)
        
        # Relay state tracking (True = ON, False = OFF)
        self.relay_states = [False] * self.num_relays
        
        # Relay names/functions for better readability
        self.relay_names = {
            0: "Heater 1",
            1: "Heater 2",
            2: "Humidifier",
            3: "Relay 4",
            4: "Relay 5",
            5: "Relay 6",
            6: "Relay 7",
            7: "Relay 8"
        }
        
        try:
            # Set up GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Initialize all relay pins as outputs and set to HIGH (relays are typically active LOW)
            for pin in self.relay_pins:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH)  # Relay OFF initially
                
            self.is_initialized = True
            print("Relay controller initialized successfully")
        except Exception as e:
            self.is_initialized = False
            print(f"Error initializing relay controller: {e}")
    
    def turn_on(self, relay_num):
        """
        Turn ON a specific relay.
        
        Args:
            relay_num: Relay number (0-7)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_initialized:
            print("Relay controller not initialized")
            return False
            
        if relay_num < 0 or relay_num >= self.num_relays:
            print(f"Invalid relay number: {relay_num}")
            return False
            
        try:
            # Relays are typically active LOW
            GPIO.output(self.relay_pins[relay_num], GPIO.LOW)
            self.relay_states[relay_num] = True
            print(f"{self.relay_names[relay_num]} (Relay {relay_num}) turned ON")
            return True
        except Exception as e:
            print(f"Error turning on relay {relay_num}: {e}")
            return False
    
    def turn_off(self, relay_num):
        """
        Turn OFF a specific relay.
        
        Args:
            relay_num: Relay number (0-7)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_initialized:
            print("Relay controller not initialized")
            return False
            
        if relay_num < 0 or relay_num >= self.num_relays:
            print(f"Invalid relay number: {relay_num}")
            return False
            
        try:
            # Relays are typically active LOW, so HIGH turns them OFF
            GPIO.output(self.relay_pins[relay_num], GPIO.HIGH)
            self.relay_states[relay_num] = False
            print(f"{self.relay_names[relay_num]} (Relay {relay_num}) turned OFF")
            return True
        except Exception as e:
            print(f"Error turning off relay {relay_num}: {e}")
            return False
    
    def toggle(self, relay_num):
        """
        Toggle a specific relay.
        
        Args:
            relay_num: Relay number (0-7)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.relay_states[relay_num]:
            return self.turn_off(relay_num)
        else:
            return self.turn_on(relay_num)
    
    def get_state(self, relay_num):
        """
        Get the current state of a specific relay.
        
        Args:
            relay_num: Relay number (0-7)
            
        Returns:
            bool: True if relay is ON, False if OFF or error
        """
        if relay_num < 0 or relay_num >= self.num_relays:
            print(f"Invalid relay number: {relay_num}")
            return False
            
        return self.relay_states[relay_num]
    
    def all_off(self):
        """
        Turn OFF all relays.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_initialized:
            print("Relay controller not initialized")
            return False
            
        try:
            for i in range(self.num_relays):
                self.turn_off(i)
            print("All relays turned OFF")
            return True
        except Exception as e:
            print(f"Error turning off all relays: {e}")
            return False
    
    def cleanup(self):
        """
        Clean up GPIO resources.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_initialized:
            return False
            
        try:
            self.all_off()
            GPIO.cleanup()
            self.is_initialized = False
            print("Relay controller cleaned up")
            return True
        except Exception as e:
            print(f"Error cleaning up relay controller: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create relay controller instance
    relay = RelayController()
    
    # Check if relay controller is initialized
    if relay.is_initialized:
        try:
            # Test each relay
            for i in range(relay.num_relays):
                print(f"Testing {relay.relay_names[i]} (Relay {i})")
                relay.turn_on(i)
                time.sleep(1)
                relay.turn_off(i)
                time.sleep(0.5)
            
            # Test heaters and humidifier specifically
            print("\nTesting heaters and humidifier...")
            
            # Turn on heaters
            relay.turn_on(0)  # Heater 1
            relay.turn_on(1)  # Heater 2
            print("Heaters ON")
            time.sleep(2)
            
            # Turn off heaters
            relay.turn_off(0)  # Heater 1
            relay.turn_off(1)  # Heater 2
            print("Heaters OFF")
            time.sleep(1)
            
            # Turn on humidifier
            relay.turn_on(2)  # Humidifier
            print("Humidifier ON")
            time.sleep(2)
            
            # Turn off humidifier
            relay.turn_off(2)  # Humidifier
            print("Humidifier OFF")
            
            # Clean up
            relay.cleanup()
            
        except KeyboardInterrupt:
            # Clean up on Ctrl+C
            relay.cleanup()
    else:
        print("Failed to initialize relay controller. Check connections.")
