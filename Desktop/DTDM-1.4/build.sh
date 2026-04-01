#!/bin/bash
# Build script for Render deployment

echo "=== Render Build Script Starting ==="
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

echo "=== Installing dependencies ==="
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "=== Testing imports ==="
python -c "import sys; print('Python path:', sys.path)"
python -c "import scalable_ai_api; print('scalable_ai_api imported successfully')"
python -c "import scalable_ai_api.models; print('models imported successfully')"
python -c "import scalable_ai_api.interfaces; print('interfaces imported successfully')"
python -c "import scalable_ai_api.load_balancer.render_app; print('load_balancer.render_app imported successfully')"
python -c "import scalable_ai_api.ai_server.render_app; print('ai_server.render_app imported successfully')"

echo "=== Build completed successfully ==="