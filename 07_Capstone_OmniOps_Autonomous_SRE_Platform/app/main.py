"""
OmniOps AI - Enterprise SRE Incident Orchestration & Multimodal Platform
Production FastAPI Microservice for Google Cloud Run Deployment
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
import chromadb
from rank_bm25 import BM25Okapi
import io
from PIL import Image

app = FastAPI(
    title="OmniOps AI - Enterprise SRE Orchestrator",
    description="Autonomous Multimodal AI Agent for Enterprise Incident Triage and Cloud Run Operations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Google GenAI Client Initialization
# -----------------------------------------------------------------------------
def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "sandbox-project")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    return genai.Client(vertexai=True, project=project, location=location)

client = get_client()

# -----------------------------------------------------------------------------
# In-Memory Runbook Knowledge Base
# -----------------------------------------------------------------------------
RUNBOOKS = [
    {
        "id": "RB-301",
        "title": "Cloud Run Memory OOM & Traffic Spikes",
        "content": "When Cloud Run instances encounter HTTP 503 or SIGKILL error codes during high concurrency (>80 requests/instance), immediately increase memory limit from 512Mi to 2Gi and raise max-instances to 200 via gcloud run services update. Verify database connection pool limits on Cloud SQL."
    },
    {
        "id": "RB-302",
        "title": "PostgreSQL Connection Exhaustion Mitigation",
        "content": "If database connection pool utilization exceeds 95% and queries queue up, deploy PgBouncer connection pooling sidecar or scale Cloud SQL read replicas. Force drain idle connections using pg_terminate_backend."
    },
    {
        "id": "RB-303",
        "title": "Zero-Trust Identity Token Expiration on Service Mesh",
        "content": "If inter-service RPC calls fail with HTTP 401 Unauthorized, verify that the caller service account possesses roles/run.invoker and that the OpenID Connect (OIDC) token is being refreshed before its 60-minute TTL expiry."
    }
]

chroma_client = chromadb.Client()
try:
    chroma_client.delete_collection("omniops_kb")
except Exception:
    pass
kb_collection = chroma_client.create_collection("omniops_kb", metadata={"hnsw:space": "cosine"})

corpus = [f"{r['title']}: {r['content']}" for r in RUNBOOKS]
bm25 = BM25Okapi([t.lower().split() for t in corpus])

# Embed corpus
emb_resp = client.models.embed_content(model="text-embedding-004", contents=corpus)
kb_collection.add(
    ids=[r["id"] for r in RUNBOOKS],
    embeddings=[e.values for e in emb_resp.embeddings],
    documents=corpus,
    metadatas=[{"title": r["title"]} for r in RUNBOOKS]
)

# -----------------------------------------------------------------------------
# Data Models & Schemas
# -----------------------------------------------------------------------------
class IncidentTriageRequest(BaseModel):
    service_name: str
    telemetry_summary: str
    error_code: Optional[str] = "HTTP 503"

class IncidentReport(BaseModel):
    service_name: str
    severity: str
    root_cause_analysis: str
    remediation_actions_taken: List[str]
    sla_impact_assessment: str
    preventative_measures: List[str]

# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------
@app.get("/healthz")
def health_check():
    return {"status": "healthy", "service": "omniops-enterprise-agent", "version": "1.0.0"}

@app.post("/api/v1/triage", response_model=IncidentReport)
async def triage_incident(request: IncidentTriageRequest):
    """Executes full autonomous triage, runbook retrieval, and SRE postmortem synthesis."""
    try:
        # 1. RAG Search
        q_emb = client.models.embed_content(model="text-embedding-004", contents=request.telemetry_summary).embeddings[0].values
        v_res = kb_collection.query(query_embeddings=[q_emb], n_results=2)["ids"][0]
        matched_rbs = [r for r in RUNBOOKS if r["id"] in v_res]
        rb_context = "\n\n".join([f"[{r['id']}] {r['title']}: {r['content']}" for r in matched_rbs])

        # 2. Synthesis with Gemini Thinking
        prompt = f"""
You are the Lead Principal SRE at Google Cloud.
Analyze this production outage and generate a complete incident report:

SERVICE: {request.service_name}
TELEMETRY: {request.telemetry_summary}
ERROR CODE: {request.error_code}

RUNBOOK CONTEXT:
{rb_context}

Execute simulated remediation: scale Cloud Run memory to 2Gi and instances to 200.
"""
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=IncidentReport,
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=2048)
            )
        )
        return IncidentReport.model_validate_json(resp.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage execution failed: {str(e)}")

@app.post("/api/v1/multimodal-triage")
async def multimodal_triage(
    service_name: str = Form(...),
    chart_image: UploadFile = File(...)
):
    """Ingests live Grafana screenshot image and performs multimodal visual anomaly triage."""
    try:
        contents = await chart_image.read()
        pil_img = Image.open(io.BytesIO(contents))
        
        prompt = f"""
Analyze this telemetry graph for service '{service_name}'.
Identify:
1. Exact timestamp of spike
2. Peak CPU and 503 error rates
3. Recommended remediation steps
"""
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[pil_img, prompt],
            config=types.GenerateContentConfig(temperature=0.0)
        )
        return {
            "service": service_name,
            "visual_analysis": resp.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multimodal inspection failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
