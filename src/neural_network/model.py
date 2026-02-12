import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
import numpy as np
import pandas as pd  # <--- Am adaugat pandas
import os
import joblib

class TrafficModel:
    def __init__(self, scaler_path='config/scaler_params.pkl', model_path='config/best_model.keras'):
        # Încercăm să încărcăm scaler-ul pentru a face predicții valide
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
            # print("[AI] Scaler încărcat corect.") 
        else:
            self.scaler = None
            print("[AI] ATENȚIE: Scaler lipsă. Predicțiile vor fi ne-normalizate!")

        # Încărcăm modelul dacă există, altfel facem unul nou
        if os.path.exists(model_path):
            # print(f"[AI] Model încărcat: {model_path}")
            self.model = load_model(model_path)
        else:
            print("[AI] Nu s-a găsit model antrenat. Se folosește arhitectura 'crudă'.")
            self.model = self._build_architecture()

    def _build_architecture(self):
        model = Sequential([
            Input(shape=(1, 2)), 
            LSTM(32, activation='relu', return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model

    def predict_trip_time(self, distance_km, hour=12):
        # 1. Pregătire input
        if self.scaler:
            # --- FIX PENTRU WARNING ---
            # Reconstruim un DataFrame cu numele coloanelor, exact ca la antrenare
            input_df = pd.DataFrame([[distance_km, hour]], columns=['distance_km', 'hour_of_day'])
            
            # Acum transform() nu se mai plânge de lipsa numelor
            input_data = self.scaler.transform(input_df)
        else:
            input_data = [[distance_km, hour]]
            
        # Reshape pentru LSTM: (batch, timesteps, features) -> (1, 1, 2)
        input_tensor = np.array([input_data])
        
        # 2. Predicție (verbose=0 ascunde logurile inutile)
        prediction = self.model.predict(input_tensor, verbose=0)
        
        # 3. Output (asigurăm valoare pozitivă)
        return max(1.0, float(prediction[0][0]))
