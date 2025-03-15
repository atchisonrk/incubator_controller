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
                
                print("\nHumidity Control:")
                print(f"  Enabled: {humidity_status['is_running']}")
                print(f"  Target: {humidity_status['target_humidity']:.1f}%")
                print(f"  Range: {humidity_status['min_humidity']:.1f}% - {humidity_status['max_humidity']:.1f}%")
                print(f"  Humidifier: {'ON' if humidity_status['humidifier_status'] else 'OFF'}")
                
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
                else:
                    print(f"Reading {i+1}: Error reading sensor")
                
                if i < readings - 1:
                    time.sleep(interval)
            
            print("Sensor test completed successfully")
            return True
        except Exception as e:
            print(f"Error testing sensor: {e}")
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
        
        # Start monitoring
        system.start_monitoring(interval=args.interval)
        
        # Start control systems if not in test-only or monitor-only mode
        if not args.test_only and not args.monitor_only:
            system.start_control_systems()
            print(f"Control systems started. Running for {args.duration} seconds...")
        else:
            if args.test_only:
                print("Test-only mode. Control systems not started.")
            else:
                print("Monitor-only mode. Control systems not started.")
            print(f"Monitoring for {args.duration} seconds...")
        
        # Run for specified duration
        time.sleep(args.duration)
        
        # Stop control systems
        if not args.test_only and not args.monitor_only:
            system.stop_control_systems()
        
        # Stop monitoring
        system.stop_monitoring()
        
        # Clean up
        system.cleanup()
        
        print("Integration test completed successfully")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        if 'system' in locals():
            system.cleanup()
    except Exception as e:
        print(f"Error in integration test: {e}")
        if 'system' in locals():
            system.cleanup()


if __name__ == "__main__":
    main()
