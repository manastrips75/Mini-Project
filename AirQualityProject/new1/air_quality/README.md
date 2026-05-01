# 🌍 AI Air Quality Intelligence System

A real-time air quality monitoring system that combines **Python Flask**, **Java DSA**, and **AI Intelligence** for sensor data processing.

## 🏗️ System Architecture

```
Sensor Reading (MQ-135)
        ↓
  Flask App (Python)
        ↓
  Java DataProcessor (Circular Queue DSA)
        ↓
  AI Intelligence Report
        ↓
  Real-time Dashboard
```

## 📁 Project Structure

```
AirQualityProject/
├── app.py                          # Main Flask application with Java bridge
├── DataProcessor.java              # Java class with circular queue logic
├── aqi_intelligence.py             # AI insights helper (legacy)
├── templates/
│   └── index.html                  # Interactive real-time dashboard
├── static/
│   └── style.css                   # Modern glassmorphism styling
└── README.md                       # This file
```

## 🔧 Requirements

- **Python 3.7+**
- **Flask** - `pip install flask`
- **Java Development Kit (JDK)** - For compiling and running Java code
  - Download from: https://www.oracle.com/java/technologies/downloads/
  - Add `javac` and `java` to your PATH

## 🚀 Setup Instructions

### 1. Install Python Dependencies

```bash
pip install flask
```

### 2. Verify Java Installation

```bash
java -version
javac -version
```

Both should show installed versions. If not, install JDK.

### 3. Run the Application

```bash
python app.py
```

You should see:

```
============================================================
🌍 AI Air Quality Monitoring System
============================================================
📊 Sensor → Python (Flask) → Java (DSA) → Dashboard
🔗 Access: http://localhost:5000
============================================================
```

### 4. Access the Dashboard

Open your browser and go to: **http://localhost:5000**

## 📊 How It Works

### 1. Sensor Reading (Simulated)
- Random PPM values between 50-600 are generated
- Simulates real MQ-135 air quality sensor readings

### 2. Java Processing (DSA - Data Structure & Algorithm)
- **Circular Queue** with window size = 5
- Computes **moving average** of recent readings
- Returns smoothed value: `raw_value * 0.92`

### 3. AI Intelligence
- **Healthy** (< 150 PPM): Green indicator
- **Warning** (150-350 PPM): Yellow indicator  
- **Danger** (> 350 PPM): Red indicator

### 4. Real-time Dashboard
- Live updating chart with dual datasets (raw + filtered)
- Status card with AI recommendations
- System architecture visualization

## 📈 Real-time Features

- **Auto-compile**: Java class automatically compiled on startup
- **Live Updates**: Dashboard refreshes every 2 seconds
- **Dual Datasets**: Compare raw vs. filtered readings
- **Color Coding**: Dynamic colors based on air quality
- **Performance**: Only last 20 data points kept in memory

## 🔌 API Endpoints

### GET `/`
Returns the interactive dashboard (HTML page)

### GET `/sensor_data`
Returns JSON with current sensor data:
```json
{
  "raw": 245,
  "filtered": 225.4,
  "value": 225.4,
  "status": "Warning",
  "color": "#f1c40f",
  "advice": "Moderate pollution. Use an air purifier."
}
```

## 🐛 Troubleshooting

### Java Compilation Error
```
[ERROR] Compilation failed
```
**Solution**: Install JDK and ensure `javac` is in your PATH
- Windows: Add JDK bin folder to System PATH
- Linux/Mac: `export PATH=$PATH:/path/to/jdk/bin`

### Port Already in Use
```
Address already in use
```
**Solution**: Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 instead
```

### No Sensor Data Appearing
1. Check browser console for errors (F12)
2. Check Flask terminal for Java execution errors
3. Verify Java files are in the same directory as `app.py`

## 📚 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | Flask (Python) | HTTP server & API |
| Processing | Java | Circular Queue DSA |
| Frontend | HTML5 + Chart.js | Real-time visualization |
| Styling | CSS3 (Glassmorphism) | Modern UI |

## 🎨 Features

✅ Real-time sensor data streaming  
✅ Python-Java interprocess communication  
✅ Circular queue data smoothing algorithm  
✅ AI-based air quality classification  
✅ Beautiful glassmorphism UI  
✅ Responsive design (mobile-friendly)  
✅ Auto-compilation on startup  
✅ Live dual-dataset charting  

## 📝 License

Educational Project - Free to use and modify

## 👨‍💻 Author

Air Quality Intelligence System v1.0

---

**Note**: This is a demonstration project. For production use with real sensors, implement:
- Database persistence
- Sensor calibration
- Error handling & logging
- Authentication & authorization
- Data backup systems
