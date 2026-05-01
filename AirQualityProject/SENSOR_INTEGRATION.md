# 📡 Sensor Integration Guide

## How to Send Real Sensor Data to Your Dashboard

---

## 🔌 Supported Sensors

| Sensor | Measurement | Range | Protocol |
|--------|-------------|-------|----------|
| **MQ-135** | Air Quality (PPM) | 0-1000 | Analog + ADC |
| **DHT22** | Temperature + Humidity | -40 to 80°C, 0-100% | Digital |
| **DHT11** | Temperature + Humidity | 0 to 50°C, 20-80% | Digital |
| **BMP180** | Temperature + Pressure | -40 to 85°C | I2C |
| **BMP280** | Temperature + Pressure | -40 to 85°C | I2C |

---

## 🚀 API Endpoint

### POST `/send_sensor_data`

**URL**: `http://your-server:5000/send_sensor_data`  
**Method**: `POST`  
**Content-Type**: `application/json`

### Request Body

```json
{
  "aqi_raw": 245.5,       // MQ-135 raw reading (0-1000)
  "temperature": 28.5,     // Temperature in Celsius (-50 to 60)
  "humidity": 65           // Humidity in % (0-100)
}
```

### Response

```json
{
  "success": true,
  "message": "Sensor data received and processed",
  "aqi": {
    "raw": 245.5,
    "filtered": 225.8,
    "value": 225.8,
    "status": "Warning",
    "advice": "Moderate pollution. Use an air purifier."
  },
  "temperature": {
    "value": 28.5,
    "status": "Warm",
    "advice": "Warm weather. Stay hydrated."
  },
  "humidity": {
    "value": 65,
    "status": "Moderate",
    "advice": "Moderate humidity. Comfortable for most."
  },
  "timestamp": "2026-03-20T10:30:45.123456"
}
```

---

## 💻 Implementation Examples

### 🐍 Python (with Arduino/Raspberry Pi)

```python
import requests
import serial
import json
from time import sleep

# Connect to Arduino/ESP32 via Serial
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Windows: 'COM3'

def send_sensor_data(aqi, temp, humidity):
    """Send sensor data to Flask server"""
    url = 'http://localhost:5000/send_sensor_data'
    
    payload = {
        'aqi_raw': float(aqi),
        'temperature': float(temp),
        'humidity': float(humidity)
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data.get('success'):
            print(f"✅ Data sent - AQI: {data['aqi']['value']} | Temp: {data['temperature']['value']}°C")
        else:
            print(f"❌ Error: {data.get('error')}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

# Main loop
while True:
    try:
        # Read from serial (format: "AQI,TEMP,HUMIDITY\n")
        line = ser.readline().decode().strip()
        
        if line:
            aqi, temp, humidity = line.split(',')
            print(f"📡 Received: AQI={aqi}, Temp={temp}°C, Humidity={humidity}%")
            send_sensor_data(aqi, temp, humidity)
        
        sleep(2)  # Send every 2 seconds
    
    except KeyboardInterrupt:
        print("Stopping...")
        break
    except Exception as e:
        print(f"Error: {e}")

ser.close()
```

### 🔌 Arduino with MQ-135 + DHT22

```cpp
#include <DHT.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Sensor pins
#define MQ135_PIN A0         // MQ-135 analog pin
#define DHT_PIN 4            // DHT22 data pin
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://YOUR_SERVER_IP:5000/send_sensor_data";

// MQ-135 calibration
const float R0 = 76.63;  // Calibration resistance

void setup() {
    Serial.begin(9600);
    dht.begin();
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected!");
}

void loop() {
    // Read MQ-135
    int rawADC = analogRead(MQ135_PIN);
    float voltage = (rawADC / 1024.0) * 5.0;
    float RS = ((5.0 - voltage) / voltage) * 10000;  // Assume RL = 10k
    float ratio = RS / R0;
    
    // Convert to PPM (MQ-135 characteristic)
    float ppm = 118.1 * pow(ratio, -2.769);  // Formula for air quality
    ppm = max(0.0, min(1000.0, ppm));  // Clamp to 0-1000
    
    // Read DHT22
    float temp = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    if (isnan(temp) || isnan(humidity)) {
        Serial.println("DHT read error!");
        temp = 25.0;
        humidity = 50.0;
    }
    
    // Send via HTTP
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverUrl);
        http.addHeader("Content-Type", "application/json");
        
        String jsonData = "{\"aqi_raw\":" + String(ppm, 1) + 
                         ",\"temperature\":" + String(temp, 1) + 
                         ",\"humidity\":" + String(humidity, 1) + "}";
        
        int httpCode = http.POST(jsonData);
        
        if (httpCode == 200) {
            Serial.print("✅ Sent: AQI=");
            Serial.print(ppm, 1);
            Serial.print(" | Temp=");
            Serial.print(temp, 1);
            Serial.print("°C | Humidity=");
            Serial.println(humidity, 1);
        } else {
            Serial.println("❌ Send failed: " + String(httpCode));
        }
        
        http.end();
    }
    
    // Send every 2 seconds
    delay(2000);
}
```

