import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
import numpy as np
import os
import joblib

class TrafficModel:
    def __init__(self, scaler_path='config/scaler_params.pkl', model_path='config/best_model.keras'):
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
            print("[AI] Scaler încărcat corect.")
        else:
            self.scaler = None
            print("[AI] ATENȚIE: Scaler lipsă. Predicțiile vor fi ne-normalizate!")

        if os.path.exists(model_path):
            print(f"[AI] ✅ S-a găsit model antrenat: {model_path}. Încărcare...")
            self.model = load_model(model_path)
        else:
            print("[AI] ⚠️ Nu s-a găsit model antrenat. Se folosește arhitectura 'crudă' (neantrenată).")
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
        if self.scaler:
            input_data = self.scaler.transform([[distance_km, hour]])
        else:
            input_data = [[distance_km, hour]]
        input_tensor = np.array([input_data])
        prediction = self.model.predict(input_tensor, verbose=0)
        return max(1.0, float(prediction[0][0]))
