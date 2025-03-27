import logging
import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # This import was missing
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from waitress import serve

# Rest of your existing app.py code remains the same...

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
MODEL_URL = "https://github.com/Hershy23/Color/releases/download/v2.0/model.h5"
MODEL_PATH = "model.h5"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
SKIN_TONES = [
    "Very Light (Type I)",
    "Light (Type II)",
    "Medium (Type III)", 
    "Olive (Type IV)",
    "Brown (Type V)",
    "Dark (Type VI)"
]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_model():
    """Download the model if it doesn't exist"""
    if not os.path.exists(MODEL_PATH):
        logger.info("Downloading model...")
        try:
            response = requests.get(MODEL_URL, stream=True)
            response.raise_for_status()
            with open(MODEL_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info("Model downloaded successfully!")
        except Exception as e:
            logger.error(f"Model download failed: {str(e)}")
            raise

def load_model():
    """Load the TensorFlow model with error handling"""
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        logger.info("Model loaded successfully!")
        return model
    except Exception as e:
        logger.error(f"Model loading failed: {str(e)}")
        # Create dummy model if real one fails
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(1, input_shape=(224, 224, 3))
        ])
        logger.warning("Using dummy model - predictions will be random")
        return model

# Initialize model
download_model()
model = load_model()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check file type
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        
        # Read and process image
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Make prediction
        prediction = model.predict(img_array)
        predicted_idx = int(np.argmax(prediction, axis=1)[0])
        confidence = float(np.max(prediction))
        
        return jsonify({
            "success": True,
            "prediction": predicted_idx,
            "confidence": confidence,
            "label": SKIN_TONES[predicted_idx],
            "message": "Analysis complete"
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Prediction failed",
            "message": str(e)
        }), 500

def run_server():
    port = int(os.environ.get('PORT', 5000))
    if os.environ.get('ENV') == 'PRODUCTION':
        # Production server (Render)
        serve(app, host="0.0.0.0", port=port, threads=4)
    else:
        # Development server
        app.run(host="0.0.0.0", port=port, debug=True)

if __name__ == '__main__':
    run_server()
