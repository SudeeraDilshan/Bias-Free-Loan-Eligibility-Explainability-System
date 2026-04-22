# Deployment Guide

Complete guide for deploying the Bias-Free Loan Eligibility System in different environments.

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- Git

### Step-by-Step Installation

#### 1. Clone Repository

```bash
git clone https://github.com/yourrepo/loan-eligibility-system.git
cd loan-eligibility-system
```

#### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Download and prepare dataset
python ../ml/download_dataset.py

# Train model (first time only)
python ../ml/train_model.py

# Start backend
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

**Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Docker Deployment

### Build & Run with Docker Compose

```bash
# Build all services
docker-compose build

# Start services
docker-compose up

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Individual Docker Builds

```bash
# Build backend
docker build -f Dockerfile.backend -t loan-backend:1.0 .

# Build frontend
docker build -f Dockerfile.frontend -t loan-frontend:1.0 .

# Run backend
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./app.db \
  -v $(pwd)/ml:/app/ml \
  loan-backend:1.0

# Run frontend  
docker run -p 3000:3000 \
  -e REACT_APP_API_URL=http://localhost:8000 \
  loan-frontend:1.0
```

### Docker Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check if services are ready
docker-compose ps
```

---

## Cloud Deployment

### AWS EC2 Deployment

#### 1. Launch EC2 Instance

```bash
# Ubuntu 22.04 LTS recommended
# Instance type: t3a.medium or larger
# Security group: Allow ports 80, 443, 8000, 3000
```

#### 2. SSH into Instance

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 3. Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3-pip nodejs npm git docker.io

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 4. Clone & Deploy

```bash
git clone your-repo
cd loan-eligibility-system

# Set up environment
cp backend/.env.example backend/.env
# Edit backend/.env with production settings

# Start with Docker Compose
docker-compose up -d

# Install Nginx reverse proxy
sudo apt install -y nginx
```

#### 5. Configure Nginx

```nginx
# /etc/nginx/sites-available/default

upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Backend API
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend/;
        proxy_set_header Host $host;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

---

### Google Cloud Run Deployment

#### 1. Prerequisites

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize
gcloud init
gcloud auth configure-docker
```

#### 2. Build & Push Images

```bash
# Set project
export PROJECT_ID=your-project-id

# Build backend
docker build -f Dockerfile.backend -t gcr.io/$PROJECT_ID/loan-backend:latest .
docker push gcr.io/$PROJECT_ID/loan-backend:latest

# Build frontend
docker build -f Dockerfile.frontend -t gcr.io/$PROJECT_ID/loan-frontend:latest .
docker push gcr.io/$PROJECT_ID/loan-frontend:latest
```

#### 3. Deploy to Cloud Run

```bash
# Deploy backend
gcloud run deploy loan-backend \
  --image gcr.io/$PROJECT_ID/loan-backend:latest \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated \
  --set-env-vars DEBUG=False

# Deploy frontend
gcloud run deploy loan-frontend \
  --image gcr.io/$PROJECT_ID/loan-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

### Azure Container Instances

#### 1. Prerequisites

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login
```

#### 2. Push to Azure Container Registry

```bash
# Create registry
az acr create --resource-group myResourceGroup \
  --name loanregistry --sku Basic

# Build images
az acr build --registry loanregistry \
  --image loan-backend:latest \
  --file Dockerfile.backend .
```

#### 3. Deploy Containers

```bash
# Deploy backend
az container create \
  --resource-group myResourceGroup \
  --name loan-backend \
  --image loanregistry.azurecr.io/loan-backend:latest \
  --ports 8000 \
  --cpu 1 --memory 2

# Deploy frontend
az container create \
  --resource-group myResourceGroup \
  --name loan-frontend \
  --image loanregistry.azurecr.io/loan-frontend:latest \
  --ports 3000 \
  --cpu 1 --memory 1
```

---

## Production Configuration

### Backend Configuration

Create `backend/.env`:

```env
# API Settings
API_TITLE=Bias-Free Loan Eligibility System
PORT=8000
DEBUG=False
ENV=production

# Security
SECRET_KEY=your-very-secure-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:password@db:5432/loandb

# Model Paths
MODEL_PATH=/app/ml/models/xgboost_model.joblib
SCALER_PATH=/app/ml/models/scaler.joblib

# CORS
CORS_ORIGINS=["https://yourdomain.com"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/api.log

# Email notifications (for alerts)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Database Setup (PostgreSQL)

```bash
# Create database
createdb loandb

