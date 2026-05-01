def get_aqi_insight(value):
    # Mimicking an AI Classifier for Health Risks
    if value < 100:
        return {"status": "Good", "color": "#28a745", "advice": "Air is clean. Fresh environment."}
    elif value < 300:
        return {"status": "Moderate", "color": "#ffc107", "advice": "Acceptable. Sensitive people should stay alert."}
    elif value < 500:
        return {"status": "Poor", "color": "#fd7e14", "advice": "High pollution. Close windows, use purifiers."}
    else:
        return {"status": "Hazardous", "color": "#dc3545", "advice": "Danger! Wear N95 masks and avoid outdoors."}