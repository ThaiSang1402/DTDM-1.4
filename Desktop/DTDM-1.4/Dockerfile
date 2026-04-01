# Dockerfile for Render deployment (backup option)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["uvicorn", "scalable_ai_api.load_balancer.render_app:app", "--host", "0.0.0.0", "--port", "8000"]