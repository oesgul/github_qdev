# Image Recognition App

A modern web application for image classification using deep learning models. Built with Flask and TensorFlow, featuring a responsive web interface and robust CI/CD pipeline.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.3+-green.svg)
![TensorFlow](https://img.shields.io/badge/tensorflow-v2.13+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

- **AI-Powered Recognition**: Uses ResNet50 pre-trained model for accurate image classification
- **Modern Web Interface**: Responsive design with drag-and-drop file upload
- **Real-time Processing**: Fast image analysis with confidence scores
- **Multiple Input Methods**: Support for drag-and-drop, file browser, and API endpoints
- **Comprehensive Testing**: Full test suite with high code coverage
- **Production Ready**: Docker containerization and CI/CD pipeline
- **Security Focused**: Input validation, file type checking, and secure file handling

## 🖼️ Supported Image Formats

- JPEG/JPG
- PNG
- GIF
- BMP
- WebP

## 🛠️ Technology Stack

- **Backend**: Python, Flask, TensorFlow/Keras
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI Model**: ResNet50 (ImageNet pre-trained)
- **Testing**: pytest, coverage
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Docker (optional, for containerized deployment)

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd image-recognition-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t image-recognition-app .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 image-recognition-app
   ```

3. **Access the application**
   Open `http://localhost:5000` in your browser

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_app.py -v
```

## 🔧 Code Quality

The project includes automated code quality checks:

```bash
# Linting
flake8 .

# Code formatting
black .

# Security scanning
bandit -r .
```

## 📊 API Endpoints

### Health Check
```
GET /health
```
Returns application health status and model loading state.

### Image Prediction
```
POST /predict
Content-Type: multipart/form-data

Parameters:
- file: Image file to classify
```

Returns JSON with predictions and confidence scores.

### Web Interface
```
GET /          # Main page with drag-and-drop upload
GET /upload    # Simple upload form
POST /upload   # Process uploaded image
```

## 🏗️ Project Structure

```
image-recognition-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── .dockerignore         # Docker ignore rules
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Main page
│   ├── upload.html      # Upload form
│   ├── results.html     # Results display
│   ├── 404.html         # 404 error page
│   └── 500.html         # 500 error page
├── tests/               # Test suite
│   ├── __init__.py
│   └── test_app.py      # Application tests
└── .github/
    └── workflows/
        └── ci.yml       # CI/CD pipeline
```

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline includes:

1. **Testing**: Multi-version Python testing (3.8, 3.9, 3.10)
2. **Code Quality**: Linting with flake8, formatting with black
3. **Security**: Vulnerability scanning with bandit and safety
4. **Build**: Docker image creation and testing
5. **Deploy**: Automated deployment to staging/production

### Pipeline Triggers

- **Push** to `main` or `develop` branches
- **Pull requests** to `main` branch

## 🚀 Deployment

### Environment Variables

- `SECRET_KEY`: Flask secret key for session management
- `FLASK_ENV`: Environment (development/production)
- `MAX_CONTENT_LENGTH`: Maximum file upload size

### Production Considerations

1. **Security**: Change default secret key
2. **Performance**: Use gunicorn with multiple workers
3. **Monitoring**: Implement logging and health checks
4. **Scaling**: Consider load balancing for high traffic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **TensorFlow Team** for the excellent deep learning framework
- **ResNet Authors** for the groundbreaking architecture
- **ImageNet** for the comprehensive dataset
- **Flask Community** for the lightweight web framework

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include error logs and system information

## 🔮 Future Enhancements

- [ ] Support for custom model uploads
- [ ] Batch image processing
- [ ] Real-time webcam classification
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

---

**Built with ❤️ using Python, Flask, and TensorFlow**