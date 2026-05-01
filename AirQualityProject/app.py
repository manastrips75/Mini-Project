import subprocess
import random
import os
import shutil
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Get the directory where this script is located
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Global sensor data storage ---
LAST_SENSOR_DATA = {
    "aqi_raw": 0,
    "aqi_filtered": 0,
    "temperature": 25.0,
    "humidity": 50,
    "timestamp": datetime.now().isoformat()
}

# --- Historical data storage for predictions ---
HISTORICAL_DATA = []
MAX_HISTORY_SIZE = 100  # Keep last 100 readings for prediction

# --- Check if Java is available ---
def check_java_available():
    """Check if Java is installed and accessible"""
    return shutil.which('javac') is not None

# --- Compile Java Class (First Time Only) ---
def compile_java_class():
    """Compile DataProcessor.java if not already compiled"""
    java_file = os.path.join(PROJECT_DIR, 'DataProcessor.java')
    class_file = os.path.join(PROJECT_DIR, 'DataProcessor.class')
    
    # Check if javac is available
    if not check_java_available():
        print("\n" + "="*70)
        print("⚠️  JAVA NOT FOUND - Setting up workaround")
        print("="*70)
        print("❌ javac is not in your system PATH")
        print("\n📌 TO FIX THIS:")
        print("   1. Download JDK from: https://www.oracle.com/java/technologies/downloads/")
        print("   2. Run the installer and choose 'Add to PATH'")
        print("   3. Restart your terminal and run app.py again")
        print("\n🔧 FOR NOW: Using Python fallback simulation mode")
        print("="*70 + "\n")
        return False
    
    # Only compile if .class doesn't exist or .java is newer
    if not os.path.exists(class_file) or os.path.getmtime(java_file) > os.path.getmtime(class_file):
        try:
            print("[INFO] Compiling DataProcessor.java...")
            subprocess.run(['javac', java_file], check=True, capture_output=True)
            print("[SUCCESS] DataProcessor compiled successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Compilation failed: {e}")
            print("Make sure Java Development Kit (JDK) is installed and javac is in PATH")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return False
    else:
        print("[INFO] DataProcessor.class already compiled")
        return True

# Compile on startup (but don't fail if Java not available)
JAVA_AVAILABLE = compile_java_class()

# --- Intelligence Logic (Decision Tree) ---
def get_intelligence_report(aqi_value):
    if aqi_value < 150:
        return {"status": "Healthy", "color": "#2ecc71", "advice": "Air is clean. Keep windows open!"}
    elif aqi_value < 350:
        return {"status": "Warning", "color": "#f1c40f", "advice": "Moderate pollution. Use an air purifier."}
    else:
        return {"status": "Danger", "color": "#e74c3c", "advice": "Hazardous levels! Wear a mask outdoors."}

def get_temperature_report(temp):
    """Generate temperature-based health recommendations"""
    if temp < 10:
        return {"status": "Cold", "icon": "❄️", "advice": "Very cold! Dress warmly."}
    elif temp < 18:
        return {"status": "Cool", "icon": "🧊", "advice": "Cool temperature. Consider putting on a sweater."}
    elif temp <= 25:
        return {"status": "Comfortable", "icon": "😊", "advice": "Comfortable temperature. Ideal for activities."}
    elif temp <= 32:
        return {"status": "Warm", "icon": "☀️", "advice": "Warm weather. Stay hydrated."}
    else:
        return {"status": "Hot", "icon": "🔥", "advice": "Very hot! Avoid outdoor activities."}

def get_humidity_report(humidity):
    """Generate humidity-based health recommendations"""
    if humidity < 30:
        return {"status": "Dry", "icon": "🏜️", "advice": "Low humidity. Your skin may feel dry."}
    elif humidity < 50:
        return {"status": "Optimal", "icon": "✅", "advice": "Optimal humidity levels."}
    elif humidity <= 70:
        return {"status": "Moderate", "icon": "💧", "advice": "Moderate humidity. Comfortable for most."}
    else:
        return {"status": "High", "icon": "💦", "advice": "High humidity. May feel sticky."}

# --- Prediction Functions ---
def add_to_history(data):
    """Add new sensor data to historical storage"""
    global HISTORICAL_DATA
    HISTORICAL_DATA.append(data)
    if len(HISTORICAL_DATA) > MAX_HISTORY_SIZE:
        HISTORICAL_DATA.pop(0)  # Remove oldest data

