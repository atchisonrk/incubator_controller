// JavaScript for Incubator Controller Web Interface

// DOM Elements
const connectionStatus = document.getElementById('connection-status');
const currentTemp = document.getElementById('current-temp');
const currentHumidity = document.getElementById('current-humidity');
const heater1Indicator = document.getElementById('heater1-indicator').querySelector('span');
const heater2Indicator = document.getElementById('heater2-indicator').querySelector('span');
const humidifierIndicator = document.getElementById('humidifier-indicator').querySelector('span');
const safetyIndicator = document.getElementById('safety-indicator').querySelector('span');

const tempControlToggle = document.getElementById('temp-control-toggle');
const humidityControlToggle = document.getElementById('humidity-control-toggle');

const tempTarget = document.getElementById('temp-target');
const tempMin = document.getElementById('temp-min');
const tempMax = document.getElementById('temp-max');
const tempSafety = document.getElementById('temp-safety');

const humidityTarget = document.getElementById('humidity-target');
const humidityMin = document.getElementById('humidity-min');
const humidityMax = document.getElementById('humidity-max');

const saveTempSettings = document.getElementById('save-temp-settings');
const saveHumiditySettings = document.getElementById('save-humidity-settings');
const resetSystem = document.getElementById('reset-system');

// Variables
let statusUpdateInterval;
let isConnected = true;
let lastUpdateTime = 0;

// Initialize the page
function init() {
    // Load initial settings
    loadSettings();
    
    // Start status updates
    startStatusUpdates();
    
    // Set up event listeners
    setupEventListeners();
}

// Load settings from the server
function loadSettings() {
    fetch('/api/settings')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load settings');
            }
            return response.json();
        })
        .then(settings => {
            // Update temperature settings
            tempTarget.value = settings.temp_target;
            tempMin.value = settings.temp_min;
            tempMax.value = settings.temp_max;
            tempSafety.value = settings.temp_safety;
            
            // Update humidity settings
            humidityTarget.value = settings.humidity_target;
            humidityMin.value = settings.humidity_min;
            humidityMax.value = settings.humidity_max;
            
            // Update toggle switches
            tempControlToggle.checked = settings.temp_control_enabled;
            humidityControlToggle.checked = settings.humidity_control_enabled;
        })
        .catch(error => {
            console.error('Error loading settings:', error);
            showConnectionError();
        });
}

// Start periodic status updates
function startStatusUpdates() {
    // Update status immediately
    updateStatus();
    
    // Set up interval for periodic updates
    statusUpdateInterval = setInterval(updateStatus, 5000);
}

// Update status from the server
function updateStatus() {
    fetch('/api/status')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to get status');
            }
            return response.json();
        })
        .then(status => {
            // Update connection status
            if (!isConnected) {
                showConnectionRestored();
            }
            
            // Update temperature display
            if (status.temperature.current !== null) {
                currentTemp.textContent = status.temperature.current.toFixed(1);
            } else {
                currentTemp.textContent = '--.-';
            }
            
            // Update humidity display
            if (status.humidity.current !== null) {
                currentHumidity.textContent = status.humidity.current.toFixed(1);
            } else {
                currentHumidity.textContent = '--.-';
            }
            
            // Update heater status indicators
            updateHeaterStatus(heater1Indicator, status.temperature.heater1_status);
            updateHeaterStatus(heater2Indicator, status.temperature.heater2_status);
            
            // Update humidifier status indicator
            updateHeaterStatus(humidifierIndicator, status.humidity.humidifier_status);
            
            // Update safety status
            if (status.temperature.safety_triggered) {
                safetyIndicator.textContent = 'TRIGGERED';
                safetyIndicator.className = 'danger';
            } else {
                safetyIndicator.textContent = 'Normal';
                safetyIndicator.className = '';
            }
            
            // Update toggle switches if they don't match the server state
            if (tempControlToggle.checked !== status.temperature.control_enabled) {
                tempControlToggle.checked = status.temperature.control_enabled;
            }
            
            if (humidityControlToggle.checked !== status.humidity.control_enabled) {
                humidityControlToggle.checked = status.humidity.control_enabled;
            }
            
            // Update last update time
            lastUpdateTime = Date.now();
        })
        .catch(error => {
            console.error('Error updating status:', error);
            showConnectionError();
        });
}

