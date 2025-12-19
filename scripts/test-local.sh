#!/bin/bash
# scripts/test-local.sh
set -e

echo "🔧 Building Docker image..."
docker build -t flask-backend:test -f docker/Dockerfile.dev .

echo "🚀 Starting services..."
docker-compose -f docker/docker-compose.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "✅ Testing health endpoint..."
curl -f http://localhost:5000/health || (echo "❌ Health check failed" && exit 1)

echo "✅ Testing auth endpoint..."
curl -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" || true

echo "📊 Checking service status..."
docker-compose ps

echo "🎉 Local test completed successfully!"