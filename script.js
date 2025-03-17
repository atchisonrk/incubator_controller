// script.js - JavaScript for Raspberry Pi Incubator Controller

// DOM Elements
const currentTemp = document.getElementById('current-temp');
const currentHumidity = document.getElementById('current-humidity');
const heater1Status = document.getElementById('heater1-status');
const heater2Status = document.getElementById('heater2-status');
const humidifierStatus = document.getElementById('humidifier-status');
const tempSafetyStatus = document.getElementById('temp-safety-status');
const sensorStatus = document.getElementById('sensor-status');
const overheatStatus = document.getElementById('overheat-status');
const lastUpdate = document.getElementById('last-update');

const tempControlToggle = document.getElementById('temp-control-toggle');
const humidityControlToggle = document.getElementById('humidity-control-toggle');

const startAllBtn = document.getElementById('start-all-btn');
const stopAllBtn = document.getElementById('stop-all-btn');
const resetBtn = document.getElementById('reset-btn');

const tempSettingsForm = document.getElementById('temp-settings-form');
const humiditySettingsForm = document.getElementById('humidity-settings-form');

// Update status display
function updateStatusDisplay(status) {
    // Update temperature display
    if (status.temperature.current !== null) {
        currentTemp.textContent = `${status.temperature.current.toFixed(1)} °F`;
    } else {
        currentTemp.textContent = 'Sensor Error';
        currentTemp.classList.add('status-danger');
    }

    // Update humidity display
    if (status.humidity.current !== null) {
        currentHumidity.textContent = `${status.humidity.current.toFixed(1)} %`;
    } else {
        currentHumidity.textContent = 'Sensor Error';
        currentHumidity.classList.add('status-danger');
    }

    // Update heater status
    heater1Status.textContent = status.temperature.heater1_status ? 'ON' : 'OFF';
    heater1Status.className = 'status ' + (status.temperature.heater1_status ? 'status-on' : 'status-off');
    
    heater2Status.textContent = status.temperature.heater2_status ? 'ON' : 'OFF';
    heater2Status.className = 'status ' + (status.temperature.heater2_status ? 'status-on' : 'status-off');
    
    // Update humidifier status
    humidifierStatus.textContent = status.humidity.humidifier_status ? 'ON' : 'OFF';
    humidifierStatus.className = 'status ' + (status.humidity.humidifier_status ? 'status-on' : 'status-off');
    
    // Update safety status
    if (status.temperature.safety_triggered) {
        tempSafetyStatus.textContent = 'SAFETY CUTOFF';
        tempSafetyStatus.className = 'status status-danger';
    } else {
        tempSafetyStatus.textContent = 'OK';
        tempSafetyStatus.className = 'status status-on';
    }
    
    // Update sensor status
    if (status.temperature.sensor_failure || status.humidity.sensor_failure) {
        sensorStatus.textContent = 'FAILURE';
        sensorStatus.className = 'status status-danger';
    } else {
        sensorStatus.textContent = 'OK';
        sensorStatus.className = 'status status-on';
    }
    
    // Update overheat status
    if (status.temperature.overheat_triggered) {
        overheatStatus.textContent = 'OVERHEATING';
        overheatStatus.className = 'status status-danger';
    } else {
        overheatStatus.textContent = 'OK';
        overheatStatus.className = 'status status-on';
    }
    
    // Update last update time
    const date = new Date();
    lastUpdate.textContent = date.toLocaleTimeString();
    
    // Update toggle switches
    tempControlToggle.checked = status.temperature.is_running;
    humidityControlToggle.checked = status.humidity.is_running;
}

// Fetch status from API
function fetchStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(status => {
            updateStatusDisplay(status);
        })
        .catch(error => {
            console.error('Error fetching status:', error);
        });
}

// Control temperature system
function controlTemperature(action) {
    fetch(`/api/control/temperature/${action}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(data.message);
                fetchStatus();
            } else {
                console.error(data.message);
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error controlling temperature:', error);
        });
}

// Control humidity system
function controlHumidity(action) {
    fetch(`/api/control/humidity/${action}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(data.message);
                fetchStatus();
            } else {
                console.error(data.message);
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error controlling humidity:', error);
        });
}

