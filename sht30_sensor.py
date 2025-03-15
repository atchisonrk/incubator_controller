#!/usr/bin/env python3
"""
SHT30 Temperature and Humidity Sensor Interface Module
for Raspberry Pi Incubator Controller

This module provides functions to initialize and read data from the SHT30 sensor.
"""

import time
import board
import busio
import adafruit_sht31d

class SHT30Sensor:
    """Class to interface with the SHT30 temperature and humidity sensor."""
    
    def __init__(self, i2c_address=0x44):
        """
        Initialize the SHT30 sensor.
        
        Args:
            i2c_address: The I2C address of the sensor (default: 0x44)
        """
        try:
            # Initialize I2C bus
            self.i2c = busio.I2C(board.SCL, board.SDA)
            # Initialize SHT30 sensor
            self.sensor = adafruit_sht31d.SHT31D(self.i2c, address=i2c_address)
            self.is_connected = True
            print("SHT30 sensor initialized successfully")
        except Exception as e:
            self.is_connected = False
            print(f"Error initializing SHT30 sensor: {e}")
    
    def read_temperature_humidity(self):
        """
        Read temperature and humidity values from the sensor.
        
        Returns:
            tuple: (temperature_c, temperature_f, humidity) or (None, None, None) if error
        """
        if not self.is_connected:
            print("Sensor not connected")
            return None, None, None
        
        try:
            # Read temperature and humidity
            temperature_c = self.sensor.temperature
            temperature_f = (temperature_c * 9/5) + 32
            humidity = self.sensor.relative_humidity
            
            return temperature_c, temperature_f, humidity
        except Exception as e:
            print(f"Error reading from SHT30 sensor: {e}")
            return None, None, None
    
    def heater_on(self):
        """Turn on the sensor's internal heater."""
        if self.is_connected:
            try:
                self.sensor.heater = True
                print("Sensor heater turned ON")
            except Exception as e:
                print(f"Error turning on sensor heater: {e}")
    
    def heater_off(self):
        """Turn off the sensor's internal heater."""
        if self.is_connected:
            try:
                self.sensor.heater = False
                print("Sensor heater turned OFF")
            except Exception as e:
                print(f"Error turning off sensor heater: {e}")
    
    def reset(self):
        """Reset the sensor."""
        if self.is_connected:
            try:
                self.sensor.reset()
                print("Sensor reset successfully")
            except Exception as e:
                print(f"Error resetting sensor: {e}")


# Example usage
if __name__ == "__main__":
    # Create sensor instance
    sensor = SHT30Sensor()
    
    # Check if sensor is connected
    if sensor.is_connected:
        # Read temperature and humidity 5 times
        for i in range(5):
            temp_c, temp_f, humidity = sensor.read_temperature_humidity()
            if temp_c is not None:
                print(f"Reading {i+1}:")
                print(f"  Temperature: {temp_c:.2f}°C / {temp_f:.2f}°F")
                print(f"  Humidity: {humidity:.2f}%")
            time.sleep(2)
    else:
        print("Failed to initialize sensor. Check connections.")