### 🔌 Raspberry Pi with MQ-135 + DHT22

```python
import Adafruit_DHT
import Adafruit_ADS1x15
import requests
from time import sleep

# Setup sensors
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
adc = Adafruit_ADS1x15.ADS1115()

# MQ-135 calibration
R0 = 76.63

def read_mq135():
    """Read MQ-135 and convert to PPM"""
    reading = adc.read_adc(0, gain=1)  # A0
    voltage = (reading / 32767.0) * 4.096  # 16-bit ADC, 4.096V ref
    RS = ((4.096 - voltage) / voltage) * 10000  # RL = 10k
    ratio = RS / R0
    ppm = 118.1 * pow(ratio, -2.769)
    return max(0, min(1000, ppm))

def send_data():
    """Read sensors and send to server"""
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    aqi = read_mq135()
    
    if temperature and humidity:
        data = {
            'aqi_raw': aqi,
            'temperature': temperature,
            'humidity': humidity
        }
        
        try:
            response = requests.post('http://localhost:5000/send_sensor_data', json=data)
            print(f"✅ Sent: AQI={aqi:.1f} | Temp={temperature:.1f}°C | Humidity={humidity:.1f}%")
        except Exception as e:
            print(f"❌ Error: {e}")

# Main loop
while True:
    send_data()
    sleep(2)  # Send every 2 seconds
```

### 📱 cURL Command

```bash
# Send sample data
curl -X POST http://localhost:5000/send_sensor_data \
  -H "Content-Type: application/json" \
  -d '{
    "aqi_raw": 245,
    "temperature": 28.5,
    "humidity": 65
  }'

# Response
{
  "success": true,
  "message": "Sensor data received and processed",
  "aqi": {...},
  "temperature": {...},
  "humidity": {...}
}
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Make sure Flask app is running on `localhost:5000` |
| Invalid JSON | Check JSON syntax, use `json.dumps()` in Python |
| Timeout error | Server might be busy, add retry logic |
| Wrong data format | Ensure aqi_raw is a number, not string |
| Cannot import requests | `pip install requests` |
| Cannot import DHT library | `pip install Adafruit-DHT` |

---

## 📊 Expected Data Ranges

- **AQI (PPM)**: 0-1000 (Higher = more pollution)
- **Temperature**: -50 to 60 °C
- **Humidity**: 0-100 %

Out-of-range values will be automatically clamped to safe limits.

---

## 🎯 Next Steps

1. **Setup your sensor hardware** - Follow the example code for your platform
2. **Update WiFi/serial credentials** - Configure for your network
3. **Test connection** - Use cURL command first
4. **Deploy script** - Run continuously using cron (Raspberry Pi) or Task Scheduler (Windows)
5. **Monitor dashboard** - Watch real-time data at `http://localhost:5000`

---

## 📚 Sensor Specifications

### MQ-135 Air Quality Sensor
- **Range**: 10-1000 PPM CO2 equivalent
- **Response Time**: 15 sec
- **Requires**: ADC converter (ADS1115 for Raspberry Pi)
- **Calibration**: Required in fresh air for accuracy

### DHT22 Temperature/Humidity
- **Temp Range**: -40 to 80°C (accuracy: ±0.5°C)
- **Humidity Range**: 0-100% (accuracy: ±2%)
- **Response Time**: 2 seconds

---

## ✅ You're ready to integrate real sensors! 🎉

Once running, your dashboard will display live environmental data with AI-powered health recommendations.
