# API Usage Examples

This document provides examples of how to interact with the Image Recognition App API programmatically.

## 🔗 Base URL

```
http://localhost:5000  # Local development
https://your-domain.com  # Production
```

## 📋 Endpoints

### Health Check

**GET** `/health`

Check if the application and model are ready.

```bash
curl -X GET http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### Image Prediction

**POST** `/predict`

Upload an image and get classification predictions.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file`: Image file (JPEG, PNG, GIF, BMP, WebP)

## 💻 Code Examples

### Python (requests)

```python
import requests
import json

def predict_image(image_path, api_url="http://localhost:5000"):
    """
    Send an image to the API for prediction.
    
    Args:
        image_path (str): Path to the image file
        api_url (str): Base URL of the API
    
    Returns:
        dict: Prediction results
    """
    url = f"{api_url}/predict"
    
    with open(image_path, 'rb') as image_file:
        files = {'file': image_file}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Example usage
if __name__ == "__main__":
    result = predict_image("path/to/your/image.jpg")
    
    if result and result['success']:
        print("Predictions:")
        for pred in result['predictions']:
            print(f"{pred['rank']}. {pred['label']}: {pred['percentage']}")
    else:
        print("Failed to get predictions")
```

### Python (with error handling)

```python
import requests
from pathlib import Path

class ImageRecognitionClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Check if the API is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            return None
    
    def predict(self, image_path):
        """
        Predict image classification.
        
        Args:
            image_path (str or Path): Path to image file
            
        Returns:
            dict: Prediction results or None if failed
        """
        image_path = Path(image_path)
        
        # Validate file exists
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Validate file size (16MB limit)
        file_size = image_path.stat().st_size
        if file_size > 16 * 1024 * 1024:
            raise ValueError("File size exceeds 16MB limit")
        
        # Validate file extension
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        if image_path.suffix.lower() not in allowed_extensions:
            raise ValueError(f"Unsupported file type: {image_path.suffix}")
        
        try:
            with open(image_path, 'rb') as image_file:
                files = {'file': (image_path.name, image_file, 'image/jpeg')}
                response = self.session.post(
                    f"{self.base_url}/predict",
                    files=files,
                    timeout=60  # Allow time for model inference
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response text: {e.response.text}")
            return None

# Example usage
client = ImageRecognitionClient()

# Check if API is healthy
health = client.health_check()
if health and health['status'] == 'healthy':
    print("✅ API is healthy")
    
    # Make prediction
    try:
        result = client.predict("example_image.jpg")
        if result and result['success']:
            print("\n🔍 Predictions:")
            for pred in result['predictions']:
                confidence_bar = "█" * int(pred['confidence'] * 20)
                print(f"{pred['rank']}. {pred['label']:<30} {pred['percentage']:>7} {confidence_bar}")
        else:
            print("❌ Prediction failed")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ API is not healthy")
```

### JavaScript (Node.js)

```javascript
const fs = require('fs');
const FormData = require('form-data');
const axios = require('axios');

class ImageRecognitionClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }

    async healthCheck() {
        try {
            const response = await axios.get(`${this.baseUrl}/health`);
            return response.data;
        } catch (error) {
            console.error('Health check failed:', error.message);
            return null;
        }
    }

    async predict(imagePath) {
        try {
            // Check if file exists
            if (!fs.existsSync(imagePath)) {
                throw new Error(`File not found: ${imagePath}`);
            }

            // Create form data
            const form = new FormData();
            form.append('file', fs.createReadStream(imagePath));

            // Make request
            const response = await axios.post(`${this.baseUrl}/predict`, form, {
                headers: {
                    ...form.getHeaders(),
                },
                timeout: 60000, // 60 seconds
            });

            return response.data;
        } catch (error) {
            console.error('Prediction failed:', error.message);
            if (error.response) {
                console.error('Error details:', error.response.data);
            }
            return null;
        }
    }
}

// Example usage
async function main() {
    const client = new ImageRecognitionClient();

    // Check health
    const health = await client.healthCheck();
    if (health && health.status === 'healthy') {
        console.log('✅ API is healthy');

        // Make prediction
        const result = await client.predict('example_image.jpg');
        if (result && result.success) {
            console.log('\n🔍 Predictions:');
            result.predictions.forEach(pred => {
                const confidenceBar = '█'.repeat(Math.floor(pred.confidence * 20));
                console.log(`${pred.rank}. ${pred.label.padEnd(30)} ${pred.percentage.padStart(7)} ${confidenceBar}`);
            });
        } else {
            console.log('❌ Prediction failed');
        }
    } else {
        console.log('❌ API is not healthy');
    }
}

main().catch(console.error);
```

