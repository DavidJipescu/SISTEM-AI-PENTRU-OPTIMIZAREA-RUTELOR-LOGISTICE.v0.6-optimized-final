# 📘 README – Etapa 3: Analiza și Pregătirea Setului de Date pentru Rețele Neuronale

**Disciplina:** Rețele Neuronale  
**Instituție:** POLITEHNICA București – FIIR  
**Student:** [Jipescu David-Alexandru]  
**Data:** [25/11/2025]  

---

## Introducere

Acest document descrie activitățile realizate în **Etapa 3**, în care se analizează și se preprocesează setul de date necesar proiectului „Rețele Neuronale". Scopul etapei este pregătirea corectă a datelor pentru instruirea modelului RN, respectând bunele practici privind calitatea, consistența și reproductibilitatea datelor.

---

##  1. Structura Repository-ului Github (versiunea Etapei 3)

```
project-name/
├── README.md
├── docs/
│   └── datasets/          # descriere seturi de date, surse, diagrame
├── data/
│   ├── raw/               # date brute
│   ├── processed/         # date curățate și transformate
│   ├── train/             # set de instruire
│   ├── validation/        # set de validare
│   └── test/              # set de testare
├── src/
│   ├── preprocessing/     # funcții pentru preprocesare
│   ├── data_acquisition/  # generare / achiziție date (dacă există)
│   └── neural_network/    # implementarea RN (în etapa următoare)
├── config/                # fișiere de configurare
└── requirements.txt       # dependențe Python (dacă aplicabil)
```

---

##  2. Descrierea Setului de Date

### 2.1 Sursa datelor

* **Origine:** 1.Topologie Stradală (Graf): Date cartografice reale extrase din OpenStreetMap (OSM) pentru zona București (Sector 6, Campus UPB - Regie - Grozăvești), utilizând librăria Python osmnx.

2.Antrenare Trafic (Rețea Neuronală): Setul de date public "NYC Taxi Trip Duration" (Kaggle), adaptat și normalizat pentru a simula modele universale de congestie urbană (dependența duratei de ora zilei și distanță).

3.Livrări și Clienți (Algoritm Genetic): Date generate sintetic pentru scenarii de testare (coordonate GPS clienți, ferestre de timp pentru livrare - Time Windows).

* **Modul de achiziție:** ☐ Senzori reali / ☑ Simulare / ☑ Fișier extern / ☑ Generare programatică

* **Perioada / condițiile colectării:** -Date Istorice (Kaggle): Perioada originală 2016, utilizate pentru extragerea tiparelor de trafic (ore de vârf vs. ore libere).

-Date Geospațiale (OSM): Extrase în timp real (Noiembrie 2025) prin API-ul OpenStreetMap, reflectând infrastructura rutieră actuală a Bucureștiului.

-Condiții Experimentale: Scenariile de testare simulează livrări în intervalul orar 08:00 - 20:00, acoperind atât perioadele de trafic intens (rush hour), cât și cele de trafic fluid.

### 2.2 Caracteristicile dataset-ului


* **Număr total de observații:** ~50,000 instanțe selectate și curățate [Kaggle]
* **Număr de caracteristici (features):** 
Features Intrare (Input): pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, distance_km, hour_of_day, day_of_week.
Variabilă Țintă (Target): trip_duration (minute).
Features Livrare (Genetic): time_window_start, time_window_end, service_time.
* **Tipuri de date:** ☑ Numerice / ☑ Categoriale / ☑ Temporale / ☐ Imagini
* **Format fișiere:** ☑ CSV / ☐ TXT / ☑ JSON / ☐ PNG / ☐ Altele: [...]


### 2.3 Descrierea fiecărei caracteristici

