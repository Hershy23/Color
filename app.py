import logging
import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

# Model Configuration
MODEL_URL = "https://github.com/Hershy23/Color/releases/download/v2.0/model.h5"
MODEL_PATH = "model.h5"

# Download Model if Not Exists
if not os.path.exists(MODEL_PATH):
    logging.info("Downloading model...")
    response = requests.get(MODEL_URL)
    with open(MODEL_PATH, "wb") as file:
        file.write(response.content)
    logging.info("Model downloaded successfully!")

# Load Model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    logging.info("Model loaded successfully!")
except Exception as e:
    logging.error(f"Error loading model: {e}")

# ✅ Add root route to serve HTML
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        logging.error("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    logging.info(f"Received file: {file.filename}")

    try:
        img = Image.open(file).convert("RGB")
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)
        predicted_label = np.argmax(prediction, axis=1)[0]

        logging.info(f"Prediction output: {prediction}")
        logging.info(f"Predicted label: {predicted_label}")

        return jsonify({"prediction": int(predicted_label)})
    
    except Exception as e:
        logging.error(f"Prediction failed: {e}")
        return jsonify({"error": "Prediction failed"}), 500

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT, debug=False)
