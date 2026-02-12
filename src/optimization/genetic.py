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
            print(f"[Genetic] 🗺️  Încărcare hartă București din cache (poate dura câteva secunde)...")
            self.G = ox.load_graphml(self.graph_path)
            self.state = "IDLE"
        else:
            print("[Genetic]  Harta nu există local. Se descarcă și se procesează (aprox. 1 min)...")
            try:
                # Mărim raza la 20km pentru a prinde și periferia (Ilfov)
                center_point = (44.435, 26.102) 
                self.G = ox.graph_from_point(center_point, dist=20000, network_type='drive')
                
                # Adăugăm viteze și timpi pentru calcule precise
                self.G = ox.add_edge_speeds(self.G)
                self.G = ox.add_edge_travel_times(self.G)
                
                os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
                ox.save_graphml(self.G, self.graph_path)
                
                self.state = "IDLE"
                print("[Genetic] Harta a fost salvată cu succes!")
            except Exception as e:
                print(f"[Genetic] Eroare critică la descărcarea hărții: {e}")
                self.state = "ERROR"

    def _get_network_distance(self, loc1, loc2):
        """Calculează distanța pe rețea între două puncte GPS."""
        if not self.G: return 5.0 # Fallback
        try:
            # Găsim cele mai apropiate noduri de coordonatele GPS
            orig = ox.distance.nearest_nodes(self.G, loc1['lon'], loc1['lat'])
            dest = ox.distance.nearest_nodes(self.G, loc2['lon'], loc2['lat'])
            
            # Calculăm cel mai scurt drum ponderat după lungime
            length_m = nx.shortest_path_length(self.G, orig, dest, weight='length')
            return length_m / 1000.0 # Returnăm km
        except: 
            # Dacă nu există drum (ex: insulă sau eroare graf), returnăm distanță aeriană * 1.5
            dist_air = np.sqrt((loc1['lat']-loc2['lat'])**2 + (loc1['lon']-loc2['lon'])**2) * 111.0
            return dist_air * 1.5

    def _get_detailed_path(self, route_indices, locations):
        """
        OPTIMIZARE VIZUALĂ:
        Extrage nu doar nodurile (intersecțiile), ci și geometria curbată a străzilor.
        Astfel, linia de pe hartă va urmări perfect curbele drumului.
        """
        detailed_path = []
        if not self.G:
            return detailed_path

        try:
            print("    [Genetic] Generare geometrie fină a traseului...")
            
            # Iterăm prin fiecare segment al rutei optime
            for i in range(len(route_indices) - 1):
                idx_curr = route_indices[i]
                idx_next = route_indices[i+1]
                
                loc_curr = locations[idx_curr]
                loc_next = locations[idx_next]
                
                # Găsim nodurile start/stop pentru acest segment
                orig = ox.distance.nearest_nodes(self.G, loc_curr['lon'], loc_curr['lat'])
                dest = ox.distance.nearest_nodes(self.G, loc_next['lon'], loc_next['lat'])
                
                # Găsim calea de noduri
                path_nodes = nx.shortest_path(self.G, orig, dest, weight='length')
                
                # --- OPTIMIZARE: Extragere Geometrie Reală (Curbe) ---
                for u, v in zip(path_nodes[:-1], path_nodes[1:]):
                    # Luăm datele muchiei dintre nodul u și nodul v
                    # (u, v, 0) este cheia pentru multigraph (luăm prima muchie)
                    edge_data = self.G.get_edge_data(u, v)[0]
                    
                    if 'geometry' in edge_data:
                        # Dacă muchia are geometrie detaliată (curbă), o folosim
                        # Geometry este un obiect LineString, extragem coordonatele
                        xx, yy = edge_data['geometry'].coords.xy
                        for x, y in zip(xx, yy):
                            detailed_path.append({'lat': y, 'lon': x})
                    else:
                        # Dacă e linie dreaptă, adăugăm doar coordonatele nodului v
                        lat = self.G.nodes[v]['y']
                        lon = self.G.nodes[v]['x']
                        detailed_path.append({'lat': lat, 'lon': lon})
                    
            return detailed_path
        except Exception as e:
            print(f"[Genetic] Eroare la extragerea geometriei detaliate: {e}")
            return []

    def calculate_confidence(self, distance_km):
        # Confidence Check - penalizează rutele foarte lungi
        if distance_km < 15:
            return 0.95
        elif distance_km < 30:
            return 0.70
        else:
            return 0.40

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
            
            # Confidence Check
            conf = self.calculate_confidence(dist)
            if conf < 0.6:
                return 99999 
            
            # Predicție AI
            duration = self.ai_model.predict_trip_time(dist, int(current_hour))
            total_time += duration
            current_hour += (duration / 60.0)
            if current_hour >= 24: current_hour -= 24
            
        return total_time

    def solve(self, locations, generations=3, pop_size=10):
        print(f">>> [Genetic] START Optimizare ({len(locations)} puncte)...")
        self.state = "PREPROCESS"
        
        # 1. Pre-calculare matrice distanțe (pentru viteză maximă în Genetic)
        n = len(locations)
        dist_matrix = [[0]*n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist_matrix[i][j] = self._get_network_distance(locations[i], locations[j])
        
        indices = list(range(len(locations)))
        depot_idx = 0 
        client_indices = indices[1:]
        
        best_route = indices
        best_fitness = float('inf')

        # 2. Algoritm Genetic
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
            
            # Elitism + Mutație
            new_pop = [best_route]
            for _ in range(pop_size - 1):
                child = best_route[1:].copy()
                random.shuffle(child)
                new_pop.append([depot_idx] + child)
            population = new_pop
            
        self.state = "SEND_RESPONSE"
        
        # 3. Extragere Geometrie Detaliată (pentru UI frumos)
        detailed_geometry = self._get_detailed_path(best_route, locations)
        
        self.state = "IDLE"
        return best_route, best_fitness, detailed_geometry