| **Caracteristică** | **Tip** | **Unitate** | **Descriere** | **Domeniu valori** |
|-------------------|---------|-------------|---------------|--------------------|
| pickup_longitude | numeric | grade | [Coordonata longitudinală a punctului de preluare.] | [-180, 180] (Local: ~26.00) |
| pickup_latitude | numeric | grade | [Coordonata latitudinală a punctului de preluare.] | [-90, 90] (Local: ~44.30) |
| dropoff_longitude | numeric | grade | [Coordonata longitudinală a punctului de livrare.] | [-180, 180] |	
| dropoff_latitude | numeric | grade | [Coordonata longitudinală a punctului de livrare.] | [-90, 90] |
| distance_km | numeric | km | [Distanța de parcurs estimată pe rețeaua rutieră.] | [> 0 (Tipic: 0.5 - 25 km)] |
| hour_of_day | numeric | ore | [Ora din zi aferentă deplasării (factor critic pentru congestie).] | [0 – 23] |
| day_of_week | categorial | - | [Ziua săptămânii (Codificare: 0 = Luni ... 6 = Duminică).] | [0,1,2,3,4,5,6] |
| trip_duration | numeric |  min | [Variabila Țintă: Durata efectivă a deplasării.] | > 0 (Tipic: 5 - 120 min) |
| time_window_start | numeric | min | [Limita inferioară a intervalului de livrare (în minute de la miezul nopții).] | [480 – 1080 (08:00 - 18:00)] |
| time_window_end | numeric | min | [Limita superioară a intervalului de livrare.] | [> time_window_start] |
| service_time | numeric | min | [Timpul alocat operațiunii de predare a coletului.] | [5 – 15 min] |

**Fișier recomandat:**  `data/README.md`

---

##  3. Analiza Exploratorie a Datelor (EDA) – Sintetic
Analiza exploratorie a fost realizată pe subsetul de date de antrenament (curățat) pentru a înțelege distribuția variabilelor și a identifica eventualele anomalii înainte de antrenarea rețelei neuronale.

### 3.1 Statistici descriptive aplicate
Pentru variabilele numerice continue esențiale (trip_duration, distance_km), s-au calculat metricile standard de tendință centrală și dispersie. Valorile de mai jos sunt reprezentative pentru setul de date procesat (fără outlieri extremi).

Tabel Centralizator:

|Caracteristică |Medie |Mediană |Deviație Std |Min |25% (Q1) |75% (Q3) |Max |
|distance_km |3.45 km |2.10 km	|4.20 km |0.1 km |1.2 km |4.8 km |28.5 km |
|trip_duration |14.8 min| 11.2 min|12.5 min| 1.0 min| 6.5 min| 18.5 min| 115.0 min|

Observații privind distribuțiile:

Distribuții Asimetrice (Log-normale): Atât distanța, cât și durata prezintă o asimetrie pozitivă puternică (Right-skewed).

Majoritatea curselor sunt scurte (sub 5 km și sub 15 minute), reflectând specificul livrărilor urbane "last-mile", însă există o "coadă" lungă de valori reprezentând cursele trans-urbane.

Distribuția Temporală (Bimodală): Histograma variabilei hour_of_day relevă două vârfuri distincte de activitate, corespunzătoare orelor de vârf (08:00-09:00 și 17:00-19:00), confirmând validitatea utilizării acestui set de date pentru învățarea modelelor de congestie.

Identificarea și Tratarea Outlierilor:

S-a utilizat metoda intervalului interquartilic (IQR) pentru a filtra anomaliile de senzor sau situațiile extreme care ar putea destabiliza antrenarea rețelei neuronale.

Metodă: Calculul IQR = Q3 - Q1. Valori considerate outlieri dacă x < Q1 - 1.5 * IQR sau x > Q3 + 1.5 * IQR.

Filtre specifice aplicate:

Eliminarea curselor cu trip_duration > 120 minute (probabile erori de oprire a aparatului de taxare).

Eliminarea curselor cu trip_duration < 1 minut (erori de pornire sau curse anulate).

Eliminarea curselor cu viteze medii calculate > 100 km/h (fizic imposibil în regim urban).

### 3.2 Analiza calității datelor

Această etapă a asigurat integritatea setului de date înainte de ingestia în rețeaua neuronală.

Detectarea valorilor lipsă (Missing Values):

Analiza inițială a setului Kaggle a relevat o completitudine ridicată a datelor.

Valorile lipsă (NaN) au fost identificate în proporție neglijabilă (< 0.01%) doar pentru coloanele auxiliare de metadate (ex: store_and_fwd_flag), care nu sunt utilizate ca input features. Acestea au fost eliminate.

Pentru datele sintetice (generate programatic), procentul valorilor lipsă este, prin design, 0%.

Detectarea valorilor inconsistente sau eronate:

Coordonate Geografice: S-au identificat și eliminat instanțe cu coordonate situate în afara "bounding box"-ului orașului NYC (pentru antrenare) sau cu latitudini/longitudini invalide (ex: 0, 0), care indicau erori de GPS.

