import random
import numpy as np
import osmnx as ox
import networkx as nx
import os
import time

class GeneticOptimizer:
    def __init__(self, ai_model, graph_path='data/processed/bucuresti_drive.graphml'):
        self.state = "IDLE"
        self.ai_model = ai_model
        self.graph_path = graph_path
        self.G = None
        self._load_graph()

    def _load_graph(self):
        self.state = "LOADING_MAP"
        if os.path.exists(self.graph_path):
            print(f"[Genetic]  Încărcare hartă București din cache...")
            self.G = ox.load_graphml(self.graph_path)
            self.state = "IDLE"
        else:
            print("[Genetic]  Harta nu există local. Se descarcă (durează un minut)...")
            try:
                center_point = (44.435, 26.102) 
                self.G = ox.graph_from_point(center_point, dist=15000, network_type='drive')
                self.G = ox.add_edge_speeds(self.G)
                self.G = ox.add_edge_travel_times(self.G)
                os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
                ox.save_graphml(self.G, self.graph_path)
                self.state = "IDLE"
                print("[Genetic] Harta a fost salvată!")
            except Exception as e:
                print(f"[Genetic] Eroare la descărcarea hărții: {e}")
                self.state = "ERROR"

    def _get_network_distance(self, loc1, loc2):
        if not self.G: return 5.0
        try:
            orig = ox.distance.nearest_nodes(self.G, loc1['lon'], loc1['lat'])
            dest = ox.distance.nearest_nodes(self.G, loc2['lon'], loc2['lat'])
            length_m = nx.shortest_path_length(self.G, orig, dest, weight='length')
            return length_m / 1000.0
        except: 
            return 5.0

    def _get_detailed_path(self, route_indices, locations):
        """
        Funcție nouă: Extrage coordonatele exacte (stradă cu stradă)
        pentru a desena polilinia perfect pe străzile din OSM.
        """
        detailed_path = []
        if not self.G:
            return detailed_path

        try:
            for i in range(len(route_indices) - 1):
                idx_curr = route_indices[i]
                idx_next = route_indices[i+1]
                
                loc_curr = locations[idx_curr]
                loc_next = locations[idx_next]
                
                # Gasim nodurile pe hartă
                orig = ox.distance.nearest_nodes(self.G, loc_curr['lon'], loc_curr['lat'])
                dest = ox.distance.nearest_nodes(self.G, loc_next['lon'], loc_next['lat'])
                
                # Calculam calea exacta (lista de noduri)
                path_nodes = nx.shortest_path(self.G, orig, dest, weight='length')
                
                # Transformam nodurile în coordonate Lat/Lon
                for node in path_nodes:
                    lat = self.G.nodes[node]['y']
                    lon = self.G.nodes[node]['x']
                    detailed_path.append({'lat': lat, 'lon': lon})
                    
            return detailed_path
        except Exception as e:
            print(f"[Genetic] Eroare la extragerea geometriei detaliate: {e}")
            # Fallback - dacă dă eroare, întoarcem gol ca să deseneze interfața o linie dreaptă
            return []

    def calculate_confidence(self, distance_km):
        # --- LOGICA NOUA ETAPA 6: Confidence Check ---
        # Modelul nostru a fost antrenat pe distante urbane (0-20km).
        # Daca distanta e mare, increderea in predictia AI scade.
        
        if distance_km < 15:
            return 0.95 # High Confidence
        elif distance_km < 30:
            return 0.70 # Medium Confidence
        else:
            return 0.40 # Low Confidence (Out of distribution)

    def calculate_fitness(self, route_indices, locations, dist_matrix=None):
        total_time = 0
        current_hour = 8.0 
        
        for i in range(len(route_indices) - 1):
            idx_curr = route_indices[i]
            idx_next = route_indices[i+1]
            
            if dist_matrix:
                dist = dist_matrix[idx_curr][idx_next]
            else:
                dist = self._get_network_distance(locations[idx_curr], locations[idx_next])
            
            # --- STARE: CONFIDENCE_CHECK ---
            conf = self.calculate_confidence(dist)
            if conf < 0.6:
                # Low confidence -> Penalizare sau Flagging
                # Simuland astfel respingerea automata ("Request Human Review")
                # print(f" [Low Confidence {conf}] Distanța {dist:.1f}km e prea mare.")
                return 99999 # Fitness foarte prost pentru a elimina gena
            
            # --- STARE: RN_INFERENCE ---
            duration = self.ai_model.predict_trip_time(dist, int(current_hour))
            total_time += duration
            current_hour += (duration / 60.0)
            if current_hour >= 24: current_hour -= 24
            
        return total_time

    def solve(self, locations, generations=3, pop_size=10):
        print(f">>> [Genetic] START Optimizare ({len(locations)} puncte)...")
        self.state = "PREPROCESS"
        
        n = len(locations)
        dist_matrix = [[0]*n for _ in range(n)]
        
        # Precalcularea distantelor pentru viteza
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist_matrix[i][j] = self._get_network_distance(locations[i], locations[j])
        
        indices = list(range(len(locations)))
        depot_idx = 0 
        client_indices = indices[1:]
        
        best_route = indices
        best_fitness = float('inf')

        # Initializare populatie
        population = []
        for _ in range(pop_size):
            route = client_indices.copy()
            random.shuffle(route)
            population.append([depot_idx] + route)

        self.state = "EVOLUTION"
        for gen in range(generations):
            for ind in population:
                fit = self.calculate_fitness(ind, locations, dist_matrix)
                if fit < best_fitness:
                    best_fitness = fit
                    best_route = ind
            
            # Evolutie simplificata: Pastram cel mai bun și randomizăm restul
            new_pop = [best_route]
            for _ in range(pop_size - 1):
                child = best_route[1:].copy()
                random.shuffle(child)
                new_pop.append([depot_idx] + child)
            population = new_pop
            
        self.state = "SEND_RESPONSE"
        
        print("    [Genetic] Extragere geometrie detaliată pentru hartă (OSMnx)...")
        # Acum apelam funcția noua care extrage strazile exact
        detailed_geometry = self._get_detailed_path(best_route, locations)
        
        self.state = "IDLE"
        return best_route, best_fitness, detailed_geometry