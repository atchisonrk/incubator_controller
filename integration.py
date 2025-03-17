#!/usr/bin/env python3
"""
Main Integration Module for Raspberry Pi Incubator Controller

This module integrates all components of the incubator controller system
and provides a test harness for verifying functionality.
"""

import time
import threading
import argparse
from sht30_sensor import SHT30Sensor
from relay_controller import RelayController
from temperature_controller import TemperatureController
from humidity_controller import HumidityController

class IncubatorSystem:
    """Class to integrate and test all components of the incubator controller."""
    
    def __init__(self):
        """Initialize the incubator system."""
        # Initialize components
        self.sensor = SHT30Sensor()
        self.relay = RelayController()
        self.temp_controller = TemperatureController()
        self.humidity_controller = HumidityController()
        
        # Status variables
        self.is_running = False
        self.monitor_thread = None
        
        # Check if all components are initialized
        self.is_initialized = (
            self.sensor.is_connected and 
            self.relay.is_initialized and
            self.temp_controller.is_initialized and
            self.humidity_controller.is_initialized
        )
        
        if self.is_initialized:
            print("Incubator system initialized successfully")
        else:
            print("Error initializing incubator system: One or more components failed to initialize")
    
    def start_monitoring(self, interval=5):
        """
        Start monitoring the system.
        
        Args:
            interval: Monitoring interval in seconds (default: 5)
            
        Returns:
            bool: True if started successfully, False otherwise
        """
        if not self.is_initialized:
            print("Incubator system not initialized")
            return False
            
        if self.is_running:
            print("Monitoring already running")
            return False
            
        try:
            self.is_running = True
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                args=(interval,),
                daemon=True
            )
            self.monitor_thread.start()
            
            print(f"System monitoring started (interval: {interval}s)")
            return True
        except Exception as e:
            print(f"Error starting monitoring: {e}")
            self.is_running = False
            return False
    
    def stop_monitoring(self):
        """
        Stop monitoring the system.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        if not self.is_running:
            print("Monitoring not running")
            return False
            
        try:
            self.is_running = False
            
            # Wait for monitoring thread to terminate
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=10)
            
            print("System monitoring stopped")
            return True
        except Exception as e:
            print(f"Error stopping monitoring: {e}")
            return False
    
    def _monitor_loop(self, interval):
        """
        Internal monitoring loop.
        
        Args:
            interval: Monitoring interval in seconds
        """
        while self.is_running:
            try:
                # Read temperature and humidity
                temp_c, temp_f, humidity = self.sensor.read_temperature_humidity()
                
                # Get controller statuses
                temp_status = self.temp_controller.get_status()
                humidity_status = self.humidity_controller.get_status()
                
                # Print status information
                print("\n===== INCUBATOR STATUS =====")
                print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if temp_f is not None:
                    print(f"Temperature: {temp_f:.1f}°F ({temp_c:.1f}°C)")
                else:
                    print("Temperature: Error reading sensor")
                
                if humidity is not None:
                    print(f"Humidity: {humidity:.1f}%")
                else:
                    print("Humidity: Error reading sensor")
                
                print("\nTemperature Control:")
                print(f"  Enabled: {temp_status['is_running']}")
                print(f"  Target: {temp_status['target_temp']:.1f}°F")
                print(f"  Range: {temp_status['min_temp']:.1f}°F - {temp_status['max_temp']:.1f}°F")
                print(f"  Safety Cutoff: {temp_status['safety_cutoff']:.1f}°F")
                print(f"  Heater 1: {'ON' if temp_status['heater1_status'] else 'OFF'}")
                print(f"  Heater 2: {'ON' if temp_status['heater2_status'] else 'OFF'}")
                print(f"  Safety Triggered: {temp_status['safety_triggered']}")
                print(f"  Sensor Failure: {temp_status['sensor_failure']}")
                print(f"  Overheat Triggered: {temp_status['overheat_triggered']}")
                
                print("\nHumidity Control:")
                print(f"  Enabled: {humidity_status['is_running']}")
                print(f"  Target: {humidity_status['target_humidity']:.1f}%")
                print(f"  Range: {humidity_status['min_humidity']:.1f}% - {humidity_status['max_humidity']:.1f}%")
                print(f"  Humidifier: {'ON' if humidity_status['humidifier_status'] else 'OFF'}")
                print(f"  Sensor Failure: {humidity_status['sensor_failure']}")
                
                print("=============================")
            
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
            
            # Wait for next monitoring cycle
            time.sleep(interval)
    
    def start_control_systems(self):
        """
        Start temperature and humidity control systems.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if not self.is_initialized:
            print("Incubator system not initialized")
            return False
            
        try:
            # Start temperature controller
            temp_result = self.temp_controller.start()
            
            # Start humidity controller
            humidity_result = self.humidity_controller.start()
            
            if temp_result and humidity_result:
                print("Temperature and humidity control systems started")
                return True
            else:
                print("Error starting control systems")
                return False
        except Exception as e:
            print(f"Error starting control systems: {e}")
            return False
    
    def stop_control_systems(self):
        """
        Stop temperature and humidity control systems.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            # Stop temperature controller
            temp_result = self.temp_controller.stop()
            
            # Stop humidity controller
            humidity_result = self.humidity_controller.stop()
            
            if temp_result and humidity_result:
                print("Temperature and humidity control systems stopped")
                return True
            else:
                print("Error stopping control systems")
                return False
        except Exception as e:
            print(f"Error stopping control systems: {e}")
            return False
    
    def test_relay_system(self):
        """
        Test the relay system by cycling through all relays.
        
        Returns:
            bool: True if test completed successfully, False otherwise
        """
        if not self.is_initialized:
            print("Incubator system not initialized")
            return False
            
        try:
            print("Testing relay system...")
            
            # Test each relay
            for i in range(self.relay.num_relays):
                print(f"Testing {self.relay.relay_names[i]} (Relay {i})")
                self.relay.turn_on(i)
                time.sleep(1)
                self.relay.turn_off(i)
                time.sleep(0.5)
            
            print("Relay system test completed successfully")
            return True
        except Exception as e:
            print(f"Error testing relay system: {e}")
            return False
    
    def test_sensor(self, readings=5, interval=2):
        """
        Test the SHT30 sensor by taking multiple readings.
        
        Args:
            readings: Number of readings to take (default: 5)
            interval: Interval between readings in seconds (default: 2)
            
        Returns:
            bool: True if test completed successfully, False otherwise
        """
        if not self.is_initialized:
            print("Incubator system not initialized")
            return False
            
        try:
            print("Testing SHT30 sensor...")
            
            # Take multiple readings
            for i in range(readings):
                temp_c, temp_f, humidity = self.sensor.read_temperature_humidity()
                
                if temp_c is not None and humidity is not None:
                    print(f"Reading {i+1}:")
                    print(f"  Temperature: {temp_c:.2f}°C / {temp_f:.2f}°F")
                    print(f"  Humidity: {humidity:.2f}%")
                    print(f"  Sensor active: {self.sensor.is_active()}")
                else:
                    print(f"Reading {i+1}: Error reading sensor")
                    print(f"  Sensor active: {self.sensor.is_active()}")
                
                if i < readings - 1:
                    time.sleep(interval)
            
            print("Sensor test completed successfully")
            return True
        except Exception as e:
            print(f"Error testing sensor: {e}")
            return False
    
    def test_safety_features(self):
        """
        Test the safety features of the system.
        
        Returns:
            bool: True if test completed successfully, False otherwise
        """
        if not self.is_initialized:
            print("Incubator system not initialized")
            return False
            
        try:
            print("Testing safety features...")
            
            # Start temperature controller
            self.temp_controller.start()
            print("Temperature controller started")
            
            # Wait for a moment
            time.sleep(2)
            
            # 1. Test sensor failure detection
            print("\n1. Testing sensor failure detection...")
            print("Simulating sensor failure by setting last_successful_read to a past time")
            # Directly modify the sensor's last_successful_read time to simulate failure
            # Note: In a real system, this would happen when the sensor becomes disconnected
            original_time = self.sensor.last_successful_read
            self.sensor.last_successful_read = time.time() - (self.temp_controller.sensor_timeout + 10)
            
            # Wait for the controller to detect the failure
            print("Waiting for controller to detect sensor failure...")
            time.sleep(5)
            
            # Check if heaters were turned off
            temp_status = self.temp_controller.get_status()
            if temp_status['sensor_failure'] and not temp_status['heater1_status'] and not temp_status['heater2_status']:
                print("PASS: Sensor failure detected and heaters turned off")
            else:
                print("FAIL: Sensor failure not detected or heaters not turned off")
            
            # Restore the original time
            self.sensor.last_successful_read = original_time
            print("Sensor restored to normal operation")
            time.sleep(5)
            
            # 2. Test overheat sensor
            print("\n2. Testing overheat sensor...")
            print("Simulating overheat condition by triggering the overheat callback")
            # Directly trigger the overheat callback to simulate the sensor opening
            self.relay._overheat_sensor_callback(self.relay.overheat_sensor_pin)
            self.relay.overheat_triggered = True
            
            # Wait for the controller to detect the overheat condition
            print("Waiting for controller to detect overheat condition...")
            time.sleep(5)
            
            # Check if heaters were turned off
            temp_status = self.temp_controller.get_status()
            if temp_status['overheat_triggered'] and not temp_status['heater1_status'] and not temp_status['heater2_status']:
                print("PASS: Overheat condition detected and heaters turned off")
            else:
                print("FAIL: Overheat condition not detected or heaters not turned off")
            
            # Restore normal operation
            self.relay.overheat_triggered = False
            self.relay._overheat_sensor_callback(self.relay.overheat_sensor_pin)
            print("Overheat sensor restored to normal operation")
            
            # Stop temperature controller
            self.temp_controller.stop()
            print("Temperature controller stopped")
            
            print("Safety features test completed")
            return True
        except Exception as e:
            print(f"Error testing safety features: {e}")
            # Make sure to stop the controller
            self.temp_controller.stop()
            return False
    
    def cleanup(self):
        """
        Clean up all resources.
        
        Returns:
            bool: True if cleaned up successfully, False otherwise
        """
        try:
            # Stop monitoring if running
            if self.is_running:
                self.stop_monitoring()
            
            # Stop control systems
            self.stop_control_systems()
            
            # Clean up controllers
            self.temp_controller.cleanup()
            self.humidity_controller.cleanup()
            
            print("Incubator system cleaned up")
            return True
        except Exception as e:
            print(f"Error cleaning up incubator system: {e}")
            return False


def main():
    """Main function for testing the incubator system."""
    parser = argparse.ArgumentParser(description='Incubator Controller Integration Test')
    parser.add_argument('--test-only', action='store_true', help='Run tests only, do not start control systems')
    parser.add_argument('--monitor-only', action='store_true', help='Monitor only, do not start control systems')
    parser.add_argument('--safety-test', action='store_true', help='Run safety features test')
    parser.add_argument('--duration', type=int, default=60, help='Test duration in seconds (default: 60)')
    parser.add_argument('--interval', type=int, default=5, help='Monitoring interval in seconds (default: 5)')
    args = parser.parse_args()
    
    try:
        # Create incubator system
        system = IncubatorSystem()
        
        # Check if system is initialized
        if not system.is_initialized:
            print("Failed to initialize incubator system. Check hardware connections.")
            return
        
        # Test sensor
        system.test_sensor()
        
        # Test relay system
        system.test_relay_system()
        
        # Test safety features if requested
        if args.safety_test:
            system.test_safety_features()
        
        # Start monitoring
        system.start_monitoring(inte<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>