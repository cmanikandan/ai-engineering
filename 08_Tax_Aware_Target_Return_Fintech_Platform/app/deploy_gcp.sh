#!/usr/bin/env bash
# ============================================================================
# 1-Click Google Cloud Run Deployment for WealthPulse AI FinTech Platform
# ============================================================================

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null)}
REGION="us-central1"
SERVICE_NAME="wealthpulse-fintech-copilot"

if [ -z "$PROJECT_ID" ]; then
  echo "❌ Error: Google Cloud Project ID not set. Please set GOOGLE_CLOUD_PROJECT or run 'gcloud config set project YOUR_PROJECT_ID'"
  exit 1
fi

echo "🚀 Deploying WealthPulse AI to Google Cloud Run in project: $PROJECT_ID ($REGION)..."

# Enable Cloud Run & Cloud Build APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --project "$PROJECT_ID"

# Build & Deploy
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY",STATE_FILE_PATH="/tmp/state_db.json" \
  --project "$PROJECT_ID"

echo "✅ Deployment complete! WealthPulse AI is live on Cloud Run."
gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)' --project "$PROJECT_ID"
