#!/usr/bin/env bash
# =============================================================================
# Google Cloud Run Automated Deployment Script for OmniOps AI Microservice
# =============================================================================
set -e

SERVICE_NAME="omniops-enterprise-agent"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
PROJECT_ID="$(gcloud config get-value project 2>/dev/null || echo '')"

if [ -z "$PROJECT_ID" ]; then
  echo "❌ Error: Google Cloud Project ID is not set. Run: gcloud config set project <PROJECT_ID>"
  exit 1
fi

echo "🚀 Deploying ${SERVICE_NAME} to Google Cloud Run in project: ${PROJECT_ID} (${REGION})..."

# Enable required Google Cloud APIs
gcloud services enable run.googleapis.com \
                       artifactregistry.googleapis.com \
                       aiplatform.googleapis.com \
                       secretmanager.googleapis.com \
                       --project="${PROJECT_ID}"

# Deploy container directly from source directory
gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --concurrency 80 \
  --timeout 300 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION}"

echo "✅ Deployment complete! Fetching service URL..."
SERVICE_URL="$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --project ${PROJECT_ID} --format 'value(status.url)')"
echo "🌐 OmniOps Live Endpoint: ${SERVICE_URL}"
echo "🔍 Health Check: curl ${SERVICE_URL}/healthz"
