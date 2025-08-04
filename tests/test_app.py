"""
Unit tests for the image recognition app.
"""

import pytest
import io
import json
from PIL import Image
import numpy as np
from unittest.mock import patch, MagicMock

# Import the app
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, allowed_file, preprocess_image, predict_image, load_model


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_image():
    """Create a sample test image."""
    # Create a simple RGB image
    image = Image.new('RGB', (224, 224), color='red')
    return image


@pytest.fixture
def sample_image_bytes():
    """Create sample image bytes for upload testing."""
    image = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_allowed_file_valid_extensions(self):
        """Test allowed_file function with valid extensions."""
        assert allowed_file('test.jpg') == True
        assert allowed_file('test.jpeg') == True
        assert allowed_file('test.png') == True
        assert allowed_file('test.gif') == True
        assert allowed_file('test.bmp') == True
        assert allowed_file('test.webp') == True
        assert allowed_file('TEST.JPG') == True  # Case insensitive
    
    def test_allowed_file_invalid_extensions(self):
        """Test allowed_file function with invalid extensions."""
        assert allowed_file('test.txt') == False
        assert allowed_file('test.pdf') == False
        assert allowed_file('test.doc') == False
        assert allowed_file('test') == False
        assert allowed_file('') == False
    
    def test_preprocess_image(self, sample_image):
        """Test image preprocessing function."""
        processed = preprocess_image(sample_image)
        
        # Check shape
        assert processed.shape == (1, 224, 224, 3)
        
        # Check data type
        assert processed.dtype == np.float32
    
    def test_preprocess_image_different_modes(self):
        """Test preprocessing with different image modes."""
        # Test RGBA image
        rgba_image = Image.new('RGBA', (100, 100), color='red')
        processed = preprocess_image(rgba_image)
        assert processed.shape == (1, 224, 224, 3)
        
        # Test grayscale image
        gray_image = Image.new('L', (100, 100), color=128)
        processed = preprocess_image(gray_image)
        assert processed.shape == (1, 224, 224, 3)


class TestRoutes:
    """Test Flask routes."""
    
    def test_index_route(self, client):
        """Test the main index route."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Image Recognition' in response.data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'model_loaded' in data
    
    def test_upload_route_get(self, client):
        """Test upload route with GET request."""
        response = client.get('/upload')
        assert response.status_code == 200
        assert b'Upload Image' in response.data
    
    def test_predict_no_file(self, client):
        """Test predict endpoint with no file."""
        response = client.post('/predict')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No file uploaded' in data['error']
    
    def test_predict_empty_filename(self, client):
        """Test predict endpoint with empty filename."""
        data = {'file': (io.BytesIO(b''), '')}
        response = client.post('/predict', data=data)
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'No file selected' in response_data['error']
    
    def test_predict_invalid_file_type(self, client):
        """Test predict endpoint with invalid file type."""
        data = {'file': (io.BytesIO(b'test content'), 'test.txt')}
        response = client.post('/predict', data=data)
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'File type not allowed' in response_data['error']
    
    @patch('app.predict_image')
    def test_predict_success(self, mock_predict, client, sample_image_bytes):
        """Test successful prediction."""
        # Mock the prediction function
        mock_predict.return_value = [
            {
                'rank': 1,
                'label': 'Test Object',
                'confidence': 0.95,
                'percentage': '95.00%'
            }
        ]
        
        data = {'file': (sample_image_bytes, 'test.jpg')}
        response = client.post('/predict', data=data)
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert response_data['success'] == True
        assert 'predictions' in response_data
        assert 'image' in response_data
        assert len(response_data['predictions']) == 1
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        assert b'Page Not Found' in response.data


class TestModelFunctions:
    """Test model-related functions."""
    
    @patch('app.ResNet50')
    def test_load_model(self, mock_resnet):
        """Test model loading function."""
        # Mock the ResNet50 model
        mock_model = MagicMock()
        mock_resnet.return_value = mock_model
        
        # Clear the global model variable
        import app
        app.model = None
        
        # Load the model
        loaded_model = load_model()
        
        # Verify model was loaded
        assert loaded_model is not None
        mock_resnet.assert_called_once_with(weights='imagenet')
    
    @patch('app.load_model')
    @patch('app.decode_predictions')
    def test_predict_image_success(self, mock_decode, mock_load_model, sample_image):
        """Test successful image prediction."""
        # Mock the model and predictions
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([[0.1, 0.9, 0.05, 0.02, 0.01]])
        mock_load_model.return_value = mock_model
        
        mock_decode.return_value = [[
            ('n123', 'test_object', 0.9),
            ('n124', 'another_object', 0.1),
        ]]
        
        # Make prediction
        results = predict_image(sample_image)
        
        # Verify results
        assert len(results) == 2
        assert results[0]['rank'] == 1
        assert results[0]['label'] == 'Test Object'
        assert results[0]['confidence'] == 0.9
        assert results[0]['percentage'] == '90.00%'


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_file_too_large(self, client):
        """Test file size limit handling."""
        # Create a large file (simulate by setting content-length)
        large_data = b'x' * (17 * 1024 * 1024)  # 17MB
        
        response = client.post('/predict', 
                             data={'file': (io.BytesIO(large_data), 'large.jpg')},
                             content_length=17 * 1024 * 1024)
        
        # Should return 413 (Request Entity Too Large)
        assert response.status_code == 413
    
    @patch('app.predict_image')
    def test_prediction_error_handling(self, mock_predict, client, sample_image_bytes):
        """Test error handling in prediction."""
        # Mock prediction to raise an exception
        mock_predict.side_effect = Exception("Model error")
        
        data = {'file': (sample_image_bytes, 'test.jpg')}
        response = client.post('/predict', data=data)
        
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'error' in response_data


class TestIntegration:
    """Integration tests."""
    
    def test_upload_form_submission(self, client, sample_image_bytes):
        """Test form-based upload workflow."""
        with patch('app.predict_image') as mock_predict:
            mock_predict.return_value = [
                {
                    'rank': 1,
                    'label': 'Test Object',
                    'confidence': 0.85,
                    'percentage': '85.00%'
                }
            ]
            
            data = {'file': (sample_image_bytes, 'test.jpg')}
            response = client.post('/upload', data=data)
            
            # Should render results template
            assert response.status_code == 200
            assert b'Recognition Results' in response.data
            assert b'Test Object' in response.data


if __name__ == '__main__':
    pytest.main([__file__])