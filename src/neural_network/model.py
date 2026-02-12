import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
import numpy as np
import pandas as pd  
import os
import joblib

class TrafficModel:
    def __init__(self, scaler_path='config/scaler_params.pkl', model_path='config/best_model.keras'):
        #Incarcam scalerul pentru predictii
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
        else:
            self.scaler = None
            print("[AI] ATENȚIE: Scaler lipsă. Predicțiile vor fi ne-normalizate!")

        # Incarcam modelul dacă exista, altfel facem unul nou
        if os.path.exists(model_path):
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
        # Pregătire input
        if self.scaler:
            # Reconstruim un DataFrame cu numele coloanelor, exact ca la antrenare
            input_df = pd.DataFrame([[distance_km, hour]], columns=['distance_km', 'hour_of_day'])
            
            input_data = self.scaler.transform(input_df)
        else:
            input_data = [[distance_km, hour]]
            
        # Reshape pentru LSTM: (batch, timesteps, features) -> (1, 1, 2)
        input_tensor = np.array([input_data])
        
        # Predictie (verbose=0 ascunde logurile inutile)
        prediction = self.model.predict(input_tensor, verbose=0)
        
        # Output (asiguram valoare pozitiva)
        return max(1.0, float(prediction[0][0]))
