# AGENTS.md — AI Engineering & Agentic Architecture Guide

This document defines the architectural standards, official Gemini model routing matrix, MCP server contracts, coding conventions, and operational workflows for autonomous AI coding agents and engineers working inside the **[`cmanikandan/ai-engineering`](https://github.com/cmanikandan/ai-engineering)** repository.

---

## 1. Repository Overview & Module Topology

This repository is an end-to-end **Production AI Engineering Curriculum & Reference Architecture** built natively on the **Google GenAI SDK (`google-genai` v2.3+)**, **Model Context Protocol (MCP)**, **FastAPI**, and **Google Cloud Run**.

| Module | Directory | Primary Agentic / Engineering Pattern | Core Models Used |
| :--- | :--- | :--- | :--- |
| **01** | [`01_LLM_Foundations_Interactive_Playground/`](01_LLM_Foundations_Interactive_Playground/) | Tokenization, Sampling Physics, Context Caching, Structured Outputs (Pydantic), Function Calling | `gemini-3.8-flash` |
| **02** | [`02_Enterprise_RAG_Knowledge_Assistant/`](02_Enterprise_RAG_Knowledge_Assistant/) | Hybrid Search (Dense `gemini-embedding-2` + BM25 + RRF), Corrective RAG (CRAG), Self-RAG Grading | `gemini-embedding-2`, `gemini-3.8-flash` |
| **03** | [`03_Agentic_Workflows_Web_Search_Agent/`](03_Agentic_Workflows_Web_Search_Agent/) | ReAct Loop, Plan-and-Execute DAGs, Multi-Agent Supervisor, Native FastMCP Server Integration | `gemini-3.8-flash`, `gemini-3.1-pro-preview` |
| **04** | [`04_Reasoning_Models_Deep_Research_Engine/`](04_Reasoning_Models_Deep_Research_Engine/) | Reasoning Tokens (`ThinkingConfig`), Tree-of-Thoughts (ToT), Iterative Deep Research Agent | `gemini-3.8-flash`, `gemini-3.1-pro-preview` |
| **05** | [`05_Multimodal_Vision_Media_Synthesis_Agent/`](05_Multimodal_Vision_Media_Synthesis_Agent/) | Native Multimodal (Video/Audio/PDF), Nano Banana Image Gen (`gemini-3-pro-image`), Omni 1.1 Flash Video, WebSocket Live API | `gemini-3.8-flash`, `gemini-3-pro-image`, `gemini-3.1-flash-image`, `gemini-omni-1.1-flash` |
| **06** | [`06_Tokenomics_Cost_Optimization_LLM_Gateway/`](06_Tokenomics_Cost_Optimization_LLM_Gateway/) | 3-Tier Semantic Router, Prompt-Injection Guardrails, LLM-as-a-Judge Evaluation, FinOps Telemetry | `gemini-3.5-flash-lite`, `gemini-3.8-flash`, `gemini-3.1-pro-preview`, `gemini-embedding-2` |
| **07** | [`07_Capstone_OmniOps_Autonomous_SRE_Platform/`](07_Capstone_OmniOps_Autonomous_SRE_Platform/) | **OmniOps SRE**: Autonomous Incident Triage, Hybrid Runbook RAG, FastMCP Diagnostics, Cloud Run Microservice | `gemini-3.8-flash`, `gemini-embedding-2` |
| **08** | [`08_Tax_Aware_Target_Return_Fintech_Platform/`](08_Tax_Aware_Target_Return_Fintech_Platform/) | **Tax-Aware FinTech**: Tax Hurdle Calculator, Intraday Engine, DhanHQ + Zerodha Kite + Razorpay MCP Servers, SEBI Guardrails | `gemini-3.8-flash`, `gemini-3.1-pro-preview` |

---

## 2. Official Gemini Model Matrix & Deprecation Rules

All code, notebooks, FastAPI microservices, and SVG/PNG architectural diagrams **MUST** strictly use the current official Google Gemini models via `from google import genai`.

### 2.1 Active Model Routing Matrix

| Tier / Capability | Official Model ID | Target Use Cases in Repository |
| :--- | :--- | :--- |
| **Tier 1: High-Speed / Cost-Optimized Lite** | `gemini-3.5-flash-lite` | Guardrail classification, PII scrubbing, simple intent routing, high-volume extraction (Module 06 Tier-1 Router). |
| **Tier 2: Default Agentic & Multimodal Workhorse** | `gemini-3.8-flash` | ReAct tool-calling loops, RAG synthesis, CRAG/Self-RAG grading, Live API streaming, OmniOps SRE & WealthPulse copilot chat. |
| **Tier 3: Frontier Reasoning & Planning** | `gemini-3.1-pro-preview` | Deep architectural synthesis, multi-step financial/tax optimization, complex root-cause analysis, LLM-as-a-Judge evaluation. |
| **Dense Semantic Embeddings** | `gemini-embedding-2` | Vector indexing, hybrid search (Dense + BM25), semantic cache lookup (`client.models.embed_content`). |
| **Image Generation & Editing (Nano Banana)** | `gemini-3-pro-image` / `gemini-3.1-flash-image` | Studio-quality visual asset generation and conversational image editing via `generate_content` with `response_modalities=["IMAGE"]`. |
| **Generative Video & Audio** | `gemini-omni-1.1-flash` | Text-to-video, frame-to-video, and multimodal video synthesis (`client.models.generate_videos`). |
| **Speech-to-Text & Text-to-Speech** | `gemini-3.5-transcribe` / `gemini-3.1-flash-tts-preview` | Dedicated audio transcription and low-latency neural speech synthesis. |

### 2.2 Strictly Prohibited / Deprecated Models

Agents **MUST NEVER** introduce or revert to any of the following legacy or shut-down model identifiers:
- ❌ `google-generativeai` (legacy SDK package — always use `google-genai`)
- ❌ `gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`, `gemini-2.7-*`
- ❌ `gemini-3.7-flash`, `gemini-3.7-thinking`, `gemini-3.1-flash-lite`, `gemini-3-pro-preview`
- ❌ `text-embedding-004` (shut down — always use `gemini-embedding-2`)
- ❌ `imagen-3.0-generate-002` or `gemini-3-pro-image-preview` (always use `gemini-3-pro-image` or `gemini-3.1-flash-image` with `generate_content`)

---

## 3. SDK & Coding Conventions for AI Agents

### 3.1 Client Initialization & Fallback Resiliency
All Python services and notebooks must initialize the unified `genai.Client()` and gracefully support offline/deterministic simulation when `GEMINI_API_KEY` is not set in CI/CD or local test environments:

```python
import os
from google import genai
from google.genai import types

client = genai.Client()  # Reads GEMINI_API_KEY from environment
```

### 3.2 Structured Outputs & Thinking Configuration
When enforcing JSON schemas or tuning reasoning budgets:
```python
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=MyPydanticSchema,
        thinking_config=types.ThinkingConfig(thinking_budget=1024),
        temperature=0.1,
    ),
)
```

### 3.3 Image Generation (Nano Banana Pro / Nano Banana 2)
Always use `client.models.generate_content` with `response_modalities=["IMAGE"]` (or `["TEXT", "IMAGE"]`):
```python
response = client.models.generate_content(
    model="gemini-3-pro-image",
    contents="Architectural blueprint of a distributed cloud system",
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
    ),
)
```

---

## 4. Agentic Systems & MCP Server Architecture

### 4.1 Module 07: OmniOps Autonomous SRE Platform (`07_Capstone_OmniOps_Autonomous_SRE_Platform/`)
- **Entrypoint**: [`app/main.py`](07_Capstone_OmniOps_Autonomous_SRE_Platform/app/main.py) (FastAPI service on port `8080`).
- **Capabilities**:
  - Hybrid Runbook Retrieval combining dense embeddings (`gemini-embedding-2`) with lexical keyword scoring.
  - Autonomous ReAct loop powered by `gemini-3.8-flash` with deterministic tool execution (`fetch_pod_telemetry`, `query_error_logs`, `execute_remediation_action`).
  - Guardrailed remediation gating (blocks destructive operations unless safety preconditions pass).

### 4.2 Module 08: Tax-Aware Target-Return FinTech Platform (`08_Tax_Aware_Target_Return_Fintech_Platform/`)
- **Entrypoint**: [`app/main.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/main.py) + interactive UI at [`app/static/index.html`](08_Tax_Aware_Target_Return_Fintech_Platform/app/static/index.html).
- **Agent & Engine Modules (`app/agents/`)**:
  - [`app/agents/tax_hurdle_calculator.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/agents/tax_hurdle_calculator.py): Indian FY 2025-26 tax hurdle & friction calculator (STCG 20%, LTCG 12.5%, STT, brokerage, SEBI/exchange charges, GST).
  - [`app/agents/intraday_engine.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/agents/intraday_engine.py): Dual-model autonomous trading & portfolio engine (`gemini-3.8-flash` for low-latency regime detection & execution; `gemini-3.1-pro-preview` for deep multi-asset tax-aware strategy).
- **Memory & Security (`app/memory/`, `app/security/`)**:
  - [`app/memory/financial_memory.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/memory/financial_memory.py) & [`app/memory/state_store.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/memory/state_store.py): Persistent trade ledger and portfolio state store.
  - [`app/security/sebi_guardrail.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/security/sebi_guardrail.py) & [`app/security/auth.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/security/auth.py): Deterministic SEBI compliance guardrails, position-sizing limits, and authentication middleware.
- **MCP Servers (`app/mcp_servers/`)**:
  - [`app/mcp_servers/dhan_mcp.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/mcp_servers/dhan_mcp.py) & [`dhan_mcp_standalone.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/mcp_servers/dhan_mcp_standalone.py): DhanHQ v2 live market quotes, intraday candles, and order execution tools.
  - [`app/mcp_servers/zerodha_mcp.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/mcp_servers/zerodha_mcp.py) & [`zerodha_mcp_standalone.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/mcp_servers/zerodha_mcp_standalone.py): Zerodha Kite Connect v3 portfolio holdings, margins, and order placement tools.
  - [`app/mcp_servers/razorpay_mcp.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/mcp_servers/razorpay_mcp.py) & [`razorpay_mcp_standalone.py`](08_Tax_Aware_Target_Return_Fintech_Platform/app/mcp_servers/razorpay_mcp_standalone.py): Razorpay capital funding, UPI payment links, and settlement verification tools.

---

## 5. Visual Diagrams & Notebook Asset Synchronization

Every module contains custom SVG vector diagrams (`images/*.svg`) rendered to high-resolution PNGs (`images/*.png`) and embedded directly as self-contained `data:image/png;base64,...` URIs inside the Jupyter notebooks (`.ipynb`) so notebooks render with zero broken image links on GitHub, Colab, and VS Code.

Whenever an agent modifies any diagram text or model label in `images/*.svg`:
1. **Validate XML**: Parse every modified `.svg` with `xml.etree.ElementTree.parse()` to guarantee well-formed XML.
2. **Render PNG**: Regenerate the corresponding `.png` at 1600px resolution (`/usr/bin/qlmanage -t -s 1600`).
3. **Sync Base64 in `.ipynb`**: Re-encode the updated `.png` into base64 and update the corresponding `![...](data:image/png;base64,...)` markdown cell in the module's `.ipynb` notebook.
4. **Validate Notebook AST**: Parse every code cell in all `.ipynb` files using Python's `ast.parse()` to ensure zero syntax errors or unescaped string literals.

---

## 6. Verification, Testing & Deployment Workflows

### 6.1 Pre-Commit Verification Checklist
Before committing or pushing changes, agents must run:
```bash
# 1. Verify all Python source files compile cleanly
python3 -m py_compile \
  07_Capstone_OmniOps_Autonomous_SRE_Platform/app/main.py \
  08_Tax_Aware_Target_Return_Fintech_Platform/app/main.py \
  08_Tax_Aware_Target_Return_Fintech_Platform/app/agents/*.py \
  08_Tax_Aware_Target_Return_Fintech_Platform/app/mcp_servers/*.py \
  08_Tax_Aware_Target_Return_Fintech_Platform/app/memory/*.py \
  08_Tax_Aware_Target_Return_Fintech_Platform/app/security/*.py
```

### 6.2 Cloud Run Deployment
Both production platforms include automated deployment scripts targeting Google Cloud Run:
- **OmniOps SRE Platform**: `07_Capstone_OmniOps_Autonomous_SRE_Platform/deploy_cloud_run.sh`
- **Tax-Aware FinTech Platform**: `08_Tax_Aware_Target_Return_Fintech_Platform/app/deploy_gcp.sh`