// Update heater/humidifier status display
function updateHeaterStatus(element, isOn) {
    if (isOn) {
        element.textContent = 'ON';
        element.className = 'on';
    } else {
        element.textContent = 'OFF';
        element.className = 'off';
    }
}

// Show connection error
function showConnectionError() {
    isConnected = false;
    connectionStatus.textContent = 'Disconnected';
    connectionStatus.className = 'disconnected';
    connectionStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Disconnected';
}

// Show connection restored
function showConnectionRestored() {
    isConnected = true;
    connectionStatus.textContent = 'Connected';
    connectionStatus.className = 'connected';
    connectionStatus.innerHTML = '<i class="fas fa-wifi"></i> Connected';
}

// Set up event listeners
function setupEventListeners() {
    // Temperature control toggle
    tempControlToggle.addEventListener('change', function() {
        const isEnabled = this.checked;
        
        fetch('/api/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                temp_control: isEnabled
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update temperature control');
            }
            return response.json();
        })
        .then(data => {
            console.log('Temperature control updated:', isEnabled ? 'enabled' : 'disabled');
        })
        .catch(error => {
            console.error('Error updating temperature control:', error);
            // Revert toggle if there was an error
            this.checked = !isEnabled;
        });
    });
    
    // Humidity control toggle
    humidityControlToggle.addEventListener('change', function() {
        const isEnabled = this.checked;
        
        fetch('/api/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                humidity_control: isEnabled
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update humidity control');
            }
            return response.json();
        })
        .then(data => {
            console.log('Humidity control updated:', isEnabled ? 'enabled' : 'disabled');
        })
        .catch(error => {
            console.error('Error updating humidity control:', error);
            // Revert toggle if there was an error
            this.checked = !isEnabled;
        });
    });
    
    // Save temperature settings
    saveTempSettings.addEventListener('click', function() {
        const settings = {
            temp_target: parseFloat(tempTarget.value),
            temp_min: parseFloat(tempMin.value),
            temp_max: parseFloat(tempMax.value),
            temp_safety: parseFloat(tempSafety.value)
        };
        
        // Validate settings
        if (settings.temp_min >= settings.temp_max) {
            alert('Minimum temperature must be less than maximum temperature');
            return;
        }
        
        if (settings.temp_max >= settings.temp_safety) {
            alert('Maximum temperature must be less than safety cutoff temperature');
            return;
        }
        
        if (settings.temp_target < settings.temp_min || settings.temp_target > settings.temp_max) {
            alert('Target temperature must be between minimum and maximum temperature');
            return;
        }
        
        // Send settings to server
        fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to save temperature settings');
            }
            return response.json();
        })
        .then(data => {
            alert('Temperature settings saved successfully');
        })
        .catch(error => {
            console.error('Error saving temperature settings:', error);
            alert('Failed to save temperature settings');
        });
    });
    
    // Save humidity settings
    saveHumiditySettings.addEventListener('click', function() {
        const settings = {
            humidity_target: parseFloat(humidityTarget.value),
            humidity_min: parseFloat(humidityMin.value),
            humidity_max: parseFloat(humidityMax.value)
        };
        
        // Validate settings
        if (settings.humidity_min >= settings.humidity_max) {
            alert('Minimum humidity must be less than maximum humidity');
            return;
        }
        
        if (settings.humidity_target < settings.humidity_min || settings.humidity_target > settings.humidity_max) {
            alert('Target humidity must be between minimum and maximum humidity');
            return;
        }
        
        // Send settings to server
        fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to save humidity settings');
            }
            return response.json();
        })
        .then(data => {
            alert('Humidity settings saved successfully');
        })
        .catch(error => {
            console.error('Error saving humidity settings:', error);
            alert('Failed to save humidity settings');
        });
    });
    
    // Reset system
    resetSystem.addEventListener('click', function() {
        if (confirm('Are you sure you want to reset the system? This will stop all control systems and restart them.')) {
            fetch('/api/reset', {
                method: 'POST'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to reset system');
                }
                return response.json();
            })
            .then(data => {
                alert('System reset successfully');
                // Reload settings and status
                loadSettings();
                updateStatus();
            })
            .catch(error => {
                console.error('Error resetting system:', error);
                alert('Failed to reset system');
            });
        }
    });
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', init);

// Check connection status periodically
setInterval(function() {
    if (Date.now() - lastUpdateTime > 15000) {
        showConnectionError();
    }
}, 5000);
