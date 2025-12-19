#!/bin/bash
# scripts/deploy-k8s.sh
set -e

ENV=${1:-dev}
IMAGE_TAG=${2:-latest}

echo "🚀 Deploying to $ENV environment..."

# Build and push image
docker build -t your-registry/flask-backend:$IMAGE_TAG -f docker/Dockerfile .
docker push your-registry/flask-backend:$IMAGE_TAG

# Apply Kubernetes manifests
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/secret.yaml
kubectl apply -f k8s/base/pvc.yaml
kubectl apply -f k8s/base/deployment.yaml
kubectl apply -f k8s/base/service.yaml
kubectl apply -f k8s/base/hpa.yaml
kubectl apply -f k8s/base/serviceaccount.yaml

# Wait for rollout
kubectl rollout status deployment/flask-backend -n flask-app --timeout=300s

# Check resources
echo "📊 Deployment status:"
kubectl get all -n flask-app

echo "✅ Deployment completed!"