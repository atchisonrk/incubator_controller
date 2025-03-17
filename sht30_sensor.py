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
    
    def __init__(self, i2c_address=0x44, read_timeout=5):
        """
        Initialize the SHT30 sensor.
        
        Args:
            i2c_address: The I2C address of the sensor (default: 0x44)
            read_timeout: Timeout in seconds for sensor read operations (default: 5)
        """
        self.i2c_address = i2c_address
        self.read_timeout = read_timeout
        self.sensor = None
        self.i2c = None
        self.is_connected = False
        self.last_successful_read = None
        
        try:
            # Initialize I2C bus
            self.i2c = busio.I2C(board.SCL, board.SDA)
            # Initialize SHT30 sensor
            self.sensor = adafruit_sht31d.SHT31D(self.i2c, address=i2c_address)
            self.is_connected = True
            self.last_successful_read = time.time()
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
            # Set timeout for read operation
            start_time = time.time()
            
            # Read temperature and humidity
            temperature_c = self.sensor.temperature
            temperature_f = (temperature_c * 9/5) + 32
            humidity = self.sensor.relative_humidity
            
            # Update last successful read timestamp
            self.last_successful_read = time.time()
            
            return temperature_c, temperature_f, humidity
        except Exception as e:
            elapsed_time = time.time() - start_time
            if elapsed_time >= self.read_timeout:
                print(f"Timeout reading from SHT30 sensor after {elapsed_time:.1f} seconds")
            else:
                print(f"Error reading from SHT30 sensor: {e}")
            return None, None, None
    
    def is_active(self, timeout=30):
        """
        Check if the sensor is active based on the last successful read.
        
        Args:
            timeout: Time in seconds since last successful read to consider sensor inactive (default: 30)
            
        Returns:
            bool: True if sensor is active, False otherwise
        """
        if not self.is_connected or self.last_successful_read is None:
            return False
        
        # Check if we've had a successful read within the timeout period
        return (time.time() - self.last_successful_read) < timeout
    
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
    
    def reconnect(self):
        """
        Attempt to reconnect to the sensor.
        
        Returns:
            bool: True if reconnection successful, False otherwise
        """
        if self.is_connected:
            # Already connected
            return True
        
        try:
            # Initialize I2C bus
            self.i2c = busio.I2C(board.SCL, board.SDA)
            # Initialize SHT30 sensor
            self.sensor = adafruit_sht31d.SHT31D(self.i2c, address=self.i2c_address)
            self.is_connected = True
            self.last_successful_read = time.time()
            print("SHT30 sensor reconnected successfully")
            return True
        except Exception as e:
            print(f"Error reconnecting to SHT30 sensor: {e}")
            return False


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
                print(f"  Sensor active: {sensor.is_active()}")
            else:
                print(f"Reading {i+1}: Failed to read sensor")
                print(f"  Sensor active: {sensor.is_active()}")
            time.sleep(2)
    else:
        print("Failed to initialize sensor. Check connections.")
        
        # Try to reconnect
        print("Attempting to reconnect...")
        if sensor.reconnect():
            print("Reconnection successful!")
        else:
            print("Reconnection failed.")
