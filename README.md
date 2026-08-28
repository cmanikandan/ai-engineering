# 🚀 Applied AI Engineering Masterclass: Building Enterprise AI Systems with Google Gemini & Google Cloud

[![Google GenAI SDK](https://img.shields.io/badge/SDK-google--genai%20v1.0+-blue.svg)](https://github.com/googleapis/python-genai)
[![Models](https://img.shields.io/badge/Models-Gemini%202.5%20%7C%20Gemini%203.7%20%7C%20Imagen%203-orange.svg)](https://ai.google.dev)
[![Deployment](https://img.shields.io/badge/Cloud-Google%20Cloud%20Run-blue.svg)](https://cloud.google.com/run)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

> **Welcome, Future Applied AI Engineer!** 👋  
> Whether you are a software engineer stepping into AI, a data scientist wanting to build real-world software, or a complete beginner to Large Language Models (LLMs), this course is designed for you. We take complex research topics—like Transformers, RAG, AI Agents, Reasoning Models, and Diffusion—and break them down into **crystal-clear mental models**, **visual illustrations**, **micro-examples**, and **production-ready code**.

---

## 🌟 What is an "Applied AI Engineer"?

In traditional software, we write deterministic code (`if / else`). In ML Research, scientists train raw foundation models on supercomputers. **Applied AI Engineering** is the practical bridge:

<div style="background-color: #0d1117; padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin: 15px 0;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 180" width="100%" height="100%">
  <rect width="850" height="180" fill="#0d1117" rx="8" />

  <!-- Box 1: Researcher -->
  <rect x="20" y="20" width="240" height="140" rx="8" fill="#161b22" stroke="#8b949e" stroke-width="1.5" />
  <text x="35" y="48" fill="#c9d1d9" font-family="sans-serif" font-size="13" font-weight="bold">🔬 ML / AI Researcher</text>
  <text x="35" y="75" fill="#8b949e" font-family="sans-serif" font-size="11">• Trains base foundation models</text>
  <text x="35" y="95" fill="#8b949e" font-family="sans-serif" font-size="11">• Manages 10,000 GPU clusters</text>
  <text x="35" y="115" fill="#8b949e" font-family="sans-serif" font-size="11">• Optimizes mathematical loss</text>
  <text x="35" y="140" fill="#58a6ff" font-family="sans-serif" font-size="10">Focus: Training Compute</text>

  <!-- Arrow 1 -->
  <path d="M 265 90 L 295 90" stroke="#388bfd" stroke-width="2" />
  <polygon points="295,85 305,90 295,95" fill="#388bfd" />

  <!-- Box 2: Applied AI Engineer (YOU) -->
  <rect x="310" y="15" width="250" height="150" rx="8" fill="#161b22" stroke="#3fb950" stroke-width="2.5" />
  <rect x="320" y="25" width="130" height="22" rx="4" fill="#238636" />
  <text x="385" y="40" fill="#ffffff" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">PRIMARY FOCUS</text>
  <text x="325" y="68" fill="#3fb950" font-family="sans-serif" font-size="13" font-weight="bold">⚡ Applied AI Engineer (YOU)</text>
  <text x="325" y="90" fill="#f0f6fc" font-family="sans-serif" font-size="11">• Builds reliable software with LLMs</text>
  <text x="325" y="110" fill="#f0f6fc" font-family="sans-serif" font-size="11">• Implements RAG, Agents &amp; Tools</text>
  <text x="325" y="130" fill="#f0f6fc" font-family="sans-serif" font-size="11">• Deploys scalable APIs on Cloud Run</text>
  <text x="325" y="152" fill="#3fb950" font-family="sans-serif" font-size="10" font-weight="bold">Goal: Enterprise Value &amp; Reliability</text>

  <!-- Arrow 2 -->
  <path d="M 565 90 L 595 90" stroke="#388bfd" stroke-width="2" />
  <polygon points="595,85 605,90 595,95" fill="#388bfd" />

  <!-- Box 3: End Users & Business -->
  <rect x="610" y="20" width="220" height="140" rx="8" fill="#161b22" stroke="#d29922" stroke-width="1.5" />
  <text x="625" y="48" fill="#d29922" font-family="sans-serif" font-size="13" font-weight="bold">👥 Business &amp; End Users</text>
  <text x="625" y="75" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Instant, accurate responses</text>
  <text x="625" y="95" fill="#c9d1d9" font-family="sans-serif" font-size="11">• SRE automated triage</text>
  <text x="625" y="115" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Enterprise compliance &amp; safety</text>
  <text x="625" y="140" fill="#3fb950" font-family="sans-serif" font-size="10">Outcome: High ROI</text>
</svg>
</div>

| Role | Primary Toolset | Focus | Goal |
| :--- | :--- | :--- | :--- |
| **Software Engineer** | Python, TypeScript, APIs, SQL | Deterministic business logic | Fast, bug-free applications |
| **AI Researcher** | PyTorch, CUDA, JAX, Distributed Training | Foundation model architectures | Training loss & academic benchmarks |
| **Applied AI Engineer (This Course)** | `google-genai` SDK, Vector DBs, Cloud Run, Pydantic | Steering, grounding, tool use & orchestrating LLMs | Intelligent, production-ready enterprise systems |

---

## 🏛️ Master Curriculum & System Architecture

<div style="background-color: #0d1117; padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin: 15px 0;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 620" width="100%" height="100%">
  <!-- Background -->
  <rect width="900" height="620" fill="#0d1117" rx="10" />

  <!-- Top Banner -->
  <rect x="25" y="20" width="850" height="50" rx="8" fill="#161b22" stroke="#388bfd" stroke-width="1.5" />
  <text x="450" y="52" fill="#58a6ff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto" font-size="16" font-weight="bold" text-anchor="middle">APPLIED AI ENGINEERING MASTERCLASS ARCHITECTURE</text>

  <!-- Row 1: Modules 1, 2, 3 -->
  <!-- Module 1 -->
  <rect x="25" y="90" width="270" height="150" rx="8" fill="#161b22" stroke="#238636" stroke-width="2" />
  <rect x="35" y="100" width="100" height="24" rx="4" fill="#238636" />
  <text x="85" y="116" fill="#ffffff" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">MODULE 01</text>
  <text x="35" y="145" fill="#3fb950" font-family="sans-serif" font-size="13" font-weight="bold">Core Foundations &amp; Studio</text>
  <text x="35" y="168" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Autoregressive Next-Token BPE</text>
  <text x="35" y="188" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Temperature &amp; Top-p Sampling</text>
  <text x="35" y="208" fill="#c9d1d9" font-family="sans-serif" font-size="11">• SFT, DPO &amp; GRPO Alignment</text>
  <text x="35" y="228" fill="#8b949e" font-family="sans-serif" font-size="11">🛠️ Interactive AI Studio</text>

  <!-- Module 2 -->
  <rect x="315" y="90" width="270" height="150" rx="8" fill="#161b22" stroke="#388bfd" stroke-width="2" />
  <rect x="325" y="100" width="100" height="24" rx="4" fill="#1f6feb" />
  <text x="375" y="116" fill="#ffffff" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">MODULE 02</text>
  <text x="325" y="145" fill="#58a6ff" font-family="sans-serif" font-size="13" font-weight="bold">Enterprise Knowledge RAG</text>
  <text x="325" y="168" fill="#c9d1d9" font-family="sans-serif" font-size="11">• text-embedding-004 Dense</text>
  <text x="325" y="188" fill="#c9d1d9" font-family="sans-serif" font-size="11">• BM25 Sparse Keyword Index</text>
  <text x="325" y="208" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Reciprocal Rank Fusion (RRF)</text>
  <text x="325" y="228" fill="#8b949e" font-family="sans-serif" font-size="11">🛠️ Grounded Knowledge Assistant</text>

  <!-- Module 3 -->
  <rect x="605" y="90" width="270" height="150" rx="8" fill="#161b22" stroke="#d29922" stroke-width="2" />
  <rect x="615" y="100" width="100" height="24" rx="4" fill="#9e6a03" />
  <text x="665" y="116" fill="#ffffff" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">MODULE 03</text>
  <text x="615" y="145" fill="#e3b341" font-family="sans-serif" font-size="13" font-weight="bold">Agentic Web Research</text>
  <text x="615" y="168" fill="#c9d1d9" font-family="sans-serif" font-size="11">• ReAct Loops &amp; Self-Correction</text>
  <text x="615" y="188" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Native Gemini Tool Calling</text>
  <text x="615" y="208" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Model Context Protocol (MCP)</text>
  <text x="615" y="228" fill="#8b949e" font-family="sans-serif" font-size="11">🛠️ Autonomous Research Agent</text>

  <!-- Row 2: Modules 4, 5, 6 -->
  <!-- Module 4 -->
  <rect x="25" y="260" width="270" height="150" rx="8" fill="#161b22" stroke="#a371f7" stroke-width="2" />
  <rect x="35" y="270" width="100" height="24" rx="4" fill="#8957e5" />
  <text x="85" y="286" fill="#ffffff" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">MODULE 04</text>
  <text x="35" y="315" fill="#bc8cff" font-family="sans-serif" font-size="13" font-weight="bold">Cognitive Deep Research</text>
  <text x="35" y="338" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Gemini Thinking Budget CoT</text>
  <text x="35" y="358" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Best-of-N &amp; Tree of Thoughts</text>
  <text x="35" y="378" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Recursive Tree Exploration</text>
  <text x="35" y="398" fill="#8b949e" font-family="sans-serif" font-size="11">🛠️ Deep Research Engine</text>

  <!-- Module 5 -->
  <rect x="315" y="260" width="270" height="150" rx="8" fill="#161b22" stroke="#f85149" stroke-width="2" />
  <rect x="325" y="270" width="100" height="24" rx="4" fill="#da3633" />
  <text x="375" y="286" fill="#ffffff" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">MODULE 05</text>
  <text x="325" y="315" fill="#ff7b72" font-family="sans-serif" font-size="13" font-weight="bold">Multimodal Media Studio</text>
  <text x="325" y="338" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Diffusion Denoising Mechanics</text>
  <text x="325" y="358" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Gemini 2.5 Flash Vision QA</text>
  <text x="325" y="378" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Google Imagen 3 Synthesis</text>
  <text x="325" y="398" fill="#8b949e" font-family="sans-serif" font-size="11">🛠️ Creative Campaign Studio</text>

  <!-- Module 6 -->
  <rect x="605" y="260" width="270" height="150" rx="8" fill="#161b22" stroke="#2ea043" stroke-width="2" />
  <rect x="615" y="270" width="100" height="24" rx="4" fill="#238636" />
  <text x="665" y="286" fill="#ffffff" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle">MODULE 06</text>
  <text x="615" y="315" fill="#3fb950" font-family="sans-serif" font-size="13" font-weight="bold">Tokenomics &amp; LLM Gateway</text>
  <text x="615" y="338" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Input/Output/Cached Economics</text>
  <text x="615" y="358" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Gemini Context Caching (75% off)</text>
  <text x="615" y="378" fill="#c9d1d9" font-family="sans-serif" font-size="11">• Dynamic 3-Tier Model Router</text>
  <text x="615" y="398" fill="#8b949e" font-family="sans-serif" font-size="11">🛠️ Enterprise Router with Fallbacks</text>

  <!-- Capstone Module 7 Banner -->
  <rect x="25" y="430" width="850" height="160" rx="8" fill="#161b22" stroke="#a371f7" stroke-width="2.5" />
  <rect x="35" y="442" width="170" height="26" rx="4" fill="#8957e5" />
  <text x="120" y="460" fill="#ffffff" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">MODULE 07 (CAPSTONE)</text>
  <text x="220" y="461" fill="#bc8cff" font-family="sans-serif" font-size="15" font-weight="bold">OmniOps AI: Autonomous Multimodal Incident SRE Platform</text>
  
  <rect x="45" y="480" width="245" height="95" rx="6" fill="#21262d" />
  <text x="55" y="502" fill="#58a6ff" font-family="sans-serif" font-size="12" font-weight="bold">🔍 Incident Ingestion &amp; RAG</text>
  <text x="55" y="522" fill="#8b949e" font-family="sans-serif" font-size="11">• Grafana dashboard vision triage</text>
  <text x="55" y="540" fill="#8b949e" font-family="sans-serif" font-size="11">• Hybrid Runbook ChromaDB KB</text>
  <text x="55" y="558" fill="#8b949e" font-family="sans-serif" font-size="11">• Automated SLA credit calculation</text>

  <rect x="310" y="480" width="270" height="95" rx="6" fill="#21262d" />
  <text x="320" y="502" fill="#3fb950" font-family="sans-serif" font-size="12" font-weight="bold">🧠 Thinking &amp; ReAct Remediation</text>
  <text x="320" y="522" fill="#8b949e" font-family="sans-serif" font-size="11">• Gemini Thinking root-cause RCA</text>
  <text x="320" y="540" fill="#8b949e" font-family="sans-serif" font-size="11">• Automated Cloud Run scale tools</text>
  <text x="320" y="558" fill="#8b949e" font-family="sans-serif" font-size="11">• Multi-agent FinOps budget gate</text>

  <rect x="600" y="480" width="260" height="95" rx="6" fill="#21262d" />
  <text x="610" y="502" fill="#e3b341" font-family="sans-serif" font-size="12" font-weight="bold">☁️ Cloud Run Production Deploy</text>
  <text x="610" y="522" fill="#8b949e" font-family="sans-serif" font-size="11">• Containerized FastAPI service</text>
  <text x="610" y="540" fill="#8b949e" font-family="sans-serif" font-size="11">• Imagen 3 topology generation</text>
  <text x="610" y="558" fill="#8b949e" font-family="sans-serif" font-size="11">• Single-command bash deploy</text>
</svg>
</div>

---

## 📁 Repository Index & Notebook Links

| Module | Notebook Link | Core Capabilities Mastered |
| :--- | :--- | :--- |
| **01. Core Foundations** | [`01_LLM_Foundations_Interactive_Playground.ipynb`](./01_LLM_Foundations_Interactive_Playground/01_LLM_Foundations_Interactive_Playground.ipynb) | Next-token prediction, BPE tokenization, Temperature/Top-p sampling dials, Post-training (SFT, DPO, GRPO), and an **interactive streaming AI studio**. |
| **02. Knowledge RAG** | [`02_Enterprise_RAG_Knowledge_Assistant.ipynb`](./02_Enterprise_RAG_Knowledge_Assistant/02_Enterprise_RAG_Knowledge_Assistant.ipynb) | Embeddings (`text-embedding-004`), semantic chunking, dense + sparse BM25 hybrid search via Reciprocal Rank Fusion (RRF), and a **grounded knowledge assistant**. |
| **03. Agentic Workflows** | [`03_Agentic_Workflows_Web_Search_Agent.ipynb`](./03_Agentic_Workflows_Web_Search_Agent/03_Agentic_Workflows_Web_Search_Agent.ipynb) | Agency spectrum, workflow patterns (Routing, Reflection, Parallelism), native Gemini tool calling, Model Context Protocol (MCP), and an **autonomous research agent**. |
| **04. Cognitive Reasoning**| [`04_Reasoning_Models_Deep_Research_Engine.ipynb`](./04_Reasoning_Models_Deep_Research_Engine/04_Reasoning_Models_Deep_Research_Engine.ipynb) | System 1 vs System 2 thinking, Gemini Thinking tokens (`thinking_budget`), test-time compute scaling (Best-of-N, Tree-of-Thoughts), and an **autonomous Deep Research engine**. |
| **05. Multimodal Vision** | [`05_Multimodal_Vision_Media_Synthesis_Agent.ipynb`](./05_Multimodal_Vision_Media_Synthesis_Agent/05_Multimodal_Vision_Media_Synthesis_Agent.ipynb) | Diffusion denoising mechanics, visual inspection with Gemini 2.5 Flash, photorealistic image synthesis with **Google Imagen 3**, and a **creative campaign studio**. |
| **06. Tokenomics & Gateway** | [`06_Tokenomics_Cost_Optimization_LLM_Gateway.ipynb`](./06_Tokenomics_Cost_Optimization_LLM_Gateway/06_Tokenomics_Cost_Optimization_LLM_Gateway.ipynb) | Input/Output/Cached token economics, Gemini Context Caching (75-90% off), Dynamic 3-Tier Model Router (Flash Lite vs Flash vs Pro), fallback cascades, and live cost telemetry. |
| **07. Capstone SRE** | [`07_Capstone_OmniOps_Autonomous_SRE_Platform.ipynb`](./07_Capstone_OmniOps_Autonomous_SRE_Platform/07_Capstone_OmniOps_Autonomous_SRE_Platform.ipynb) | The Grand Finale: **OmniOps AI**, an autonomous incident triage platform uniting RAG + Vision + Thinking + Tools, packaged as a **FastAPI backend** on **Google Cloud Run**. |

---

## ⚡ Quickstart: Get Running in 3 Minutes

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-org/ai-engineering-masterclass.git
cd ai-engineering-masterclass
```

### Step 2: Set Up a Python Environment
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Choose Your Authentication Method

#### 🌟 Option A: Google AI Studio API Key (Easiest & Free)
Get your free API key at [aistudio.google.com](https://aistudio.google.com/):
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

#### 🏢 Option B: Google Cloud Vertex AI (Enterprise)
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

### Step 4: Launch Jupyter
```bash
jupyter lab
```
Open any of the 7 module folders and dive in!

---

## 💡 How Each Notebook Is Structured

To ensure you never feel lost or overwhelmed, every single notebook follows a consistent, friendly **5-tier learning structure**:

1. **💡 Intuition in Plain English (ELI5)**: Simple real-world analogies (e.g. comparing temperature to ordering coffee; embeddings to a GPS map; RAG to open-book exams).
2. **🎨 Visual Mental Model Diagrams**: Clear enterprise architecture flowcharts showing exactly how data moves through the system.
3. **⚡ The 30-Second Micro-Example**: Minimal 3-5 lines of code so you see the core idea working immediately.
4. **🔍 Under the Hood**: Demystifying the math, architecture, and engineering principles step-by-step without intimidating academic jargon.
5. **🎯 Hands-On Exercises & Complete Solutions**: Step-by-step challenges with starter code, helpful hints, and verified production solutions.

---

## ☁️ Capstone Deployment: Google Cloud Run

In Module 7, you will deploy the full OmniOps incident engine as a serverless container on **Google Cloud Run**:

```bash
cd 07_Capstone_OmniOps_Autonomous_SRE_Platform
./deploy_cloud_run.sh
```

### Test Your Live Cloud Microservice:
```bash
# 1. Health Check
curl -X GET "https://<YOUR_SERVICE_URL>/healthz"

# 2. Automated SRE Incident Triage
curl -X POST "https://<YOUR_SERVICE_URL>/api/v1/triage" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "payment-gateway",
    "telemetry_summary": "High latency spike with 503 error rate reaching 14%.",
    "error_code": "HTTP 503"
  }'
```

---

## 📚 Essential Applied AI Engineering Glossary for Freshers

| Term | What It Means in Plain English |
| :--- | :--- |
| **Token** | A piece of a word (roughly 4 characters or 0.75 words). Models read and write in tokens, not letters. |
| **Temperature** | The "creativity dial" ($0.0$ = strict and factual; $1.0$ = creative and varied). |
| **Prompt** | The text instruction you provide to the model. |
| **Context Window** | The maximum number of tokens (memory) the model can read in a single conversation. |
| **Embedding** | A list of numbers (vector) representing the *meaning* of a piece of text. |
| **Vector DB** | A database that searches by *concept similarity* rather than exact keyword matches. |
| **RAG** | Retrieval-Augmented Generation: Giving the model relevant documents before asking it to answer. |
| **Agent** | An LLM connected to external tools (like search, calculators, databases) that can take actions. |
| **Thinking Tokens** | Hidden reasoning scratchpad tokens generated by models like Gemini 2.5/3.7 before giving the final answer. |
| **Diffusion** | An AI technique that turns random visual noise into high-resolution images and videos. |

---

## 📄 License & Community
Authored with love for the next generation of Applied AI Engineers. Licensed under the [Apache License 2.0](LICENSE).  
Happy building! 🚀