def predict_future_values(hours_ahead=24):
    """Predict future temperature and AQI values using trend analysis"""
    if len(HISTORICAL_DATA) < 5:  # Need minimum data points
        return None

    # Prepare data for prediction
    df = pd.DataFrame(HISTORICAL_DATA)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    predictions = {}

    # Predict temperature using simple trend
    if len(df) >= 3:
        try:
            # Calculate trend (slope) from recent data
            recent_temp = df['temperature'].tail(10)  # Use last 10 points
            if len(recent_temp) >= 2:
                temp_trend = (recent_temp.iloc[-1] - recent_temp.iloc[0]) / len(recent_temp)
            else:
                temp_trend = 0

            current_temp = float(df['temperature'].iloc[-1])
            temp_predictions = []

            for hour in range(1, hours_ahead + 1):
                # Add some random variation but keep trend
                variation = np.random.normal(0, 0.5)  # Small random variation
                predicted_temp = current_temp + (temp_trend * hour) + variation
                predicted_temp = np.clip(predicted_temp, -50, 60)  # Reasonable range
                temp_predictions.append(float(predicted_temp))

            predictions['temperature'] = {
                'current': current_temp,
                'predictions': temp_predictions,
                'hours_ahead': list(range(1, hours_ahead + 1))
            }
        except Exception as e:
            print(f"Temperature prediction error: {e}")
            predictions['temperature'] = None

    # Predict AQI using simple trend
    if len(df) >= 3:
        try:
            # Calculate trend from recent data
            recent_aqi = df['aqi_filtered'].tail(10)  # Use last 10 points
            if len(recent_aqi) >= 2:
                aqi_trend = (recent_aqi.iloc[-1] - recent_aqi.iloc[0]) / len(recent_aqi)
            else:
                aqi_trend = 0

            current_aqi = float(df['aqi_filtered'].iloc[-1])
            aqi_predictions = []

            for hour in range(1, hours_ahead + 1):
                # Add some random variation but keep trend
                variation = np.random.normal(0, 5)  # Moderate random variation for AQI
                predicted_aqi = current_aqi + (aqi_trend * hour) + variation
                predicted_aqi = max(0, predicted_aqi)  # Ensure non-negative
                aqi_predictions.append(float(predicted_aqi))

            predictions['aqi'] = {
                'current': current_aqi,
                'predictions': aqi_predictions,
                'hours_ahead': list(range(1, hours_ahead + 1))
            }
        except Exception as e:
            print(f"AQI prediction error: {e}")
            predictions['aqi'] = None

    return predictions

# --- Java Bridge (Subprocess with Circular Queue) ---
def get_dsa_filtered_value(raw_val):
    """
    Sends raw sensor reading to Java DataProcessor
    Java uses a circular queue (size=5) to compute moving average
    Returns the filtered value
    
    Falls back to Python simulation if Java is not available
    """
    if not JAVA_AVAILABLE:
        # Python fallback: simulate the circular queue logic
        filtered_value = raw_val * 0.92
        print(f"[SENSOR] Raw: {raw_val} → [PYTHON FALLBACK] Smoothed: {filtered_value}")
        return filtered_value
    
    try:
        # Execute from the project directory to find the DataProcessor class
        cmd = ['java', '-cp', PROJECT_DIR, 'DataProcessor', str(raw_val)]
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, cwd=PROJECT_DIR, timeout=5)
        filtered_value = float(result.strip())
        print(f"[SENSOR] Raw: {raw_val} → [JAVA DSA] Filtered: {filtered_value}")
        return filtered_value
    except subprocess.CalledProcessError as e:
        print(f"[JAVA ERROR] {e.output}")
        return raw_val
    except subprocess.TimeoutExpired:
        print(f"[JAVA ERROR] Java process timed out")
        return raw_val
    except Exception as e:
        print(f"[BRIDGE ERROR] {e}")
        return raw_val

# --- Routes ---
@app.route('/')
def home():
    # Get current predictions for the dashboard
    predictions = predict_future_values(hours_ahead=6)  # Show 6-hour predictions on dashboard
    
    return render_template('index.html', predictions=predictions)

