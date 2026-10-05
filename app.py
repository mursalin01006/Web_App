# ==============================================================================
# SQL Injection Detection API - Flask Web Application
# ==============================================================================

import os
import time
import joblib
from flask import Flask, request, jsonify, render_template

# Initialize Flask application
app = Flask(__name__)

# Load pre-trained model and vectorizer at startup
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

print(f"Model loaded successfully from: {MODEL_PATH}")
print(f"Vectorizer loaded successfully from: {VECTORIZER_PATH}")


@app.route("/")
def index():
    """Render the main dashboard page."""
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """Accept a SQL query string and return detection result with confidence."""
    data = request.get_json(silent=True)

    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' field in request body."}), 400

    user_query = str(data["query"]).strip()

    if len(user_query) == 0:
        return jsonify({"error": "Empty query submitted."}), 400

    if len(user_query) > 5000:
        return jsonify({"error": "Query exceeds maximum length of 5000 characters."}), 400

    # Measure inference latency
    start_time = time.time()
    query_vector = vectorizer.transform([user_query])
    prediction = model.predict(query_vector)[0]

    # Compute confidence score
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(query_vector)[0]
        confidence = float(probabilities[prediction]) * 100
    else:
        confidence = 99.0

    latency_ms = (time.time() - start_time) * 1000

    is_malicious = int(prediction) == 1
    status = "MALICIOUS" if is_malicious else "SAFE"
    description = "SQL Injection Attack Detected" if is_malicious else "Legitimate Query - No Threat"

    return jsonify({
        "status": status,
        "description": description,
        "is_malicious": is_malicious,
        "confidence": round(confidence, 2),
        "latency_ms": round(latency_ms, 2),
        "input_query": user_query
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for deployment platforms."""
    return jsonify({"status": "healthy", "model": "Random Forest", "accuracy": "99.58%"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
