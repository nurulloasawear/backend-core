# Makefile
.PHONY: help build push deploy test clean

# Variables
APP_NAME = flask-backend
REGISTRY = your-registry
TAG = latest
NAMESPACE = flask-app
ENV = dev

help:
	@echo "Available targets:"
	@echo "  build     - Build Docker image"
	@echo "  push      - Push Docker image to registry"
	@echo "  deploy    - Deploy to Kubernetes"
	@echo "  test      - Run tests"
	@echo "  clean     - Clean up resources"

build:
	docker build -t $(REGISTRY)/$(APP_NAME):$(TAG) -f docker/Dockerfile .

push:
	docker push $(REGISTRY)/$(APP_NAME):$(TAG)

deploy:
	kubectl config use-context $(ENV)-cluster
	cd k8s/overlays/$(ENV) && kustomize edit set image flask-backend=$(REGISTRY)/$(APP_NAME):$(TAG)
	kustomize build k8s/overlays/$(ENV) | kubectl apply -f -
	kubectl rollout status deployment/$(APP_NAME) -n $(NAMESPACE) --timeout=300s

deploy-dev:
	$(MAKE) deploy ENV=dev

deploy-prod:
	$(MAKE) deploy ENV=prod

test:
	docker-compose -f docker/docker-compose.test.yml up --build --abort-on-container-exit

test-local:
	python -m pytest tests/ -v

logs:
	kubectl logs -f deployment/$(APP_NAME) -n $(NAMESPACE)

port-forward:
	kubectl port-forward svc/flask-service 8080:80 -n $(NAMESPACE)

clean:
	kubectl delete all --all -n $(NAMESPACE)
	kubectl delete pvc --all -n $(NAMESPACE)

setup-dev:
	minikube start --cpus=4 --memory=8192 --disk-size=20g
	minikube addons enable ingress
	minikube addons enable metrics-server
	minikube tunnel &

docker-run:
	docker-compose -f docker/docker-compose.yml up --build