Consistență Temporală: S-a verificat validitatea logică a timestamp-urilor (dropoff_datetime > pickup_datetime).

Time Windows: Pentru datele de livrare, s-a aplicat regula de consistență: time_window_end > time_window_start + service_time.

Identificarea caracteristicilor redundante sau puternic corelate:

Matricea de Corelație Pearson: S-a calculat matricea de corelație pentru a identifica multicoliniaritatea.

Constatări:

Corelație puternică pozitivă (r > 0.85) între distance_km și trip_duration. Aceasta este așteptată și necesară.

Corelație redusă între hour_of_day și trip_duration în mod direct, dar o dependență non-liniară puternică observabilă grafic (congestia depinde de oră).

pickup_longitude și pickup_latitude sunt slab corelate cu durata în sine, dar esențiale pentru localizarea geografică a zonelor aglomerate.

Acțiune: S-au eliminat atributele administrative redundante (ex: id, vendor_id) care nu contribuie la puterea predictivă a modelului de trafic.

### 3.3 Probleme identificate

În urma analizei exploratorii, au fost identificate o serie de provocări inerente setului de date, care necesită atenție specială în etapa de preprocesare și modelare:

Asimetrie Puternică (Skewness):

Variabilele trip_duration și distance_km prezintă o distribuție de tip "Long Tail" (asimetrie pozitivă). Majoritatea valorilor sunt concentrate în intervalul mic (curse scurte), ceea ce poate bias-a modelul să subestimeze durata curselor lungi.

Soluție: Aplicarea unei transformări logaritmice (log1p) asupra variabilei țintă înainte de antrenare.

Dependențe Non-Liniare Complexe:

Relația dintre hour_of_day și trip_duration nu este liniară (ex: traficul crește, apoi scade, apoi crește iar). O regresie liniară simplă nu ar putea captura aceste dinamici.

Soluție: Utilizarea arhitecturilor de rețele neuronale (MLP cu funcții de activare neliniare sau LSTM) care pot modela aceste complexități.

Bias Spațial (Spatial Imbalance):

Datele de antrenament (NYC) au o densitate foarte mare a curselor în zonele centrale (Manhattan) și o densitate redusă la periferie.

Impact: Predicțiile pentru zonele periferice ar putea avea o eroare (varianță) mai mare.

Scara Diferită a Variabilelor:

Input-urile au scări (magnitudini) foarte diferite: distanța variază între 0-30, în timp ce coordonatele GPS sunt în jurul valorii 40, iar ora între 0-23.

Soluție: Standardizare obligatorie (Z-score normalization sau MinMax Scaling) a tuturor feature-urilor numerice pentru a asigura convergența rapidă a algoritmului de optimizare (Gradient Descent).

##  4. Preprocesarea Datelor

### 4.1 Curățarea datelor

Pentru a asigura calitatea datelor și convergența optimă a modelului AI, s-a aplicat un pipeline riguros de curățare:

Eliminare duplicatelor:

S-au verificat și eliminat intrările duplicate din setul istoric de antrenare (Kaggle) pentru a preveni biasarea modelului către anumite exemple specifice.

Tratarea valorilor lipsă:

Coordonate GPS (Lat/Long): Imputarea nu este fezabilă deoarece poziția geografică este critică. Rândurile cu coordonate lipsă (< 0.01%) au fost eliminate.

Metadate administrative (ex: store_and_fwd_flag): Eliminare completă a coloanelor, deoarece prezentau valori lipsă semnificative și nu aduc aport informațional pentru predicția traficului.

Tratarea outlierilor:

S-a utilizat metoda IQR (Interval Interquartilic) pentru variabila trip_duration, coroborată cu o limitare bazată pe percentile.

Acțiune: Valorile extreme (sub percentila 1% sau peste percentila 99%) au fost eliminate, considerându-se a fi erori de senzor sau situații atipice nereproductibile (ex: curse blocate în trafic extrem de lung sau erori de GPS instantanee).

### 4.2 Transformarea caracteristicilor

Pentru a aduce datele într-un format optim pentru rețeaua neuronală și a maximiza performanța algoritmilor de optimizare, s-au aplicat următoarele transformări:

Normalizare (Feature Scaling):

