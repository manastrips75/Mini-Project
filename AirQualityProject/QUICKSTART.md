# 🚀 Quick Start Guide

## Step-by-Step Setup (2 minutes)

### Step 1: Verify Java Installation ✅
```powershell
java -version
javac -version
```
Both commands should show version info. If not, download JDK from: https://www.oracle.com/java/technologies/downloads/

### Step 2: Install Flask ✅
```powershell
pip install -r requirements.txt
# Or manually:
pip install flask
```

### Step 3: Run the Application ✅
```powershell
python app.py
```

Expected output:
```
============================================================
🌍 AI Air Quality Monitoring System
============================================================
📊 Sensor → Python (Flask) → Java (DSA) → Dashboard
🔗 Access: http://localhost:5000
============================================================
 * Running on http://localhost:5000
```

### Step 4: Open Dashboard 📊
Open browser → http://localhost:5000

---

## 📂 Project Files

### ✅ Created Files
- **DataProcessor.java** - Java circular queue implementation
- **README.md** - Complete project documentation
- **requirements.txt** - Python dependencies
- **QUICKSTART.md** - This file

### ✅ Updated Files
- **app.py** - Added Java compilation & bridge
- **templates/index.html** - Complete interactive dashboard
- **static/style.css** - Modern UI styling

---

## 🔄 Data Flow

```
┌─────────────┐
│   Sensors   │  Random readings (50-600 PPM)
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  Flask (Python)      │  → app.route('/sensor_data')
│  - Generates random  │
│  - Calls Java        │
└──────┬───────────────┘
       │
       ▼ subprocess call
┌──────────────────────┐
│  Java DataProcessor  │  → Circular Queue (size=5)
│  - Receives raw data │  → Computes moving average
│  - Returns filtered  │  → Returns smoothed value
└──────┬───────────────┘
       │
       ▼ JSON Response
┌──────────────────────┐
│  AI Intelligence     │  → Decision Tree
│  - Analyzes value    │  → Health status
│  - Color coded       │  → Advice message
└──────┬───────────────┘
       │
       ▼ JavaScript/Chart.js
┌──────────────────────┐
│  Web Dashboard       │  → Real-time updates
│  - Status card       │  → Live chart
│  - Architecture info │  → System stats
└──────────────────────┘
```

---

## 🧪 Testing

### Test 1: Check Java Compilation
```powershell
# Python will automatically compile DataProcessor.java
# Watch the terminal for:
# [INFO] Compiling DataProcessor.java...
# [SUCCESS] DataProcessor compiled successfully!
```

### Test 2: Access Dashboard
- Browser: http://localhost:5000
- Should show dynamic chart with color-changing status

### Test 3: Console Logs
- Open browser DevTools (F12)
- Go to Console tab
- You should see logs like:
  ```
  [1] Raw: 245 → Filtered: 225.4 | Status: Warning
  [2] Raw: 312 → Filtered: 286.8 | Status: Warning
  ```

### Test 4: API Endpoint
- Browser: http://localhost:5000/sensor_data
- Should return JSON like:
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

---

## 🎯 What Each Component Does

| Component | Role | Technology |
|-----------|------|-----------|
| **Sensors** | Generate random air quality readings | Simulation |
| **Flask** | HTTP server, receives requests, calls Java | Python |
| **Java** | Processes sensor data using circular queue | Circular Queue DSA |
| **AI** | Classifies air quality level | Decision Tree |
| **Dashboard** | Visualizes real-time data | Chart.js + HTML5 |

---

## 🛑 Stop the Application

Press `Ctrl + C` in the terminal running Flask

---

## ❌ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `java: command not found` | Install JDK, add to PATH |
| `javac: command not found` | Install JDK, add bin folder to PATH |
| `Address already in use` | Change port in app.py line 89 |
| `No chart appearing` | Check browser console, reload page |
| `Java compilation error` | Ensure DataProcessor.java is in same folder as app.py |
| `ModuleNotFoundError: flask` | Run `pip install flask` |

---

## 📝 Next Steps

After successful setup, you can:

1. **Real Sensors**: Replace `random.randint()` with actual sensor data
2. **Database**: Add SQLAlchemy to store historical data
3. **Alerts**: Email/SMS notifications for dangerous levels
4. **Mobile App**: Package as mobile application
5. **Cloud Deployment**: Deploy to AWS/Azure/Heroku

---

## 📞 Support

All files include comments explaining the code. Check:
- **app.py** - Python implementation
- **DataProcessor.java** - Java implementation  
- **index.html** - Frontend logic
- **style.css** - UI styling

---

**Status**: ✅ Ready to run!

Run `python app.py` and visit http://localhost:5000 🌍