@app.route('/sensor_data', methods=['GET'])
def sensor_data():
    """GET: Returns current sensor data (simulated or real)"""
    global LAST_SENSOR_DATA
    
    # Check if using simulated data or real data
    use_simulation = request.args.get('simulate', 'true').lower() == 'true'
    
    if use_simulation:
        # 1. Simulate Raw Sensor Data (from MQ-135 Sensor)
        raw_reading = random.randint(50, 600)
        temp_reading = round(random.uniform(15, 35), 1)
        humidity_reading = random.randint(30, 80)
    else:
        # Use last stored real data
        raw_reading = LAST_SENSOR_DATA.get("aqi_raw", random.randint(50, 600))
        temp_reading = LAST_SENSOR_DATA.get("temperature", 25.0)
        humidity_reading = LAST_SENSOR_DATA.get("humidity", 50)
    
    # 2. Process via Java (DSA Circular Queue Logic)
    filtered_reading = get_dsa_filtered_value(raw_reading)
    
    # 3. Get AI Intelligence Reports
    aqi_insight = get_intelligence_report(filtered_reading)
    temp_insight = get_temperature_report(temp_reading)
    humidity_insight = get_humidity_report(humidity_reading)
    
    # Store current reading
    LAST_SENSOR_DATA = {
        "aqi_raw": raw_reading,
        "aqi_filtered": filtered_reading,
        "temperature": temp_reading,
        "humidity": humidity_reading,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add to historical data for predictions
    add_to_history(LAST_SENSOR_DATA.copy())
    
    # Include prediction result in sensor output so UI can show 24h forecast without hardware
    prediction_result = predict_future_values(24)

    return jsonify({
        "aqi": {
            "raw": raw_reading,
            "filtered": filtered_reading,
            "value": round(filtered_reading, 2),
            "status": aqi_insight['status'],
            "color": aqi_insight['color'],
            "advice": aqi_insight['advice']
        },
        "temperature": {
            "value": temp_reading,
            "status": temp_insight['status'],
            "icon": temp_insight['icon'],
            "advice": temp_insight['advice']
        },
        "humidity": {
            "value": humidity_reading,
            "status": humidity_insight['status'],
            "icon": humidity_insight['icon'],
            "advice": humidity_insight['advice']
        },
        "predictions": prediction_result,
        "timestamp": LAST_SENSOR_DATA['timestamp']
    })

@app.route('/send_sensor_data', methods=['POST'])
def send_sensor_data():
    """
    POST: Receive real sensor data from MQ-135, DHT22, etc.
    
    Expected JSON:
    {
        "aqi_raw": 245.5,           # MQ-135 raw reading (0-1023 or PPM value)
        "temperature": 28.5,        # Temperature in Celsius (DHT22, BMP180, etc.)
        "humidity": 65              # Humidity in % (DHT22, DHT11, etc.)
    }
    
    Example cURL:
    curl -X POST http://localhost:5000/send_sensor_data \\
         -H "Content-Type: application/json" \\
         -d '{"aqi_raw": 245, "temperature": 28.5, "humidity": 65}'
    """
    global LAST_SENSOR_DATA
    
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        aqi_raw = data.get('aqi_raw')
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        
        # Check required field
        if aqi_raw is None:
            return jsonify({"error": "Missing 'aqi_raw' field"}), 400
        
        # Validate values
        try:
            aqi_raw = float(aqi_raw)
            temperature = float(temperature) if temperature is not None else 25.0
            humidity = float(humidity) if humidity is not None else 50
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid sensor values. Must be numbers."}), 400
        
        # Clamp values to reasonable ranges
        aqi_raw = max(0, min(1000, aqi_raw))  # 0-1000 PPM
        temperature = max(-50, min(60, temperature))  # -50 to 60 Celsius
        humidity = max(0, min(100, humidity))  # 0-100 %
        
        # Process through DSA
        filtered_aqi = get_dsa_filtered_value(aqi_raw)
        
        # Get intelligence reports
        aqi_insight = get_intelligence_report(filtered_aqi)
        temp_insight = get_temperature_report(temperature)
        humidity_insight = get_humidity_report(humidity)
        
        # Update global data
        LAST_SENSOR_DATA = {
            "aqi_raw": aqi_raw,
            "aqi_filtered": filtered_aqi,
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to historical data for predictions
        add_to_history(LAST_SENSOR_DATA.copy())
        
        print(f"[MQ-135] Raw: {aqi_raw} → Filtered: {filtered_aqi} | Temp: {temperature}°C | Humidity: {humidity}%")
        
        return jsonify({
            "success": True,
            "message": "Sensor data received and processed",
            "aqi": {
                "raw": aqi_raw,
                "filtered": filtered_aqi,
                "value": round(filtered_aqi, 2),
                "status": aqi_insight['status'],
                "advice": aqi_insight['advice']
            },
            "temperature": {
                "value": temperature,
                "status": temp_insight['status'],
                "advice": temp_insight['advice']
            },
            "humidity": {
                "value": humidity,
                "status": humidity_insight['status'],
                "advice": humidity_insight['advice']
            },
            "timestamp": LAST_SENSOR_DATA['timestamp']
        }), 200
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/predictions', methods=['GET'])
def get_predictions():
    """GET: Returns AI predictions for future temperature and AQI"""
    hours_ahead = int(request.args.get('hours', 24))  # Default 24 hours
    
    if hours_ahead < 1 or hours_ahead > 168:  # Max 1 week
        return jsonify({"error": "Hours ahead must be between 1 and 168"}), 400
    
    predictions = predict_future_values(hours_ahead)
    
    if predictions is None:
        return jsonify({
            "error": "Not enough historical data for predictions. Need at least 10 data points.",
            "data_points": len(HISTORICAL_DATA)
        }), 400
    
    # Add intelligence to predictions
    response = {
        "predictions_available": True,
        "data_points_used": len(HISTORICAL_DATA),
        "hours_ahead": hours_ahead,
        "generated_at": datetime.now().isoformat()
    }
    
    if predictions.get('temperature'):
        temp_data = predictions['temperature']
        response['temperature'] = {
            "current": temp_data['current'],
            "forecast": []
        }
        
        for i, pred_temp in enumerate(temp_data['predictions']):
            hours = temp_data['hours_ahead'][i]
            insight = get_temperature_report(pred_temp)
            response['temperature']['forecast'].append({
                "hours_ahead": hours,
                "predicted_value": round(pred_temp, 1),
                "status": insight['status'],
                "icon": insight['icon'],
                "advice": insight['advice']
            })
    
    if predictions.get('aqi'):
        aqi_data = predictions['aqi']
        response['aqi'] = {
            "current": aqi_data['current'],
            "forecast": []
        }
        
        for i, pred_aqi in enumerate(aqi_data['predictions']):
            hours = aqi_data['hours_ahead'][i]
            insight = get_intelligence_report(pred_aqi)
            response['aqi']['forecast'].append({
                "hours_ahead": hours,
                "predicted_value": round(pred_aqi, 2),
                "status": insight['status'],
                "color": insight['color'],
                "advice": insight['advice']
            })
    
    return jsonify(response)

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation endpoint"""
    return jsonify({
        "title": "Air Quality & Environmental Monitoring API",
        "version": "1.0",
        "endpoints": {
            "GET /": "Dashboard (HTML)",
            "GET /sensor_data": {
                "description": "Get current sensor readings",
                "params": {
                    "simulate": "true/false - Use simulated or real data (default: true)"
                },
                "example": "http://localhost:5000/sensor_data?simulate=false"
            },
            "POST /send_sensor_data": {
                "description": "Send real sensor data to server",
                "content_type": "application/json",
                "body": {
                    "aqi_raw": "number - Air quality raw reading (0-1000 PPM)",
                    "temperature": "number - Temperature in Celsius",
                    "humidity": "number - Humidity in % (0-100)"
                },
                "example": {
                    "aqi_raw": 245.5,
                    "temperature": 28.5,
                    "humidity": 65
                }
            },
            "GET /predictions": {
                "description": "Get AI predictions for future temperature and AQI",
                "params": {
                    "hours": "number - Hours to predict ahead (1-168, default: 24)"
                },
                "example": "http://localhost:5000/predictions?hours=48"
            },
            "GET /api/docs": "This documentation"
        }
    })

if __name__ == '__main__':
    print("=" * 70)
    print("🌍 AI Air Quality Monitoring System")
    print("=" * 70)
    if JAVA_AVAILABLE:
        print("✅ Java DSA: ACTIVE (Circular Queue Processing)")
        print("   Sensor → Python (Flask) → Java (DSA) → Dashboard")
    else:
        print("⚠️  Java DSA: INACTIVE (Using Python Fallback)")
        print("   Sensor → Python (Flask) → Python Simulation → Dashboard")
        print("\n💡 To enable Java DSA:")
        print("   1. Install JDK: https://www.oracle.com/java/technologies/downloads/")
        print("   2. Add to PATH during installation")
        print("   3. Restart terminal and run this script again")
    print("=" * 70)
    print("🔗 Access: http://localhost:5000")
    print("=" * 70)
    app.run(debug=True, host='0.0.0.0', port=5000)