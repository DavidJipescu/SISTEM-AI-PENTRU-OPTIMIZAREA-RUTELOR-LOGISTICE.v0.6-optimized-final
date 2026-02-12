import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
import joblib

def run():
    raw_csv = 'data/raw/synthetic_traffic_data.csv'
    proc_csv = 'data/processed/train_data.csv'
    scaler_path = 'config/scaler_params.pkl'
    
    print(">>> [Preprocessing] Începere procesare date...")
    if not os.path.exists(raw_csv):
        print(f"Eroare: Nu găsesc {raw_csv}. Rulează generate_synthetic.py întâi!")
        return

    df = pd.read_csv(raw_csv)
    print(f"   Date încărcate: {len(df)} rânduri.")

    scaler = StandardScaler()
    X = scaler.fit_transform(df[['distance_km', 'hour_of_day']])
    
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    df_proc = pd.DataFrame(X, columns=['distance_km', 'hour_of_day'])
    df_proc['trip_duration'] = df['trip_duration'] 
    
    df_proc.to_csv(proc_csv, index=False)
    joblib.dump(scaler, scaler_path)
    
    print(f"   Date procesate salvate în: {proc_csv}")
    print(f"   Scaler salvat în: {scaler_path}")

if __name__ == "__main__":
    run()
