# 📘 README – Etapa 4: Arhitectura Completă a Aplicației SIA

**Student:** [Numele Tău]
**Data:** 12.12.2025

## 1. Livrabile Obligatorii

| **Nevoie reală concretă** | **Cum o rezolvă SIA-ul vostru** | **Modul software responsabil** |
|---------------------------|--------------------------------|--------------------------------|
| **Estimarea întârzierilor în traficul urban aglomerat** | Predicție dinamică a duratei de deplasare în funcție de oră și zi → **Eroare ETA < 5 minute** | `src/neural_network` (Model LSTM) |
| **Planificarea livrărilor multiple cu ferestre de timp fixe** | Reordonarea optimă a secvenței de vizitare a clienților → **Reducere 15% km parcurși** | `src/optimization` (GeneticOptimizer) |
| **Vizualizarea și confirmarea rutei în timp real** | Interfață API pentru transmiterea rutei calculate către șofer → **Timp răspuns < 2 secunde** | `app.py` (Web Service / Flask API) |

## 2. Contribuția Voastră Originală la Setul de Date

**Total observații finale:** 25,000
**Observații originale:** 10,000 (40%)

**Tipul contribuției:**
[X] Date sintetice prin metode avansate

**Descriere:**
Am generat un set de date sintetic complex pentru problema VRPTW mapat pe topologia reală a Bucureștiului. Am utilizat librăria `osmnx` pentru a extrage noduri valide din Sectorul 6 și am proiectat scenariile de livrare pe acestea.

**Locația codului:** `src/data_acquisition/generate_synthetic.py`
**Locația datelor:** `data/raw/synthetic_traffic_data.csv`
