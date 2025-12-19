# Kubernetes Deployment

Kubernetes manifests for deploying the Arc brain tumor classification app:
- **Namespace:** Isolates Arc resources
- **Backend Deployment:** FastAPI backend (1 replica)
- **Backend Service:** NodePort service (port 30000)
- **AI Deployment:** AI training service (1 replica)
- **AI Service:** ClusterIP service for internal communication
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
kubectl get all -n arc

# Access the application
# Note: Backend may take a minute to load the ML model on first startup
# Be patient!

# Using minikube service (tested with Docker driver on macOS)
minikube service arc-backend -n arc
# This will open your browser automatically

# Or get the URL manually:
minikube service arc-backend -n arc --url
# Keep terminal open and access the URL in your browser
```

The app should now be running on Kubernetes and accessible through the URL provided by Minikube.

## Managing Pods

```shell
# Stop pods (scale deployment to 0 replicas)
kubectl scale deployment arc-backend -n arc --replicas=0
kubectl scale deployment arc-ai -n arc --replicas=0

# Restart pods (scale deployment back to 1 replica)
kubectl scale deployment arc-backend -n arc --replicas=1
kubectl scale deployment arc-ai -n arc --replicas=1

# Remove pods and restart from scratch
kubectl delete pods -n arc --all
# Kubernetes will automatically recreate them from the deployments

# Or delete specific pod
kubectl delete pod <pod-name> -n arc
```

## Troubleshooting

```shell
# Check pod status
kubectl get pods -n arc

# View pod logs
kubectl logs -n arc <pod-name>

# Describe pod for detailed information
kubectl describe pod -n arc <pod-name>
```

## Removing the Deployment

```shell
# Delete all resources
kubectl delete namespace arc

# Stop Minikube
minikube stop
```