from flask import Flask, request, render_template, jsonify
import tensorflow as tf
import numpy as np
import cv2
import os
import gdown
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Google Drive file ID
FILE_ID = "1dtxCw1PCIQcbfkb2rgd6vr4Zpv-Y4Qv5"
MODEL_PATH = "model.h5"

def download_model():
    if not os.path.exists(MODEL_PATH):
        logger.info("Downloading model from Google Drive...")
        try:
            gdown.download(f"https://drive.google.com/uc?id={FILE_ID}", MODEL_PATH, quiet=False)
            logger.info("Model downloaded successfully")
        except Exception as e:
            logger.error(f"Failed to download model: {str(e)}")
            raise

# Download model at startup
try:
    download_model()
    model = tf.keras.models.load_model(MODEL_PATH)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Model loading failed: {str(e)}")
    model = None

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
        # Read and preprocess image
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            return jsonify({"error": "Invalid image file"}), 400
            
        image = cv2.resize(image, (224, 224))
        image = image / 255.0
        image = np.expand_dims(image, axis=0)

        # Predict
        predictions = model.predict(image)
        skin_tone_labels = ["light", "mid-light", "mid-dark", "dark"]
        predicted_skin_tone = skin_tone_labels[np.argmax(predictions)]

        return jsonify({"skin_tone": predicted_skin_tone})

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": "An error occurred during processing"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)