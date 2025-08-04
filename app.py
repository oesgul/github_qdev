"""
Image Recognition Web Application
A Flask-based web app for image classification using pre-trained models.
"""

import os
import io
import base64
from flask import Flask, request, render_template, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Global model variable
model = None

def load_model():
    """Load the pre-trained ResNet50 model."""
    global model
    if model is None:
        logger.info("Loading ResNet50 model...")
        model = ResNet50(weights='imagenet')
        logger.info("Model loaded successfully!")
    return model

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image):
    """Preprocess image for model prediction."""
    try:
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image to 224x224 (ResNet50 input size)
        image = image.resize((224, 224))
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        # Preprocess for ResNet50
        img_array = preprocess_input(img_array)
        
        return img_array
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise

def predict_image(image):
    """Make prediction on preprocessed image."""
    try:
        model = load_model()
        
        # Preprocess the image
        processed_image = preprocess_image(image)
        
        # Make prediction
        predictions = model.predict(processed_image)
        
        # Decode predictions
        decoded_predictions = decode_predictions(predictions, top=5)[0]
        
        # Format results
        results = []
        for i, (imagenet_id, label, score) in enumerate(decoded_predictions):
            results.append({
                'rank': i + 1,
                'label': label.replace('_', ' ').title(),
                'confidence': float(score),
                'percentage': f"{score * 100:.2f}%"
            })
        
        return results
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        raise

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

@app.route('/predict', methods=['POST'])
def predict():
    """Handle image upload and prediction."""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload an image file.'}), 400
        
        # Read and process the image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Make prediction
        predictions = predict_image(image)
        
        # Convert image to base64 for display
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'image': f"data:image/jpeg;base64,{img_base64}"
        })
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file upload via form submission."""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                flash('No file selected')
                return redirect(request.url)
            
            file = request.files['file']
            
            if file.filename == '':
                flash('No file selected')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                # Process the image
                image_bytes = file.read()
                image = Image.open(io.BytesIO(image_bytes))
                
                # Make prediction
                predictions = predict_image(image)
                
                # Convert image to base64 for display
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                return render_template('results.html', 
                                     predictions=predictions,
                                     image=f"data:image/jpeg;base64,{img_base64}")
            else:
                flash('Invalid file type. Please upload an image file.')
                return redirect(request.url)
                
        except Exception as e:
            logger.error(f"Error in upload: {str(e)}")
            flash(f'Error processing image: {str(e)}')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Load model on startup
    load_model()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)