# Run migrations
psql loandb -f database/schema.sql

# Load data
psql loandb -f database/initial_data.sql
```

### SSL/TLS Certificate

```bash
# Using Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com

# Auto-renew
sudo systemctl enable certbot.timer
```

---

## Performance Optimization

### Backend Optimization

```python
# in app/main.py

from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend
from fastapi_cache2.decorator import cache

# Configure caching
@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache2.init(RedisBackend(redis), prefix="loan-api")

# Cache predictions for identical applications
@cache(expire=3600)
@app.post("/predict")
async def predict_loan_eligibility(application: LoanApplicationInput):
    # ... prediction logic
```

### Frontend Optimization

```javascript
// Vite config - code splitting
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'api': ['axios'],
          'charts': ['recharts']
        }
      }
    }
  }
}

// Lazy loading components
const PredictionResult = lazy(() => import('./components/PredictionResult'));
const SHAPExplanation = lazy(() => import('./components/SHAPExplanation'));
```

### Load Balancing

```nginx
upstream backend_pool {
    server backend1.local:8000;
    server backend2.local:8000;
    server backend3.local:8000;
    least_conn;  # Least connections strategy
}

server {
    location /api/ {
        proxy_pass http://backend_pool/;
    }
}
```

---

## Monitoring & Logging

### Application Monitoring

```python
# Setup logging
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.FileHandler(filename='logs/app.log')
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger('loan-api')
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Log predictions
logger.info('Prediction made', extra={
    'loan_id': prediction.loan_id,
    'decision': prediction.prediction,
    'confidence': prediction.confidence_score
})
```

### Health Monitoring

```bash
# Setup monitoring with Prometheus
docker run -d \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Add to docker-compose.yml for integration
```

### Extract Metrics

```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
prediction_counter = Counter('predictions_total', 'Total predictions', ['decision'])
approval_rate = Gauge('approval_rate', 'Current approval rate')
prediction_time = Histogram('prediction_duration_seconds', 'Prediction duration')

@app.post("/predict")
@prediction_time.time()
async def predict_loan_eligibility(application):
    # ... logic
    prediction_counter.labels(decision=result['prediction']).inc()
```

---

## Backup & Disaster Recovery

### Automated Backups

```bash
# Backup database daily
0 2 * * * pg_dump loandb | gzip > /backups/loandb_$(date +\%Y\%m\%d).sql.gz

# Backup models
0 3 * * * tar -czf /backups/models_$(date +\%Y\%m\%d).tar.gz /app/ml/models/

# Backup to S3
aws s3 sync /backups s3://my-bucket/loan-system-backups/ --delete
```

### Disaster Recovery Plan

```
RTO (Recovery Time Objective): 1 hour
RPO (Recovery Point Objective): 4 hours

Procedure:
1. Restore database from latest backup
2. Deploy latest model versions
3. Run smoke tests
4. Verify fairness metrics
5. Gradual traffic shift (canary deployment)
```

---

## Security Checklist

- [ ] HTTPS/TLS enabled
- [ ] CORS configured for trusted domains
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (use ORM/parameterized queries)
- [ ] XSS prevention in frontend
- [ ] CSRF tokens enabled
- [ ] Secrets in environment variables (not in code)
- [ ] API key authentication enabled
- [ ] Audit logging enabled
- [ ] Regular security updates applied
- [ ] Data encryption at rest and in transit

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Verify model files exist
ls -la ml/models/

# Test imports
python -c "from ml.models import xgboost_model"
```

### Frontend can't reach backend

```bash
# Check CORS headers
curl -i -X OPTIONS http://localhost:8000/predict

# Verify API URL in .env
echo $REACT_APP_API_URL

# Check network connectivity
docker network inspect loan-network
```

### Slow predictions

```bash
# Profile prediction function
python -m cProfile -s cumulative predict.py

# Check SHAP computation time
import time
start = time.time()
shap_explainer.shap_values(X)
print(f"SHAP time: {time.time() - start}s")
```

---

## Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://react.dev/learn/start-a-new-react-project)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

---

**Last Updated**: April 2026  
**Version**: 1.0.0
