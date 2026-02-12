### 4.1 Tabel Sumar Rezultate Finale

Acest tabel sintetizează evoluția performanței sistemului de la faza de schelet (Etapa 4) până la optimizarea finală (Etapa 6).

*Note: Metricile sunt adaptate pentru problema de regresie (predicție durată livrare).*

| Metrică                             | Etapa 4 (Schelet) | Etapa 5 (Baseline) | Etapa 6 (Final) | Target Industrial     | Status     |
| :---------------------------------- | :---------------- | :----------------- | :-------------- | :-------------------- | :--------- |
| **MAE (Eroare Medie Absolută)** | ~15.0 min (Random)| 2.45 min           | **1.45 min** | ≤ 2.0 min             | ✅ Atins   |
| **Accuracy (în marja de 3 min)** | ~5%               | 72%                | **92%** | ≥ 90%                 | ✅ Atins   |
| **RMSE (Penalizare Erori Mari)** | ~20.0 min         | 3.10 min           | **2.15 min** | ≤ 2.5 min             | ✅ Atins   |
| **Rata Erori Critice (>5 min)** | ~95%              | 12%                | **1.4%** | ≤ 3%                  | ✅ Atins   |
| **Latență Inferență (per rută)** | 50ms              | 48ms               | **35ms** | ≤ 50ms                | ✅ OK      |
| **Throughput (Cereri/sec)** | N/A               | 20 req/s           | **45 req/s** | ≥ 30 req/s            | ✅ OK      |

**Concluzie:**
Sistemul **PyRoute-NeuroGen** a atins și depășit obiectivele industriale stabilite pentru Etapa 6. Optimizarea arhitecturii LSTM și introducerea datelor sintetice augmentate au redus rata erorilor critice sub pragul de 3%, făcând soluția viabilă pentru implementare în producție.
