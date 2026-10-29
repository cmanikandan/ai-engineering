# AGENTS.md — AI Engineering, Multi-Harness & Agentic Architecture Guide (2026 Edition)

This document defines the architectural standards, official 2026 Gemini model routing matrix, multi-harness contracts (Google Antigravity SDK, Gemini Managed Agents, Google ADK, Gemini Enterprise, Direct Interactions API), LLM Gateway & Alerting specifications, and operational workflows for autonomous AI coding agents and engineers working inside **[`cmanikandan/ai-engineering`](https://github.com/cmanikandan/ai-engineering)**.

---

## 1. Repository Overview & 10-Module Topology

This repository is an end-to-end **Production AI Engineering Curriculum, Interactive Workshop & Visual Reference Architecture (2026 Edition)** built natively on the **Google GenAI SDK (`google-genai` v2.30+)**, **Google Antigravity SDK (`google-antigravity`)**, **Google ADK (`google-adk`)**, **Model Context Protocol (MCP)**, **FastAPI**, and **Google Cloud Run**.

| Module | Directory | Primary Agentic / Engineering Pattern | Core Models Used |
| :--- | :--- | :--- | :--- |
| **01** | [`01_LLM_Foundations_Interactive_Playground/`](01_LLM_Foundations_Interactive_Playground/) | BPE Tokenization, Sampling Physics, Stateful Interactions API, Structured Outputs, Post-Training (GRPO) | `gemini-3.8-flash`, `gemini-4-argon` |
| **02** | [`02_Enterprise_RAG_Knowledge_Assistant/`](02_Enterprise_RAG_Knowledge_Assistant/) | Hybrid Search (Dense `gemini-embedding-2` + BM25 + RRF), Stratified Prefix Caching, RAFT & Self-RAG Grading | `gemini-embedding-2`, `gemini-3.8-flash`, `gemini-4-argon` |
| **03** | [`03_Agentic_Workflows_Web_Search_Agent/`](03_Agentic_Workflows_Web_Search_Agent/) | ReAct Loop, Evaluator-Optimizer, Streamable HTTP FastMCP, Managed Antigravity Agent Integration | `gemini-3.8-flash`, `antigravity-preview-09-2026` |
| **04** | [`04_Reasoning_Models_Deep_Research_Engine/`](04_Reasoning_Models_Deep_Research_Engine/) | Gemini 4 Argon 1M Unified Window & Long-Decode (`background=True`), `thinking_level`, Deep Research Max | `gemini-4-argon`, `deep-research-max-preview-04-2026` |
| **05** | [`05_Multimodal_Vision_Media_Synthesis_Agent/`](05_Multimodal_Vision_Media_Synthesis_Agent/) | Nano Banana 2.1 (14-image fusion & 4K edit), Omni 1.1 Flash 40s Video, Gemini 3.8 Live Extended Thinking, 3.8 Flash TTS | `gemini-nano-banana-2.1`, `gemini-omni-1.1-flash`, `gemini-3.8-live-extended-thinking`, `gemini-3.8-flash-tts` |
| **06** | [`06_Tokenomics_Cost_Optimization_LLM_Gateway/`](06_Tokenomics_Cost_Optimization_LLM_Gateway/) | **OmniGateway**: Multi-Tier + Multimodal Router, Context Cache Vault, Live FinOps Web Dashboard, Automated User (80%) & Admin (100% / SecOps / Executive) HTML Email Alerting | `gemma-4-26b-a4b-it`, `gemini-3.5-flash-lite`, `gemini-3.8-flash`, `gemini-4-argon` |
| **07** | [`07_Capstone_OmniOps_Autonomous_SRE_Platform/`](07_Capstone_OmniOps_Autonomous_SRE_Platform/) | **OmniOps SRE**: Autonomous Incident Triage, Hybrid Runbook RAG, Grafana Vision, Dual-Model Escalation | `gemini-3.8-flash`, `gemini-4-argon`, `gemini-embedding-2` |
| **08** | [`08_Tax_Aware_Target_Return_Fintech_Platform/`](08_Tax_Aware_Target_Return_Fintech_Platform/) | **WealthPulse FinTech**: Section 111A Tax Hurdle Engine, Intraday MIS vs Swing CNC, DhanHQ + Zerodha + Razorpay MCPs | `gemini-3.8-flash`, `gemini-4-argon` |
| **09** | [`09_Multi_Harness_Agentic_Engineering_Lab/`](09_Multi_Harness_Agentic_Engineering_Lab/) | **Multi-Harness Lab**: Side-by-side mastery of Antigravity SDK, Managed Agents, Google ADK, Gemini Enterprise, Direct Interactions API & LiteRT Local | `gemini-4-argon`, `gemini-3.8-flash`, `gemma-4-26b-a4b-it` |
| **10** | [`10_Industry_Best_Practices_Market_Leaders_Playbook/`](10_Industry_Best_Practices_Market_Leaders_Playbook/) | **Market Leaders Playbook**: Stratified Context Compaction, Speculative Cascade, Sandboxed Hooks, LLM-as-a-Judge CI/CD Flywheel & Executive Alerting | `gemini-4-argon`, `gemini-3.8-flash`, `gemini-3.5-flash-lite` |

---

## 2. Official 2026 Gemini Model Matrix & Deprecation Rules

### 2.1 Active Model Routing Matrix

| Tier / Capability | Official Model ID | Target Use Cases in Repository |
| :--- | :--- | :--- |
| **Tier 0: On-Device Local Open-Weights (LiteRT)** | `gemma-4-26b-a4b-it` / `gemma-4-31b-it` | Air-gapped local coding & privacy-strict operations via `LiteRTAgentConfig`. |
| **Tier 1: Ultra-Fast / Cost-Optimized Lite** | `gemini-3.5-flash-lite` | Pre-inference prompt-injection guardrails, PII scrubbing, simple intent routing, high-volume extraction. |
| **Tier 2: Default Agentic & Multimodal Workhorse** | `gemini-3.8-flash` | Default model for Antigravity SDK & Managed Agents, ReAct tool-calling loops, Hybrid RAG synthesis. |
| **Tier 3: Frontier Reasoning, Judge & 1M Long-Decode** | `gemini-4-argon` | Complex software engineering, financial/tax optimization, formal math/science proofs, 1M unified context & Long-Decode (`background=True`), LLM-as-a-Judge (`thinking_level="low"\|"medium"\|"high"`). |
| **Image Generation & Editing (Nano Banana)** | `gemini-nano-banana-2.1` | High-efficiency 4K image generation, conversational image editing, up to 14 reference images fusion. |
| **Generative Video & Audio** | `gemini-omni-1.1-flash` | Text-to-video, `<FIRST_FRAME>` / `<LAST_FRAME>` transitions, reference-guided video, 40s video extensions. |
| **Real-Time Live API (WebSockets)** | `gemini-3.8-live` / `gemini-3.8-live-extended-thinking` | Bidirectional voice/video streaming, `behavior="NON_BLOCKING"` async tools, `interaction_status` lifecycle. |
| **Speech Synthesis (TTS) & Transcription (STT)** | `gemini-3.8-flash-tts` / `gemini-3.8-flash-lite-tts` / `gemini-3.5-transcribe-live` | Expressive multi-speaker TTS, Voice Design, Voice Replication, and real-time STT with Hybrid VAD. |
| **Multimodal Semantic Embeddings** | `gemini-embedding-2` | Vector indexing across text/images/video/audio/PDF, hybrid search, semantic cache lookup. |
| **Managed Cloud Agents** | `antigravity-preview-09-2026` / `deep-research-max-preview-04-2026` | Remote sandboxed Linux execution (`environment="remote"`) and exhaustive autonomous research. |

### 2.2 Strictly Prohibited / Deprecated Models
Agents **MUST NEVER** introduce or revert to legacy or shut-down identifiers:
- ❌ `google-generativeai` (legacy SDK package — always use `google-genai`)
- ❌ Any older generation `1.x`, `2.x`, or pre-`3.5` Gemini text/pro/flash/image identifiers
- ❌ Legacy text-only embedding or standalone Imagen preview identifiers (always use `gemini-embedding-2` and `gemini-nano-banana-2.1`)

---

## 3. Pre-Commit Verification Checklist

Before committing or pushing changes, agents must run:
```bash
python3 -m py_compile \
  06_Tokenomics_Cost_Optimization_LLM_Gateway/app/main.py \
  06_Tokenomics_Cost_Optimization_LLM_Gateway/app/gateway_engine.py \
  06_Tokenomics_Cost_Optimization_LLM_Gateway/app/alerting.py \
  07_Capstone_OmniOps_Autonomous_SRE_Platform/app/main.py \
  08_Tax_Aware_Target_Return_Fintech_Platform/app/main.py \
  08_Tax_Aware_Target_Return_Fintech_Platform/app/agents/*.py \
  08_Tax_Aware_Target_Return_Fintech_Platform/app/mcp_servers/*.py \
  08_Tax_Aware_Target_Return_Fintech_Platform/app/memory/*.py \
  08_Tax_Aware_Target_Return_Fintech_Platform/app/security/*.py \
  09_Multi_Harness_Agentic_Engineering_Lab/harness_orchestrator.py \
  10_Industry_Best_Practices_Market_Leaders_Playbook/market_leaders_playbook.py
```
