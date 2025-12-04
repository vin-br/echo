# Project To-Do List

---

## FastAPI Backend

### Backend implementation

- [ ] Update the FastAPI backend to use the PyTorch model
	- [ ] Load the PyTorch model in the FastAPI app
	- [ ] Update the prediction logic to use PyTorch for inference
	- [ ] Test the FastAPI app to ensure predictions are working correctly with the PyTorch model

- [ ] Clean up and docs
	- [ ] Update `README.md` with new run commands
	- [ ] After FastAPI works, remove Django files

### Testing

- [ ] Write tests
	- [ ] Use `pytest`
	- [ ] Test: `GET /` returns 200; unknown path returns 404
	- [ ] Test: `POST` without file shows an error
	- [ ] Test the model for a fast prediction test

---

## SvelteKit Frontend

- [ ] Start using SveltekitKit while using the HTML/CSS/JS from the existing FastAPI templates
	- [ ] Set up SvelteKit project structure
	- [ ] Integrate existing HTML/CSS/JS into Svelte components
	- [ ] Ensure communication with FastAPI backend works correctly

---

## PyTorch Model

- [ ] Train and test more models to ensure comparable performance with the Keras model or even better performance
	- [ ] Experiment with different architectures
	- [ ] Tune hyperparameters (learning rate, batch size, epochs)
- [ ] Explore more plots and metrics to better evaluate the models

---

## DevOps

### Docker

- [ ] Create Dockerfile for FastAPI backend
- [ ] Create Dockerfile for SvelteKit frontend
- [ ] Create Dockerfile for PyTorch model training environment
- [ ] Set up Docker Compose to orchestrate all three services
- [ ] Test the entire setup locally using Docker Compose
- [ ] Document the Docker setup in the `README.md` file
- [ ] Push Docker images to Docker Hub

### Kubernetes

- [ ] Create Kubernetes manifests for deploying the FastAPI backend
- [ ] Create Kubernetes manifests for deploying the SvelteKit frontend
- [ ] Create Kubernetes manifests for deploying the PyTorch model training environment
- [ ] Set up Kubernetes cluster using Minikube