### JavaScript (Browser)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Image Recognition API Example</title>
</head>
<body>
    <input type="file" id="imageInput" accept="image/*">
    <button onclick="predictImage()">Predict</button>
    <div id="results"></div>

    <script>
        async function predictImage() {
            const fileInput = document.getElementById('imageInput');
            const resultsDiv = document.getElementById('results');
            
            if (!fileInput.files[0]) {
                alert('Please select an image file');
                return;
            }

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            try {
                resultsDiv.innerHTML = 'Processing...';
                
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    let html = '<h3>Predictions:</h3><ul>';
                    result.predictions.forEach(pred => {
                        html += `<li>${pred.rank}. ${pred.label}: ${pred.percentage}</li>`;
                    });
                    html += '</ul>';
                    
                    html += `<img src="${result.image}" style="max-width: 300px; margin-top: 20px;">`;
                    resultsDiv.innerHTML = html;
                } else {
                    resultsDiv.innerHTML = `Error: ${result.error}`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `Error: ${error.message}`;
            }
        }
    </script>
</body>
</html>
```

### cURL Examples

```bash
# Health check
curl -X GET http://localhost:5000/health

# Image prediction
curl -X POST \
  -F "file=@path/to/your/image.jpg" \
  http://localhost:5000/predict

# With verbose output
curl -X POST \
  -F "file=@image.jpg" \
  -H "Accept: application/json" \
  -v \
  http://localhost:5000/predict
```

### PowerShell (Windows)

```powershell
# Health check
$healthResponse = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get
Write-Host "Health Status: $($healthResponse.status)"

# Image prediction
$imagePath = "C:\path\to\your\image.jpg"
$uri = "http://localhost:5000/predict"

# Create multipart form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$(Split-Path $imagePath -Leaf)`"",
    "Content-Type: image/jpeg$LF",
    [System.IO.File]::ReadAllText($imagePath),
    "--$boundary--$LF"
) -join $LF

try {
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $bodyLines -ContentType "multipart/form-data; boundary=$boundary"
    
    if ($response.success) {
        Write-Host "Predictions:"
        foreach ($pred in $response.predictions) {
            Write-Host "$($pred.rank). $($pred.label): $($pred.percentage)"
        }
    } else {
        Write-Host "Error: $($response.error)"
    }
} catch {
    Write-Host "Request failed: $($_.Exception.Message)"
}
```

## 📊 Response Format

### Successful Prediction Response

```json
{
  "success": true,
  "predictions": [
    {
      "rank": 1,
      "label": "Golden Retriever",
      "confidence": 0.8945,
      "percentage": "89.45%"
    },
    {
      "rank": 2,
      "label": "Labrador Retriever",
      "confidence": 0.0823,
      "percentage": "8.23%"
    },
    {
      "rank": 3,
      "label": "Nova Scotia Duck Tolling Retriever",
      "confidence": 0.0156,
      "percentage": "1.56%"
    },
    {
      "rank": 4,
      "label": "Cocker Spaniel",
      "confidence": 0.0045,
      "percentage": "0.45%"
    },
    {
      "rank": 5,
      "label": "Irish Setter",
      "confidence": 0.0031,
      "percentage": "0.31%"
    }
  ],
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

### Error Response

```json
{
  "error": "File type not allowed. Please upload an image file."
}
```

## 🚨 Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid file, missing parameters) |
| 413 | Request Entity Too Large (file > 16MB) |
| 500 | Internal Server Error (model error, processing error) |

## 📝 Best Practices

1. **Always check the health endpoint** before making predictions
2. **Implement retry logic** for network failures
3. **Validate file types and sizes** on the client side
4. **Handle errors gracefully** and provide user feedback
5. **Use appropriate timeouts** for API calls
6. **Cache results** when appropriate to reduce API calls

## 🔧 Rate Limiting

The API doesn't implement rate limiting by default, but you should:

- Implement client-side throttling
- Add server-side rate limiting in production
- Monitor API usage and performance

## 📈 Performance Tips

1. **Resize images** before uploading to reduce transfer time
2. **Use appropriate image formats** (JPEG for photos, PNG for graphics)
3. **Implement caching** for frequently predicted images
4. **Use connection pooling** for multiple requests
5. **Consider batch processing** for multiple images

---

For more information, see the main [README.md](README.md) and [DEPLOYMENT.md](DEPLOYMENT.md) files.