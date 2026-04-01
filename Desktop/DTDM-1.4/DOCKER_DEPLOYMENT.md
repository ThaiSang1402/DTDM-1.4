# Docker Deployment Guide

## 🐳 Docker Deployment Options

### **Quick Start with Docker Compose**

```bash
# Build and run all services
make docker-build
make docker-run

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
make docker-stop
```

### **Individual Docker Images**

#### **Load Balancer**
```bash
# Build
docker build -f Dockerfile.loadbalancer -t scalable-ai-api-loadbalancer .

# Run
docker run -p 8000:8000 \
  -e SERVER_A_URL=http://server-a:8080 \
  -e SERVER_B_URL=http://server-b:8080 \
  scalable-ai-api-loadbalancer
```

#### **AI Server**
```bash
# Build
docker build -f Dockerfile.aiserver -t scalable-ai-api-server .

# Run Server A
docker run -p 8080:8080 \
  -e SERVER_ID="Server A" \
  scalable-ai-api-server

# Run Server B
docker run -p 8081:8080 \
  -e SERVER_ID="Server B" \
  scalable-ai-api-server
```

## 🚀 Production Deployment

### **Docker Swarm**
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml scalable-ai-api

# Check services
docker service ls

# Scale services
docker service scale scalable-ai-api_server-a=2
docker service scale scalable-ai-api_server-b=2
```

### **Kubernetes Deployment**
```bash
# Generate Kubernetes manifests
docker-compose -f docker-compose.prod.yml config > k8s-manifest.yaml

# Apply to cluster
kubectl apply -f k8s-manifest.yaml
```

## 🔧 Configuration

### **Environment Variables**

#### **Load Balancer:**
- `SERVER_A_URL`: URL of Server A (default: http://server-a:8080)
- `SERVER_B_URL`: URL of Server B (default: http://server-b:8080)
- `HEALTH_CHECK_INTERVAL`: Health check interval in seconds (default: 30)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)
- `LOG_LEVEL`: Logging level (default: INFO)

#### **AI Servers:**
- `SERVER_ID`: Server identifier (required: "Server A" or "Server B")
- `LOG_LEVEL`: Logging level (default: INFO)

### **Resource Limits**
```yaml
# Production limits per service
resources:
  limits:
    cpus: '0.5'
    memory: 512M
  reservations:
    cpus: '0.25'
    memory: 256M
```

## 🏥 Health Checks

All services include built-in health checks:

```bash
# Check Load Balancer
curl http://localhost:8000/health

# Check Server A
curl http://localhost:8080/health

# Check Server B
curl http://localhost:8081/health
```

## 📊 Monitoring

### **Docker Stats**
```bash
# Real-time stats
docker stats

# Service logs
docker-compose logs -f load-balancer
docker-compose logs -f server-a
docker-compose logs -f server-b
```

### **Health Check Status**
```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## 🔍 Troubleshooting

### **Common Issues**

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   
   # Use different ports
   docker-compose up -d --scale load-balancer=0
   docker run -p 9000:8000 scalable-ai-api-loadbalancer
   ```

2. **Memory Issues**
   ```bash
   # Check memory usage
   docker stats --no-stream
   
   # Increase memory limits in docker-compose.yml
   ```

3. **Network Issues**
   ```bash
   # Check network connectivity
   docker network ls
   docker network inspect scalable-ai-api_ai-network
   ```

### **Debug Commands**
```bash
# Enter container shell
docker exec -it scalable-ai-api_load-balancer_1 /bin/bash

# Check logs
docker logs scalable-ai-api_load-balancer_1

# Inspect container
docker inspect scalable-ai-api_load-balancer_1
```

## 🧪 Testing

### **Automated Testing**
```bash
# Test Docker deployment
make docker-test

# Manual testing
docker-compose up -d
sleep 30

# Test Load Balancer
curl -X POST http://localhost:8000/api/ai \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello Docker!", "client_id": "test"}'

# Test round-robin
for i in {1..4}; do
  curl -X POST http://localhost:8000/api/ai \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"Request $i\", \"client_id\": \"test$i\"}"
  echo ""
done
```

## 📦 Image Management

### **Build Optimization**
```bash
# Multi-stage build (future enhancement)
# Use .dockerignore to reduce build context
# Layer caching for faster builds

# Check image sizes
docker images | grep scalable-ai-api
```

### **Registry Deployment**
```bash
# Tag for registry
docker tag scalable-ai-api-loadbalancer your-registry/scalable-ai-api-loadbalancer:latest
docker tag scalable-ai-api-server your-registry/scalable-ai-api-server:latest

# Push to registry
docker push your-registry/scalable-ai-api-loadbalancer:latest
docker push your-registry/scalable-ai-api-server:latest
```

## 🔐 Security

### **Best Practices**
- ✅ Non-root user in containers
- ✅ Minimal base images (python:3.11-slim)
- ✅ .dockerignore to exclude sensitive files
- ✅ Health checks for reliability
- ✅ Resource limits to prevent abuse

### **Production Security**
```bash
# Scan images for vulnerabilities
docker scan scalable-ai-api-loadbalancer
docker scan scalable-ai-api-server

# Use secrets for sensitive data
docker secret create db_password password.txt
```