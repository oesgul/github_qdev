# Deployment Guide

This guide provides detailed instructions for deploying the Image Recognition App in various environments.

## 🚀 Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd image-recognition-app
   chmod +x run.sh
   ./run.sh
   ```

2. **Windows Users**
   ```cmd
   run.bat
   ```

### Docker Deployment

1. **Build and Run**
   ```bash
   docker build -t image-recognition-app .
   docker run -p 5000:5000 image-recognition-app
   ```

## 🌐 Production Deployment

### Environment Variables

Set these environment variables for production:

```bash
export SECRET_KEY="your-super-secret-key-here"
export FLASK_ENV="production"
export MAX_CONTENT_LENGTH="16777216"  # 16MB in bytes
```

### Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=production
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
```

### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        client_max_body_size 16M;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## ☁️ Cloud Deployment

### AWS ECS

1. **Create Task Definition**
   ```json
   {
     "family": "image-recognition-app",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "app",
         "image": "your-account.dkr.ecr.region.amazonaws.com/image-recognition-app:latest",
         "portMappings": [
           {
             "containerPort": 5000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "SECRET_KEY",
             "value": "your-secret-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/image-recognition-app",
             "awslogs-region": "us-west-2",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

### Google Cloud Run

1. **Deploy to Cloud Run**
   ```bash
   # Build and push to Container Registry
   gcloud builds submit --tag gcr.io/PROJECT-ID/image-recognition-app

   # Deploy to Cloud Run
   gcloud run deploy image-recognition-app \
     --image gcr.io/PROJECT-ID/image-recognition-app \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 1 \
     --max-instances 10
   ```

### Azure Container Instances

1. **Deploy to ACI**
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name image-recognition-app \
     --image your-registry.azurecr.io/image-recognition-app:latest \
     --cpu 1 \
     --memory 2 \
     --ports 5000 \
     --environment-variables SECRET_KEY=your-secret-key
   ```

## 🔧 Kubernetes Deployment

### Deployment Manifest

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-recognition-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: image-recognition-app
  template:
    metadata:
      labels:
        app: image-recognition-app
    spec:
      containers:
      - name: app
        image: image-recognition-app:latest
        ports:
        - containerPort: 5000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: image-recognition-service
spec:
  selector:
    app: image-recognition-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer

---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  secret-key: <base64-encoded-secret-key>
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
```

## 📊 Monitoring and Logging

### Application Metrics

Add to your deployment:

```python
# Add to app.py
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')
```

### Health Checks

The app includes a `/health` endpoint that returns:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### Logging Configuration

For production, configure structured logging:

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_entry)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

## 🔒 Security Considerations

### SSL/TLS Configuration

1. **Obtain SSL Certificate**
   ```bash
   # Using Let's Encrypt
   certbot certonly --webroot -w /var/www/html -d your-domain.com
   ```

2. **Configure HTTPS Redirect**
   - Use the Nginx configuration above
   - Or configure your cloud provider's load balancer

### Security Headers

Add security middleware:

```python
from flask_talisman import Talisman

Talisman(app, force_https=True)
```

### Environment Security

- Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
- Rotate secrets regularly
- Use least-privilege IAM roles
- Enable audit logging

## 🚨 Troubleshooting

### Common Issues

1. **Model Loading Errors**
   ```bash
   # Check TensorFlow installation
   python -c "import tensorflow as tf; print(tf.__version__)"
   
   # Verify model download
   python -c "from tensorflow.keras.applications import ResNet50; ResNet50(weights='imagenet')"
   ```

2. **Memory Issues**
   - Increase container memory limits
   - Use model quantization for smaller memory footprint
   - Implement model caching strategies

3. **Performance Issues**
   - Use multiple gunicorn workers
   - Implement request queuing
   - Add caching for frequent predictions

### Debugging

Enable debug mode for development:
```bash
export FLASK_DEBUG=1
python app.py
```

Check logs:
```bash
# Docker logs
docker logs container-name

# Kubernetes logs
kubectl logs deployment/image-recognition-app
```

## 📈 Scaling

### Horizontal Scaling

1. **Load Balancer Configuration**
   - Use sticky sessions if needed
   - Configure health checks
   - Set appropriate timeouts

2. **Auto-scaling**
   ```yaml
   # Kubernetes HPA
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: image-recognition-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: image-recognition-app
     minReplicas: 2
     maxReplicas: 10
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
   ```

### Vertical Scaling

- Monitor memory usage during model loading
- Adjust CPU limits based on inference time
- Consider GPU instances for better performance

---

For additional support, please refer to the main [README.md](README.md) or create an issue in the repository.