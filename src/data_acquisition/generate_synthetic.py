import pandas as pd
import numpy as np
import json
import os
import random

# Configurare Geografică (București)
CENTER_LAT = 44.435
CENTER_LON = 26.102
RADIUS_KM = 15

def generate_gps_point(center_lat, center_lon, radius_km):
    r = radius_km / 111.0
    u, v = random.random(), random.random()
    w = r * np.sqrt(u)
    t = 2 * np.pi * v
    x = w * np.cos(t)
    y = w * np.sin(t)
    return x + center_lat, y + center_lon / np.cos(np.radians(center_lat))

def simulate_traffic_cost(dist_km, hour):
    # Model matematic pentru congestie (Funcție neliniară)
    base_speed = 35.0 # km/h
    # Factor congestie: Vârfuri la 8-9 și 17-18
    congestion = 1.0 + 1.5 * np.exp(-((hour - 8.5)**2)/2) + 1.8 * np.exp(-((hour - 17.5)**2)/2)
    real_speed = base_speed / congestion
    duration_min = (dist_km / real_speed) * 60
    # Adăugare zgomot stochastic
    noise = np.random.normal(0, duration_min * 0.15) 
    return max(2.0, duration_min + noise)

def run():
    print(">>> [DataGen] 1. Generare Date Trafic pentru Antrenare RN...")
    data = []
    for _ in range(5000):
        lat1, lon1 = generate_gps_point(CENTER_LAT, CENTER_LON, RADIUS_KM)
        lat2, lon2 = generate_gps_point(CENTER_LAT, CENTER_LON, RADIUS_KM)
        dist = np.sqrt((lat1-lat2)**2 + (lon1-lon2)**2) * 111.0
        h = random.randint(6, 22)
        data.append({
            'distance_km': round(dist, 2),
            'hour_of_day': h,
            'trip_duration': round(simulate_traffic_cost(dist, h), 2)
        })
    os.makedirs('data/raw', exist_ok=True)
    pd.DataFrame(data).to_csv('data/raw/synthetic_traffic_data.csv', index=False)
    print("   ✅ CSV generat: data/raw/synthetic_traffic_data.csv")

    print(">>> [DataGen] 2. Generare Scenarii Livrare (Input pt Algoritm Genetic)...")
    scenarios = []
    for i in range(5):
        stops = []
        stops.append({"id": "depot", "lat": CENTER_LAT, "lon": CENTER_LON, "type": "depot"})
        for k in range(10):
            lat, lon = generate_gps_point(CENTER_LAT, CENTER_LON, RADIUS_KM)
            stops.append({"id": f"client_{k}", "lat": round(lat, 5), "lon": round(lon, 5), "type": "customer"})
        scenarios.append({"scenario_id": i, "locations": stops})
    with open('data/raw/delivery_scenarios.json', 'w') as f:
        json.dump(scenarios, f, indent=2)
    print("   ✅ JSON generat: data/raw/delivery_scenarios.json")

if __name__ == "__main__":
    run()