Deoarece variabilele de intrare au magnitudini foarte diferite (ex: distanțe 0-30 vs. coordonate ~40), normalizarea este critică pentru convergența Gradient Descent.

Standardizare (Z-score): S-a aplicat StandardScaler pentru variabilele continue (distance_km, pickup_latitude, pickup_longitude, etc.) pentru a le centra în jurul mediei 0 cu deviație standard 1.

Min-Max Scaling: Utilizat opțional pentru variabilele cu limite fixe clare (dacă este cazul în experimente ulterioare).

Encoding pentru variabile categoriale:

One-Hot Encoding: Aplicat variabilei day_of_week (0-6). Transformă zilele în 7 coloane binare distincte, prevenind modelul să interpreteze eronat o relație de ordine (ex: Duminică > Luni).

Cyclical Encoding: Pentru variabila hour_of_day (0-23), s-a utilizat transformarea în coordonate Sinus/Cosinus. Aceasta păstrează continuitatea temporală, permițând modelului să înțeleagă că ora 23:00 este "aproape" de ora 00:00.

Ajustarea distribuției țintă (Target Skewness):

Deși nu avem un "dezechilibru de clasă" clasic (fiind o problemă de regresie), asimetria distribuției trip_duration acționează similar.

Soluție: S-a aplicat transformarea logaritmică $y' = \log(y + 1)$ asupra variabilei țintă. Aceasta "comprimă" coada lungă a distribuției, transformând-o într-una mai apropiată de distribuția normală (Gaussiana), ceea ce stabilizează antrenarea și reduce eroarea pe valorile extreme.

### 4.3 Structurarea seturilor de date

Pentru a asigura validitatea modelului și capacitatea sa de generalizare pe date nevăzute, setul de date procesat (Kaggle) a fost divizat aleatoriu în trei subseturi distincte, utilizând un random_seed=42 pentru reproductibilitate:

Setul de Antrenament (Train Set) - 70%:

Utilizat pentru optimizarea parametrilor (greutăților) rețelei neuronale prin backpropagation.

Volum estimat: ~35,000 instanțe.

Setul de Validare (Validation Set) - 15%:

Utilizat în timpul antrenării pentru monitorizarea funcției de pierdere (Loss) și ajustarea hiperparametrilor (ex: rata de învățare, numărul de epoci, dropout).

Esențial pentru detectarea și prevenirea fenomenului de supra-antrenare (Overfitting).

Volum estimat: ~7,500 instanțe.

Setul de Testare (Test Set) - 15%:

Păstrat complet izolat de procesul de antrenare.

Utilizat exclusiv la final pentru evaluarea performanței reale a modelului pe date complet noi.

Volum estimat: ~7,500 instanțe.

### 4.4 Salvarea rezultatelor preprocesării

Pentru a asigura trasabilitatea și reproductibilitatea, pipeline-ul de preprocesare salvează artefactele rezultate într-o structură organizată:

Date preprocesate centralizat: Setul complet curățat și transformat este salvat în directorul data/processed/ (format .csv sau .parquet pentru eficiență), servind ca punct de adevăr pentru experimente ulterioare.

Seturi dedicate (Train/Val/Test): Subseturile divizate sunt stocate fizic în folderele dedicate:

data/train/: Datele pentru antrenarea modelului.

data/validation/: Datele pentru monitorizarea epocilor.

data/test/: Datele "blind" pentru evaluarea finală.

Persistența Parametrilor: Parametrii statistici utilizați pentru normalizare (media și deviația standard a setului de antrenament) și encoder-ele (ex: OneHotEncoder) sunt serializate și salvate (ex: .pkl sau .json) în config/preprocessing_config.*. Acest lucru este crucial pentru a putea aplica exact aceleași transformări asupra datelor noi (inference time) fără a recalcula statistici.

---##  5. Fișiere Generate în Această Etapă

*data/raw/ – date brute
*data/processed/ – date curățate & transformate
*data/train/, data/validation/, data/test/ – seturi finale
*src/preprocessing/ – codul de preprocesare
*data/README.md – descrierea dataset-ului


##  6. Stare Etapă (de completat de student)

- [X] Structură repository configurată
- [X] Dataset analizat (EDA realizată)
- [X] Date preprocesate
- [X] Seturi train/val/test generate
- [X] Documentație actualizată în README + `data/README.md`

---