// Control all systems
function controlAll(action) {
    fetch(`/api/control/all/${action}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(data.message);
                fetchStatus();
            } else {
                console.error(data.message);
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error controlling systems:', error);
        });
}

// Reset system
function resetSystem() {
    if (confirm('Are you sure you want to reset the system? This will stop all controls and restore default settings.')) {
        fetch('/api/reset')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(data.message);
                    // Reload page to get updated settings
                    location.reload();
                } else {
                    console.error(data.message);
                    alert(`Error: ${data.message}`);
                }
            })
            .catch(error => {
                console.error('Error resetting system:', error);
            });
    }
}

// Update temperature settings
function updateTemperatureSettings(event) {
    event.preventDefault();
    
    const settings = {
        temperature: {
            target: parseFloat(document.getElementById('temp-target').value),
            min: parseFloat(document.getElementById('temp-min').value),
            max: parseFloat(document.getElementById('temp-max').value),
            safety_cutoff: parseFloat(document.getElementById('temp-safety').value),
            sensor_timeout: parseInt(document.getElementById('sensor-timeout').value)
        }
    };
    
    // Validate settings
    if (settings.temperature.min >= settings.temperature.max) {
        alert('Minimum temperature must be less than maximum temperature.');
        return;
    }
    
    if (settings.temperature.target < settings.temperature.min || settings.temperature.target > settings.temperature.max) {
        alert('Target temperature must be within the minimum and maximum range.');
        return;
    }
    
    if (settings.temperature.safety_cutoff <= settings.temperature.max) {
        alert('Safety cutoff temperature must be greater than maximum temperature.');
        return;
    }
    
    if (settings.temperature.sensor_timeout < 5) {
        alert('Sensor timeout must be at least 5 seconds.');
        return;
    }
    
    // Send settings to API
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Temperature settings updated successfully.');
                // Update display
                document.getElementById('target-temp').textContent = settings.temperature.target;
                document.getElementById('min-temp').textContent = settings.temperature.min;
                document.getElementById('max-temp').textContent = settings.temperature.max;
                document.getElementById('safety-cutoff').textContent = settings.temperature.safety_cutoff;
                fetchStatus();
            } else {
                console.error(data.message);
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error updating temperature settings:', error);
        });
}

// Update humidity settings
function updateHumiditySettings(event) {
    event.preventDefault();
    
    const settings = {
        humidity: {
            target: parseInt(document.getElementById('humidity-target').value),
            min: parseInt(document.getElementById('humidity-min').value),
            max: parseInt(document.getElementById('humidity-max').value)
        }
    };
    
    // Validate settings
    if (settings.humidity.min >= settings.humidity.max) {
        alert('Minimum humidity must be less than maximum humidity.');
        return;
    }
    
    if (settings.humidity.target < settings.humidity.min || settings.humidity.target > settings.humidity.max) {
        alert('Target humidity must be within the minimum and maximum range.');
        return;
    }
    
    // Send settings to API
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Humidity settings updated successfully.');
                // Update display
                document.getElementById('target-humidity').textContent = settings.humidity.target;
                document.getElementById('min-humidity').textContent = settings.humidity.min;
                document.getElementById('max-humidity').textContent = settings.humidity.max;
                fetchStatus();
            } else {
                console.error(data.message);
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error updating humidity settings:', error);
        });
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initial status fetch
    fetchStatus();
    
    // Set up periodic status updates (every 5 seconds)
    setInterval(fetchStatus, 5000);
    
    // Temperature control toggle
    tempControlToggle.addEventListener('change', () => {
        if (tempControlToggle.checked) {
            controlTemperature('start');
        } else {
            controlTemperature('stop');
        }
    });
    
    // Humidity control toggle
    humidityControlToggle.addEventListener('change', () => {
        if (humidityControlToggle.checked) {
            controlHumidity('start');
        } else {
            controlHumidity('stop');
        }
    });
    
    // Start all button
    startAllBtn.addEventListener('click', () => {
        controlAll('start');
    });
    
    // Stop all button
    stopAllBtn.addEventListener('click', () => {
        controlAll('stop');
    });
    
    // Reset button
    resetBtn.addEventListener('click', resetSystem);
    
    // Temperature settings form
    tempSettingsForm.addEventListener('submit', updateTemperatureSettings);
    
    // Humidity settings form
    humiditySettingsForm.addEventListener('submit', updateHumiditySettings);
});
