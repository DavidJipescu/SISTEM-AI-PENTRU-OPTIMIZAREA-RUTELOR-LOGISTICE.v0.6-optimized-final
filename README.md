# SISTEM AI PENTRU OPTIMIZAREA RUTELOR LOGISTICE
Sistem hibrid Neuro-Evolutiv pentru optimizarea rutelor logistice. Utilizează Rețele Neuronale (LSTM) pentru predicția traficului și Algoritmi Genetici (Metaheuristici) pentru rezolvarea problemei VRPTW. Proiect Rețele Neuronale.

>Dicționar de Date și Descrierea Variabilelor

1. Caracteristică

2. Tip

3. Unitate

4. Descriere Tehnică

5. Domeniu de Valori

>pickup_longitude

numeric

grade

Coordonata longitudinală a punctului de preluare.

[-180, 180] (Local: ~26.00)

>pickup_latitude

numeric

grade

Coordonata latitudinală a punctului de preluare.

[-90, 90] (Local: ~44.30)

>dropoff_longitude

numeric

grade

Coordonata longitudinală a punctului de livrare.

[-180, 180]

>dropoff_latitude

numeric

grade

Coordonata latitudinală a punctului de livrare.

[-90, 90]

>distance_km

numeric

km

Distanța de parcurs estimată pe rețeaua rutieră.

 0 (Tipic: 0.5 - 25 km)

>hour_of_day

numeric

ore

Ora din zi aferentă deplasării (factor critic pentru congestie).

0 – 23

>day_of_week

categorial

–

Ziua săptămânii (Codificare: 0 = Luni ... 6 = Duminică).

{0, 1, 2, 3, 4, 5, 6}

>trip_duration

numeric

min

Variabila Țintă: Durata efectivă a deplasării.

 0 (Tipic: 5 - 120 min)

>time_window_start

numeric

min

Limita inferioară a intervalului de livrare (în minute de la miezul nopții).

480 – 1080 (08:00 - 18:00)

>time_window_end

numeric

min

Limita superioară a intervalului de livrare.

> time_window_start

service_time

numeric

min

Timpul alocat operațiunii de predare a coletului.

5 – 15 min