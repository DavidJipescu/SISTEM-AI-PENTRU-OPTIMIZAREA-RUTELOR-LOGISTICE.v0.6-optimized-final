from flask import Flask, jsonify, request, render_template
from src.neural_network.model import TrafficModel
from src.optimization.genetic import GeneticOptimizer
import os
import sys

# Specificăm folderul de template-uri pentru HTML
app = Flask(__name__, template_folder='templates')

# --- INIȚIALIZARE SIA ---
print("\n--- [SERVER] INIȚIALIZARE SISTEM HIBRID ---")
ai_brain = None
optimizer = None

try:
    ai_brain = TrafficModel()
    optimizer = GeneticOptimizer(ai_brain)
    print("[SERVER] Module încărcate cu succes.")
except Exception as e:
    print(f"[CRITIC] Eroare la inițializare: {e}")

# --- RUTE WEB ---

@app.route('/')
def home():
    # Servim interfața grafică din templates/index.html
    return render_template('index.html')

@app.route('/api/optimize', methods=['POST'])
def optimize_route():
    if not optimizer:
        return jsonify({"error": "Sistemul nu este inițializat corect."}), 500

    data = request.json
    locations = data.get('locations', [])
    
    if not locations or len(locations) < 2:
        return jsonify({"error": "Lista de locații invalidă."}), 400

    print(f"[API] Cerere optimizare UI pentru {len(locations)} puncte...")
    
    try:
        # Rezultat extins cu geometrie pentru hartă
        best_route_indices, total_time, detailed_path = optimizer.solve(locations)
        
        optimized_locs = [locations[i] for i in best_route_indices]
        
        response = {
            "status": "success",
            "result": {
                "estimated_duration_min": round(total_time, 2),
                "optimized_stops": optimized_locs,
                "detailed_geometry": detailed_path
            }
        }
        return jsonify(response)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
