import random
import numpy as np
import osmnx as ox
import networkx as nx
import os

class GeneticOptimizer:
    def __init__(self, ai_model, graph_path='data/processed/bucuresti_drive.graphml'):
        self.ai_model = ai_model
        self.graph_path = graph_path
        self.G = None
        self._load_graph()

    def _load_graph(self):
        if os.path.exists(self.graph_path):
            print(f"[Genetic] 🗺️  Încărcare hartă din {self.graph_path}...")
            self.G = ox.load_graphml(self.graph_path)
        else:
            print("[Genetic] ⚠️  Harta nu există. Se va descărca la prima rulare (poate dura)...")
            try:
                center_point = (44.435, 26.102) 
                self.G = ox.graph_from_point(center_point, dist=8000, network_type='drive')
                self.G = ox.add_edge_speeds(self.G)
                self.G = ox.add_edge_travel_times(self.G)
                os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
                ox.save_graphml(self.G, self.graph_path)
                print("[Genetic] ✅ Harta descărcată și salvată.")
            except Exception as e:
                print(f"[Genetic] ❌ Eroare descărcare hartă: {e}")
                self.G = None

    def _get_network_distance(self, loc1, loc2):
        if not self.G:
            # Fallback Euclidian
            return np.sqrt((loc1['lat']-loc2['lat'])**2 + (loc1['lon']-loc2['lon'])**2) * 111.0
        try:
            orig = ox.distance.nearest_nodes(self.G, loc1['lon'], loc1['lat'])
            dest = ox.distance.nearest_nodes(self.G, loc2['lon'], loc2['lat'])
            length_m = nx.shortest_path_length(self.G, orig, dest, weight='length')
            return length_m / 1000.0
        except:
            return 5.0

    def _get_detailed_path(self, route_indices, locations):
        full_path_coords = []
        if not self.G: return []
        
        for i in range(len(route_indices) - 1):
            start = locations[route_indices[i]]
            end = locations[route_indices[i+1]]
            try:
                orig = ox.distance.nearest_nodes(self.G, start['lon'], start['lat'])
                dest = ox.distance.nearest_nodes(self.G, end['lon'], end['lat'])
                path_nodes = nx.shortest_path(self.G, orig, dest, weight='length')
                for node_id in path_nodes:
                    full_path_coords.append({
                        "lat": self.G.nodes[node_id]['y'],
                        "lon": self.G.nodes[node_id]['x']
                    })
            except: pass
        return full_path_coords

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
            
            duration = self.ai_model.predict_trip_time(dist, int(current_hour))
            total_time += duration
            current_hour += (duration / 60.0)
            if current_hour >= 24: current_hour -= 24
        return total_time

    def solve(self, locations, generations=3, pop_size=10):
        print(f">>> [Genetic] Optimizare pentru {len(locations)} locații...")
        
        # Pre-calcul distanțe
        n = len(locations)
        dist_matrix = [[0]*n for _ in range(n)]
        if self.G:
            print("   [Genetic] Calculare matrice distanțe reale...")
            for i in range(n):
                for j in range(n):
                    if i != j:
                        dist_matrix[i][j] = self._get_network_distance(locations[i], locations[j])

        indices = list(range(len(locations)))
        depot_idx = 0 
        client_indices = indices[1:]
        
        best_route = indices
        best_fitness = float('inf')

        population = []
        for _ in range(pop_size):
            route = client_indices.copy()
            random.shuffle(route)
            population.append([depot_idx] + route)

        for gen in range(generations):
            for ind in population:
                fit = self.calculate_fitness(ind, locations, dist_matrix)
                if fit < best_fitness:
                    best_fitness = fit
                    best_route = ind
            
            new_pop = [best_route]
            for _ in range(pop_size - 1):
                child = best_route[1:].copy()
                random.shuffle(child)
                new_pop.append([depot_idx] + child)
            population = new_pop
            
        print(f"   [Genetic] Soluție: {best_fitness:.1f} min")
        detailed_geometry = self._get_detailed_path(best_route, locations)
        return best_route, best_fitness, detailed_geometry
