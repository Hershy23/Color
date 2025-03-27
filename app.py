import logging
import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
MODEL_URL = "https://github.com/Hershy23/Color/releases/download/v2.0/model.h5"
MODEL_PATH = "model.h5"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Download model if not exists
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
        logger.error(f"Failed to download model: {str(e)}")
        raise

# Load model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    logger.info("Model loaded successfully!")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Check if request contains file
    if 'file' not in request.files:
        logger.error("No file part in request")
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    # Check if file is selected
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({"error": "No file selected"}), 400
    
    # Check file type
    if not allowed_file(file.filename):
        logger.error(f"Invalid file type: {file.filename}")
        return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG, WEBP allowed"}), 400
    
    try:
        # Read image directly from memory
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        
        # Process image
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Make prediction
        prediction = model.predict(img_array)
        predicted_label = int(np.argmax(prediction, axis=1)[0])
        confidence = float(np.max(prediction))
        
        logger.info(f"Prediction successful - Label: {predicted_label}, Confidence: {confidence:.2f}")
        
        return jsonify({
            "success": True,
            "prediction": predicted_label,
            "confidence": confidence,
            "message": "Analysis complete"
        })
    
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Prediction failed",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
