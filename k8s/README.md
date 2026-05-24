# Kubernetes Deployment

Kubernetes manifests for deploying the Echo brain tumor classification app:
- **Namespace:** Isolates Echo resources
- **Backend Deployment:** FastAPI backend (1 replica)
- **Backend Service:** ClusterIP service for internal communication
- **Frontend Deployment:** SvelteKit frontend (1 replica)
- **Frontend Service:** ClusterIP service for internal communication
- **Nginx Deployment:** Reverse proxy routing traffic to frontend and backend
- **Nginx Service:** NodePort service (port 30080) — single entry point
- **Nginx ConfigMap:** Nginx configuration for upstream routing
- **PersistentVolume & PersistentVolumeClaim:** 5Gi storage for data persistence

## Prerequisites

Before you start:
- Make sure you have [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) installed on your machine
- Make sure you have [kubectl](https://kubernetes.io/docs/tasks/tools/) installed on your machine

## Installation

```shell
# Start Minikube
minikube start

# Apply manifests (namespace first, then the rest)
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/

# Check deployment status
kubectl get all -n echo

# Access the application
# Note: Backend may take a minute to load the ML model on first startup
# Be patient!

# Using minikube service (tested with Docker driver on macOS)
minikube service echo-nginx -n echo
# This will open your browser automatically

# Or get the URL manually:
minikube service echo-nginx -n echo --url
# Keep terminal open and access the URL in your browser
```

The app should now be running on Kubernetes and accessible through the URL provided by Minikube.

## Managing Pods

```shell
# Stop pods (scale deployment to 0 replicas)
kubectl scale deployment echo-backend -n echo --replicas=0
kubectl scale deployment echo-frontend -n echo --replicas=0
kubectl scale deployment echo-nginx -n echo --replicas=0

# Restart pods (scale deployment back to 1 replica)
kubectl scale deployment echo-backend -n echo --replicas=1
kubectl scale deployment echo-frontend -n echo --replicas=1
kubectl scale deployment echo-nginx -n echo --replicas=1

# Remove pods and restart from scratch
kubectl delete pods -n echo --all
# Kubernetes will automatically recreate them from the deployments

# Or delete specific pod
kubectl delete pod <pod-name> -n echo
```

## Troubleshooting

```shell
# Check pod status
kubectl get pods -n echo

# View pod logs
kubectl logs -n echo <pod-name>

# Describe pod for detailed information
kubectl describe pod -n echo <pod-name>
```

## Removing the Deployment

```shell
# Delete all resources
kubectl delete namespace echo

# Stop Minikube
minikube stop
```