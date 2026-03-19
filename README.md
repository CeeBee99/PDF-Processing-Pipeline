# PDF Storage Service on Kubernetes

A containerized PDF upload and retrieval service deployed on Kubernetes, demonstrating core backend and infrastructure concepts including REST API design, containerization, persistent storage, and declarative deployment.

Users can upload, list, and download PDF files with data persistence guaranteed across pod restarts.

---

## Features

- Upload PDF files via REST API
- List and download stored PDFs
- Persistent storage using Kubernetes Volumes
- Containerized with Docker
- Declarative infrastructure via Kubernetes YAML manifests

---

## Architecture

```
Client (Browser / curl)
        ↓
   Kubernetes Service
        ↓
   FastAPI Pod
     ├── SQLite (metadata)
     └── /data (PDF storage)
```

---

## Components

| Component | Purpose |
|---|---|
| FastAPI Application | Handles HTTP requests and file operations |
| SQLite Database | Stores PDF metadata |
| PersistentVolumeClaim | Ensures storage survives pod restarts |
| Kubernetes Deployment | Manages application lifecycle and availability |
| Kubernetes Service | Provides stable internal network access |

---

## API Endpoints

### Upload a PDF
```
POST /upload
```
- Accepts: `multipart/form-data`
- Returns: uploaded filename

### List PDFs
```
GET /files
```
- Returns: array of filenames

### Download a PDF
```
GET /files/{filename}
```
- Returns: file stream

---

## Tech Stack

- Python 3 / FastAPI
- Docker
- Kubernetes (kind for local development)
- SQLite

---

## Getting Started

### Prerequisites
- Docker installed
- kind installed (`brew install kind` or equivalent)
- kubectl installed

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd pdf-server

# Build the Docker image
docker build -t pdf-api .

# Create a local Kubernetes cluster
kind create cluster

# Apply Kubernetes manifests
kubectl apply -f k8s/

# Port-forward to access the API locally
kubectl port-forward svc/pdf-service 8080:80
```

API available at `http://localhost:8080`

---

## Project Structure

```
pdf-server/
├── app/
│   └── main.py
├── Dockerfile
├── requirements.txt
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── pvc.yaml
└── README.md
```

---

## Design Decisions

**Separated storage concerns** — PDF binaries are stored on disk while metadata lives in SQLite. This keeps the architecture simple while reflecting real-world patterns for handling file-based workloads.

**Kubernetes for orchestration** — Using Deployments, Services, and PVCs demonstrates production-relevant infrastructure patterns even in a local development context.

**Simplicity first** — Single replica and SQLite keep the focus on core infrastructure concepts. PostgreSQL and multi-replica support are planned for future iterations.

---

## Roadmap

- [ ] Replace SQLite with PostgreSQL
- [ ] Add JWT authentication
- [ ] Build frontend UI
- [ ] Configure Ingress for domain-based routing
- [ ] Deploy to cloud or self-hosted Proxmox cluster

---

## What This Project Demonstrates

- Kubernetes core objects — Pods, Deployments, Services, PVCs
- Persistent storage design across container restarts
- Containerized application workflow with Docker
- REST API design with FastAPI
- Separation of concerns between application logic and infrastructure

---

## License

MIT
