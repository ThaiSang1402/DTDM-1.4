# Deployment Commands - Scalable AI API System

## 🚀 Render Platform Deployment

### 1. Automatic Deployment (Recommended)
```bash
# Connect your GitHub repository to Render
# Render will automatically use render.yaml configuration
```

### 2. Manual Service Creation

#### Load Balancer Service:
```bash
# Service Name: scalable-ai-api-load-balancer
# Runtime: Python
# Build Command: pip install --upgrade pip && pip install -r requirements.txt
# Start Command: uvicorn scalable_ai_api.load_balancer.render_app:app --host 0.0.0.0 --port $PORT
```

#### Server A Service:
```bash
# Service Name: scalable-ai-api-server-a
# Runtime: Python
# Build Command: pip install --upgrade pip && pip install -r requirements.txt
# Start Command: uvicorn scalable_ai_api.ai_server.render_app:app --host 0.0.0.0 --port $PORT
# Environment Variables:
#   SERVER_ID=Server A
#   LOG_LEVEL=INFO
```

#### Server B Service:
```bash
# Service Name: scalable-ai-api-server-b
# Runtime: Python
# Build Command: pip install --upgrade pip && pip install -r requirements.txt
# Start Command: uvicorn scalable_ai_api.ai_server.render_app:app --host 0.0.0.0 --port $PORT
# Environment Variables:
#   SERVER_ID=Server B
#   LOG_LEVEL=INFO
```

## 🖥️ Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Individual Servers

#### Server A (Port 8080):
```bash
python server_a.py
```

#### Server B (Port 8081):
```bash
python server_b.py
```

#### Load Balancer (Port 8000):
```bash
uvicorn scalable_ai_api.load_balancer.render_app:app --host 0.0.0.0 --port 8000
```

### 3. Alternative Uvicorn Commands

#### Load Balancer with auto-reload:
```bash
uvicorn scalable_ai_api.load_balancer.render_app:app --reload --host 0.0.0.0 --port 8000
```

#### Server A with uvicorn:
```bash
SERVER_ID="Server A" uvicorn scalable_ai_api.ai_server.render_app:app --host 0.0.0.0 --port 8080
```

#### Server B with uvicorn:
```bash
SERVER_ID="Server B" uvicorn scalable_ai_api.ai_server.render_app:app --host 0.0.0.0 --port 8081
```

## 🧪 Testing Commands

### 1. Validate Setup
```bash
python validate_setup.py
```

### 2. Test Server A
```bash
python test_server_a.py
```

### 3. Test Server B
```bash
python test_server_b.py
```

### 4. Test Render Deployment
```bash
python test_render_deployment.py
```

### 5. Validate Task 2.4
```bash
python validate_task_2_4.py
```

### 6. Demo A/B Testing
```bash
python demo_ab_testing.py
```

### 7. Demo Load Balancer
```bash
python demo_load_balancer.py
```

## 🌐 Production URLs (After Render Deployment)

- **Load Balancer:** https://scalable-ai-api-load-balancer.onrender.com
- **Server A:** https://scalable-ai-api-server-a.onrender.com
- **Server B:** https://scalable-ai-api-server-b.onrender.com

## 📋 Health Check Endpoints

```bash
# Load Balancer Health
curl https://scalable-ai-api-load-balancer.onrender.com/health

# Server A Health
curl https://scalable-ai-api-server-a.onrender.com/health

# Server B Health
curl https://scalable-ai-api-server-b.onrender.com/health
```

## 🔧 Environment Variables for Render

### Load Balancer:
- `LOAD_BALANCER_PORT`: $PORT (auto-set by Render)
- `SERVER_A_URL`: https://scalable-ai-api-server-a.onrender.com
- `SERVER_B_URL`: https://scalable-ai-api-server-b.onrender.com
- `HEALTH_CHECK_INTERVAL`: 30
- `REQUEST_TIMEOUT`: 30
- `LOG_LEVEL`: INFO

### Server A & B:
- `SERVER_ID`: "Server A" or "Server B"
- `LOG_LEVEL`: INFO

## 🚀 Quick Deploy to Render

1. **Fork/Clone Repository:**
   ```bash
   git clone https://github.com/ThaiSang1402/DTDM-1.4.git
   cd DTDM-1.4
   ```

2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Connect your GitHub account
   - Select the repository
   - Render will auto-detect `render.yaml` and deploy all services

3. **Monitor Deployment:**
   - Check deployment logs in Render dashboard
   - Test endpoints once deployment completes

## 🔍 Troubleshooting

### Common Issues:
1. **Import Errors:** All relative imports have been converted to absolute imports
2. **Port Binding:** Use `0.0.0.0` host for Render compatibility
3. **Environment Variables:** Ensure all required env vars are set in Render dashboard

### Debug Commands:
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Test imports
python -c "import scalable_ai_api.load_balancer.render_app; print('Success')"

# Validate requirements
pip check
```