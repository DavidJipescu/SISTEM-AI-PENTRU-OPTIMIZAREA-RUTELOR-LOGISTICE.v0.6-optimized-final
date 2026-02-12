import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import os

DATA_PATH = 'data/processed/train_data.csv'
MODEL_SAVE_PATH = 'config/best_model.keras'
PLOT_PATH = 'docs/training_history.png'

def build_model(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        LSTM(32, activation='relu', return_sequences=False),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def run_training():
    print(">>> [Training] Încărcare date...")
    if not os.path.exists(DATA_PATH):
        print(f" Lipsă date: {DATA_PATH}. Rulează clean_data.py!")
        return

    df = pd.read_csv(DATA_PATH)
    X = df[['distance_km', 'hour_of_day']].values
    y = df['trip_duration'].values
    X = X.reshape((X.shape[0], 1, X.shape[1]))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = build_model(input_shape=(1, 2))
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        ModelCheckpoint(MODEL_SAVE_PATH, monitor='val_loss', save_best_only=True)
    ]

    print(">>> [Training] Start Antrenare...")
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        verbose=1
    )

    os.makedirs('docs', exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.title('Training History')
    plt.savefig(PLOT_PATH)
    print(f" Grafic salvat în: {PLOT_PATH}")
    print(f" Model antrenat salvat în: {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    run_training()
