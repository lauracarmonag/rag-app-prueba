#!/bin/bash

# Activar entorno virtual
source venv/bin/activate

# Ejecutar comandos manteniendo el entorno virtual
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable containerregistry.googleapis.com

gcloud projects add-iam-policy-binding prueba-davivienda-2025 --member="user:lauracgz@gmail.com" --role="roles/owner"
gcloud projects add-iam-policy-binding prueba-davivienda-2025 --member="user:lauracgz@gmail.com" --role="roles/storage.admin"
gcloud projects add-iam-policy-binding prueba-davivienda-2025 --member="user:lauracgz@gmail.com" --role="roles/cloudbuild.builds.builder"

gcloud builds submit --tag gcr.io/prueba-davivienda-2025/rag-app --timeout=1800s