# PDF-Processing-Pipeline

A containerized PDF upload and retrieval service deployed on Kubernetes, demonstrating core backend and infrastructure concepts including REST API design, containerization, persistent storage, and declarative deployment.
Users can upload, list, and download PDF files with data persistence guaranteed across pod restarts.

Features

Upload PDF files via REST API
List and download stored PDFs
Persistent storage using Kubernetes Volumes
Containerized with Docker
Declarative infrastructure via Kubernetes YAML manifests

Architecture

Client (Browser / curl)
        ↓
   Kubernetes Service
        ↓
   FastAPI Pod
     ├── SQLite (metadata)
     └── /data (PDF storage)

Components
ComponentPurposeFastAPI ApplicationHandles HTTP requests and file operationsSQLite DatabaseStores PDF metadataPersistentVolumeClaimEnsures storage survives pod restartsKubernetes DeploymentManages application lifecycle and availabilityKubernetes ServiceProvides stable internal network access

