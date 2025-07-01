from flask import Flask, request, jsonify
import numpy as np
from models.ml_model import SimpleModel

app = Flask(__name__)

# Initialize the global model
global_model = SimpleModel()
global_model_initialized = False
num_updates_received = 0

# Simple aggregation: average weights from clients
def aggregate_models(global_weights, new_weights, num_clients):
    # Assuming weights is a dict with 'coefficients' and 'intercept' lists/scalars
    agg_coefs = [(g + n) / num_clients for g, n in zip(global_weights['coefficients'], new_weights['coefficients'])]
    agg_intercept = (global_weights['intercept'] + new_weights['intercept']) / num_clients
    return {
        'coefficients': agg_coefs,
        'intercept': agg_intercept
    }

@app.route("/upload_model", methods=["POST"])
def upload_model():
    global global_model_initialized, num_updates_received, global_model
    
    client_weights = request.get_json()
    
    if not global_model_initialized:
        global_model.load_weights(client_weights)
        global_model_initialized = True
        num_updates_received = 1
        print("[Server] Initialized global model from first client update.")
        return "Global model initialized", 200
    
    # Aggregate client weights into global model
    old_weights = global_model.get_weights()
    num_updates_received += 1
    agg_weights = aggregate_models(old_weights, client_weights, num_updates_received)
    
    global_model.load_weights(agg_weights)
    print(f"[Server] Aggregated model update #{num_updates_received}")
    
    return "Model updated and aggregated", 200

@app.route("/get_global_model", methods=["GET"])
def get_global_model():
    if not global_model_initialized:
        return jsonify({"error": "No global model yet"}), 404
    return jsonify(global_model.get_weights())

if __name__ == "__main__":
    app.run(debug=True)
