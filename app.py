from flask import Flask, request, render_template, jsonify
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
import numpy as np
import cv2

import logging
import gdown
from flask_cors import CORS
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model settings
MODEL_PATH = "model.h5"
FILE_ID = "1dtxCw1PCIQcbfkb2rgd6vr4Zpv-Y4Qv5"  # Replace with your actual Google Drive file ID

def download_model():
    """Downloads the model from Google Drive if it doesn't exist."""
    if not os.path.exists(MODEL_PATH):
        logger.info("Downloading model...")
        try:
            gdown.download(f"https://drive.google.com/uc?id={FILE_ID}", MODEL_PATH, quiet=False)
            logger.info("Model downloaded successfully.")
        except Exception as e:
            logger.error(f"Error downloading model: {str(e)}")

# Ensure model is downloaded before starting the app
download_model()

# Load the model
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        logger.info("Model loaded successfully.")
    except Exception as e:
        logger.error(f"Model loading failed: {str(e)}")
else:
    logger.error("Model file not found!")

# Initialize Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded. Service unavailable."}), 503

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded!"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected!"}), 400

    try:
        # Read and preprocess the image
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"error": "Invalid image file"}), 400

        # Preprocess image for model input
        image = cv2.resize(image, (224, 224))
        image = image / 255.0
        image = np.expand_dims(image, axis=0)

        # Make prediction
        predictions = model.predict(image)
        skin_tone_labels = ["light", "mid-light", "mid-dark", "dark"]
        predicted_skin_tone = skin_tone_labels[np.argmax(predictions)]

        return jsonify({"skin_tone": predicted_skin_tone})

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": "An error occurred during processing"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
