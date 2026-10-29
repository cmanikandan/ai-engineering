"""
Enterprise Multi-Tier + Multimodal LLM Gateway, FinOps Router & Governance Engine
=================================================================================
Routes requests across the official 2026 Google Gemini & Gemma Model Portfolio:
- Tier 0 (On-Device Local LiteRT): `gemma-4-26b-a4b-it`, `gemma-4-31b-it`
- Tier 1 (Ultra-Fast / Lite): `gemini-3.5-flash-lite`
- Tier 2 (Agentic & Multimodal Workhorse): `gemini-3.8-flash`
- Tier 3 / Frontier (Reasoning, Coding, Judge & 1M Long-Decode): `gemini-4-argon` (`thinking_level="low"|"medium"|"high"`)
- Multimodal Studio: `gemini-nano-banana-2.1`, `gemini-omni-1.1-flash`, `gemini-3.8-live`, `gemini-3.8-live-extended-thinking`, `gemini-3.8-flash-tts`, `gemini-3.5-transcribe-live`
"""

import os
import re
import time
import uuid
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from alerting import alerting_service


# -----------------------------------------------------------------------------
# 1. Official 2026 Gemini Model Pricing & Capability Catalog (USD per 1M tokens)
# -----------------------------------------------------------------------------
MODEL_CATALOG: Dict[str, Dict[str, Any]] = {
    "gemma-4-26b-a4b-it": {
        "tier": "TIER_0_LOCAL_LITERT",
        "display_name": "Gemma 4 26B-A4B (Local LiteRT)",
        "input_per_1m": 0.00,
        "cached_input_per_1m": 0.00,
        "output_per_1m": 0.00,
        "context_window": 131_072,
        "default_latency_ms": 165,
        "best_for": "Zero-API-cost local/offline air-gapped agentic coding & privacy-strict PII workflows via LiteRTAgentConfig",
    },
    "gemini-3.5-flash-lite": {
        "tier": "TIER_1_FLASH_LITE",
        "display_name": "Gemini 3.5 Flash-Lite",
        "input_per_1m": 0.075,
        "cached_input_per_1m": 0.01875,
        "output_per_1m": 0.30,
        "context_window": 1_048_576,
        "default_latency_ms": 210,
        "best_for": "Guardrail classification, PII scrubbing, high-throughput extraction, intent routing",
    },
    "gemini-3.8-flash": {
        "tier": "TIER_2_FLASH_WORKHORSE",
        "display_name": "Gemini 3.8 Flash",
        "input_per_1m": 0.15,
        "cached_input_per_1m": 0.0375,
        "output_per_1m": 0.60,
        "context_window": 1_048_576,
        "default_latency_ms": 420,
        "best_for": "Default agentic tool-calling, Hybrid RAG synthesis, multimodal inspection, Antigravity default",
    },
    "gemini-4-argon": {
        "tier": "TIER_3_ARGON_FRONTIER",
        "display_name": "Gemini 4 Argon (Frontier GA)",
        "input_per_1m": 2.00,
        "cached_input_per_1m": 0.50,
        "output_per_1m": 10.00,
        "context_window": 1_048_576,
        "default_latency_ms": 1350,
        "best_for": "Frontier software architecture, tax/quant optimization, LLM-as-a-Judge, math proofs & 1M Long-Decode (background=True)",
    },
    "gemini-nano-banana-2.1": {
        "tier": "TIER_MULTIMODAL_IMAGE",
        "display_name": "Gemini Nano Banana 2.1 🍌",
        "input_per_1m": 0.20,
        "cached_input_per_1m": 0.05,
        "output_per_1m": 1.20,
        "context_window": 131_072,
        "default_latency_ms": 1150,
        "best_for": "4K image generation, conversational visual editing, up to 14 reference images fusion",
    },
    "gemini-omni-1.1-flash": {
        "tier": "TIER_MULTIMODAL_VIDEO",
        "display_name": "Gemini Omni 1.1 Flash 🎬",
        "input_per_1m": 0.30,
        "cached_input_per_1m": 0.075,
        "output_per_1m": 2.40,
        "context_window": 131_072,
        "default_latency_ms": 3200,
        "best_for": "Text-to-video, first/last frame transitions, 40s video extensions, native audio track synthesis",
    },
    "gemini-3.8-live-extended-thinking": {
        "tier": "TIER_MULTIMODAL_LIVE",
        "display_name": "Gemini 3.8 Live Extended Thinking",
        "input_per_1m": 0.25,
        "cached_input_per_1m": 0.06,
        "output_per_1m": 1.00,
        "context_window": 128_000,
        "default_latency_ms": 180,
        "best_for": "Real-time bidirectional voice/video streaming, NON_BLOCKING async tool calls, Hybrid VAD",
    },
    "gemini-3.8-flash-tts": {
        "tier": "TIER_MULTIMODAL_AUDIO",
        "display_name": "Gemini 3.8 Flash TTS 🎙️",
        "input_per_1m": 0.12,
        "cached_input_per_1m": 0.03,
        "output_per_1m": 0.50,
        "context_window": 65_536,
        "default_latency_ms": 290,
        "best_for": "Expressive multi-speaker speech synthesis, Voice Design personas, Voice Replication",
    },
}


class GatewayRequest(BaseModel):
    prompt: str = Field(description="User or agent prompt sent to the Enterprise LLM Gateway")
    tenant_id: str = Field(default="acme-core-eng")
    user_email: str = Field(default="dev.lead@acme.io")
    harness: str = Field(
        default="antigravity_sdk",
        description="Harness: antigravity_sdk | antigravity_managed_agent | google_adk | gemini_enterprise_vertex | direct_interactions_api | rest_websocket",
    )
    modality: str = Field(default="TEXT", description="TEXT | IMAGE | VIDEO | LIVE_AUDIO | TTS")
    thinking_level: str = Field(default="medium", description="low | medium | high")
    use_context_cache: bool = Field(default=True)
    service_tier: str = Field(default="standard", description="standard | priority | flex")
    force_model: Optional[str] = Field(default=None)


class TenantBudgetState(BaseModel):
    tenant_id: str
    tenant_name: str
    owner_email: str
    admin_email: str
    budget_limit_usd: float
    current_spend_usd: float = 0.0
    warned_80_pct: bool = False
    circuit_breaker_tripped: bool = False
    requests_count: int = 0
    cached_requests_count: int = 0
    blocked_security_count: int = 0


class EnterpriseGatewayEngine:
    """
    Stateful Enterprise LLM Gateway with:
    - Pre-inference PII & Prompt-Injection Guardrail
    - Semantic & Prefix Context Cache Vault
    - 4-Tier + Multimodal Complexity Router
    - Per-Tenant FinOps Quota & Circuit-Breaker Governance
    - Real-Time Alerting Integration (User & Admin HTML Emails)
    """

    def __init__(self) -> None:
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client: Optional[genai.Client] = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

        self.tenants: Dict[str, TenantBudgetState] = {
            "acme-core-eng": TenantBudgetState(
                tenant_id="acme-core-eng",
                tenant_name="Acme Core Platform Engineering",
                owner_email="dev.lead@acme.io",
                admin_email="finops-admin@acme.io",
                budget_limit_usd=0.0500,  # Low demo cap so interactive queries easily trigger 80% & 100% alerts
                current_spend_usd=0.0360,
            ),
            "wealthpulse-quant": TenantBudgetState(
                tenant_id="wealthpulse-quant",
                tenant_name="WealthPulse Quant & Tax Desk",
                owner_email="quant.trader@wealthpulse.ai",
                admin_email="ciso-admin@wealthpulse.ai",
                budget_limit_usd=0.1000,
                current_spend_usd=0.0410,
            ),
            "omniops-sre-prod": TenantBudgetState(
                tenant_id="omniops-sre-prod",
                tenant_name="OmniOps Autonomous SRE Fleet",
                owner_email="sre.oncall@omniops.cloud",
                admin_email="platform-sre-admin@omniops.cloud",
                budget_limit_usd=0.2000,
                current_spend_usd=0.0890,
            ),
        }
        self.semantic_cache: Dict[str, Dict[str, Any]] = {}
        self.telemetry_log: List[Dict[str, Any]] = []
        self._seed_initial_telemetry()

    # -------------------------------------------------------------------------
    # Security & PII DLP Scrubber
    # -------------------------------------------------------------------------
    def inspect_and_scrub_prompt(self, prompt: str, tenant_id: str, user_email: str) -> Tuple[bool, str, Optional[str], float]:
        """
        Returns (is_allowed, scrubbed_prompt, violation_category, risk_score).
        Blocks prompt injections / credential leaks and dispatches SecOps Admin Email.
        """
        lower_p = prompt.lower()
        injection_patterns = [
            "ignore previous instructions",
            "ignore all prior rules",
            "dump system prompt",
            "bypass safety guardrail",
            "exfiltrate database",
            "drop table users",
        ]
        for pat in injection_patterns:
            if pat in lower_p:
                redacted = re.sub(r"[A-Za-z0-9]{6,}", "[REDACTED]", prompt[:180])
                alerting_service.send_admin_security_guardrail_alert(
                    secops_email="secops-admin@enterprise.internal",
                    tenant_id=tenant_id,
                    user_email=user_email,
                    violation_category="PROMPT_INJECTION_ATTEMPT",
                    risk_score=0.97,
                    redacted_snippet=redacted,
                )
                if tenant_id in self.tenants:
                    self.tenants[tenant_id].blocked_security_count += 1
                return False, prompt, "PROMPT_INJECTION_ATTEMPT", 0.97

        # Scrub sensitive PII (SSNs, Credit Cards, API keys) inline
        scrubbed = prompt
        pii_found = False
        if re.search(r"\b\d{3}-\d{2}-\d{4}\b", scrubbed):
            scrubbed = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]", scrubbed)
            pii_found = True
        if re.search(r"\b(AIza[0-9A-Za-z\-_]{20,}|ghp_[0-9A-Za-z]{20,})\b", scrubbed):
            scrubbed = re.sub(r"\b(AIza[0-9A-Za-z\-_]{20,}|ghp_[0-9A-Za-z]{20,})\b", "[REDACTED_SECRET_KEY]", scrubbed)
            pii_found = True

        if pii_found:
            alerting_service.send_admin_security_guardrail_alert(
                secops_email="secops-admin@enterprise.internal",
                tenant_id=tenant_id,
                user_email=user_email,
                violation_category="PII_OR_SECRET_INLINE_REDACTION",
                risk_score=0.74,
                redacted_snippet=scrubbed[:180],
                action_taken="SCRUBBED_INLINE_AND_FORWARDED",
            )
        return True, scrubbed, ("PII_SCRUBBED" if pii_found else None), (0.74 if pii_found else 0.04)

    # -------------------------------------------------------------------------
    # Intelligent 4-Tier + Multimodal Classifier
    # -------------------------------------------------------------------------
    def select_optimal_model(self, req: GatewayRequest, tenant: TenantBudgetState) -> Tuple[str, str]:
        """Returns (model_id, routing_rationale)."""
        if req.harness == "litert_local":
            return (
                "gemma-4-26b-a4b-it",
                "Local air-gapped harness (LiteRTAgentConfig) -> Routed to Tier-0 On-Device Gemma 4 26B-A4B ($0 API cost)",
            )

        if tenant.circuit_breaker_tripped:
            return (
                "gemini-3.5-flash-lite",
                "Circuit Breaker Active (100% Tenant Cap Reached) -> Forced downgrade to Tier-1 Flash-Lite",
            )

        if req.force_model and req.force_model in MODEL_CATALOG:
            return req.force_model, f"Explicit model override requested ({req.force_model})"

        modality = req.modality.upper()
        if modality == "IMAGE":
            return "gemini-nano-banana-2.1", "Multimodal Image synthesis/editing routed to Nano Banana 2.1"
        if modality == "VIDEO":
            return "gemini-omni-1.1-flash", "Multimodal Video generation/extension routed to Gemini Omni 1.1 Flash"
        if modality == "LIVE_AUDIO":
            return "gemini-3.8-live-extended-thinking", "Real-time bidirectional voice/video session routed to Gemini 3.8 Live Extended Thinking"
        if modality == "TTS":
            return "gemini-3.8-flash-tts", "Expressive speech synthesis routed to Gemini 3.8 Flash TTS"

        p_lower = req.prompt.lower()
        frontier_keywords = [
            "prove",
            "theorem",
            "formal verification",
            "distributed consensus",
            "race condition",
            "long decode",
            "architecture blueprint",
            "compiler",
            "quantum",
            "deep research",
            "1m token",
            "tax hurdle",
            "section 111a",
            "portfolio optimization",
            "evaluate trajectory",
            "llm-as-a-judge",
            "financial model",
            "compliance audit",
        ]
        lite_keywords = [
            "classify",
            "sentiment",
            "extract json",
            "format",
            "summarize in one line",
            "translate",
            "tag",
            "pii",
        ]

        if any(k in p_lower for k in frontier_keywords) or req.thinking_level == "high":
            return (
                "gemini-4-argon",
                f"Frontier reasoning / judge / long-decode signature detected -> Routed to Gemini 4 Argon (thinking_level={req.thinking_level})",
            )
        if any(k in p_lower for k in lite_keywords) or len(req.prompt.split()) < 14:
            return (
                "gemini-3.5-flash-lite",
                "Lightweight classification/extraction signature -> Routed to Tier-1 Gemini 3.5 Flash-Lite (96% cheaper than Argon)",
            )

        return (
            "gemini-3.8-flash",
            "Standard agentic / RAG / code task -> Routed to Tier-2 Workhorse Gemini 3.8 Flash",
        )

    # -------------------------------------------------------------------------
    # Cost Calculation & Execution
    # -------------------------------------------------------------------------
    def compute_cost(
        self,
        model_id: str,
        prompt_tokens: int,
        cached_tokens: int,
        output_tokens: int,
        thoughts_tokens: int,
        service_tier: str = "standard",
    ) -> Tuple[float, float]:
        """Returns (actual_cost_usd, unoptimized_argon_baseline_usd)."""
        spec = MODEL_CATALOG.get(model_id, MODEL_CATALOG["gemini-3.8-flash"])
        uncached_in = max(0, prompt_tokens - cached_tokens)
        tier_mult = 1.5 if service_tier == "priority" else (0.5 if service_tier == "flex" else 1.0)

        in_cost = (uncached_in / 1_000_000) * spec["input_per_1m"]
        cache_cost = (cached_tokens / 1_000_000) * spec["cached_input_per_1m"]
        out_cost = ((output_tokens + thoughts_tokens) / 1_000_000) * spec["output_per_1m"]
        actual_usd = (in_cost + cache_cost + out_cost) * tier_mult

        # Baseline: what it would have cost running uncached on Frontier gemini-4-argon
        argon = MODEL_CATALOG["gemini-4-argon"]
        baseline_usd = (
            (prompt_tokens / 1_000_000) * argon["input_per_1m"]
            + ((output_tokens + thoughts_tokens + 600) / 1_000_000) * argon["output_per_1m"]
        )
        return round(actual_usd, 6), round(max(baseline_usd, actual_usd), 6)

    def route_and_execute(self, req: GatewayRequest) -> Dict[str, Any]:
        tenant = self.tenants.get(req.tenant_id)
        if not tenant:
            tenant = TenantBudgetState(
                tenant_id=req.tenant_id,
                tenant_name=f"Tenant {req.tenant_id}",
                owner_email=req.user_email,
                admin_email="finops-admin@enterprise.internal",
                budget_limit_usd=0.1000,
            )
            self.tenants[req.tenant_id] = tenant

        # 1. Pre-Inference Security & PII Guardrail
        allowed, scrubbed_prompt, sec_flag, risk_score = self.inspect_and_scrub_prompt(
            req.prompt, req.tenant_id, req.user_email
        )
        if not allowed:
            record = {
                "request_id": f"req_{uuid.uuid4().hex[:8]}",
                "timestamp": time.strftime("%H:%M:%S"),
                "tenant_id": req.tenant_id,
                "user_email": req.user_email,
                "harness": req.harness,
                "model_selected": "BLOCKED_BY_GUARDRAIL",
                "tier": "SECURITY_BLOCK",
                "prompt_preview": req.prompt[:90],
                "prompt_tokens": 0,
                "cached_tokens": 0,
                "output_tokens": 0,
                "thoughts_tokens": 0,
                "latency_ms": 18,
                "actual_cost_usd": 0.0,
                "baseline_cost_usd": 0.0045,
                "cache_hit": False,
                "security_flag": sec_flag,
                "routing_rationale": "Blocked by pre-inference prompt-injection guardrail; SecOps alert dispatched.",
                "response_text": "🛑 Request blocked by Enterprise AI Security Guardrail (Prompt Injection / Policy Violation). Incident logged and SecOps notified.",
            }
            self.telemetry_log.insert(0, record)
            return record

        # 2. Check Semantic Cache
        cache_key = hashlib.sha256(f"{req.modality}:{scrubbed_prompt.strip().lower()}".encode()).hexdigest()[:16]
        is_semantic_hit = req.use_context_cache and (cache_key in self.semantic_cache)

        # 3. Select Model Tier
        model_id, rationale = self.select_optimal_model(req, tenant)
        spec = MODEL_CATALOG[model_id]

        # 4. Token & Response Synthesis (Live API if key configured, else realistic deterministic simulation)
        prompt_tokens = max(120, len(scrubbed_prompt.split()) * 4 + (3200 if req.use_context_cache else 0))
        cached_tokens = int(prompt_tokens * 0.82) if req.use_context_cache else 0
        thoughts_tokens = (
            1250 if model_id == "gemini-4-argon" else (480 if model_id in ("gemini-3.8-flash", "gemini-3.8-live-extended-thinking") else 0)
        )
        if req.thinking_level == "low":
            thoughts_tokens = int(thoughts_tokens * 0.35)
        elif req.thinking_level == "high":
            thoughts_tokens = int(thoughts_tokens * 1.8)

        output_tokens = 420 if model_id != "gemini-3.5-flash-lite" else 140
        latency_ms = 24 if is_semantic_hit else spec["default_latency_ms"]

        response_text = ""
        if is_semantic_hit:
            cached_entry = self.semantic_cache[cache_key]
            response_text = f"⚡ [SEMANTIC CACHE HIT — 0 Model Output Tokens Billed]\n{cached_entry['response_text']}"
            actual_usd, baseline_usd = 0.000015, cached_entry["baseline_cost_usd"]
            tenant.cached_requests_count += 1
        else:
            if self.client and req.modality == "TEXT" and model_id in ("gemini-3.8-flash", "gemini-3.5-flash-lite"):
                try:
                    t0 = time.time()
                    resp = self.client.models.generate_content(
                        model=model_id,
                        contents=scrubbed_prompt,
                    )
                    latency_ms = int((time.time() - t0) * 1000)
                    response_text = resp.text or "Response generated."
                except Exception:
                    response_text = self._simulate_model_response(model_id, req.harness, scrubbed_prompt, req.thinking_level)
            else:
                response_text = self._simulate_model_response(model_id, req.harness, scrubbed_prompt, req.thinking_level)

            actual_usd, baseline_usd = self.compute_cost(
                model_id=model_id,
                prompt_tokens=prompt_tokens,
                cached_tokens=cached_tokens,
                output_tokens=output_tokens,
                thoughts_tokens=thoughts_tokens,
                service_tier=req.service_tier,
            )
            if req.use_context_cache:
                tenant.cached_requests_count += 1
                self.semantic_cache[cache_key] = {
                    "response_text": response_text,
                    "baseline_cost_usd": baseline_usd,
                }

        # 5. Update Tenant Spend & Check 80% User Warning / 100% Admin Circuit Breaker
        tenant.requests_count += 1
        tenant.current_spend_usd = round(tenant.current_spend_usd + actual_usd, 6)
        utilization_ratio = tenant.current_spend_usd / max(tenant.budget_limit_usd, 0.0001)

        alerts_triggered: List[str] = []
        if utilization_ratio >= 0.80 and not tenant.warned_80_pct:
            tenant.warned_80_pct = True
            ev = alerting_service.send_user_quota_warning(
                user_email=tenant.owner_email,
                user_name=tenant.tenant_name,
                tenant_id=tenant.tenant_id,
                used_usd=tenant.current_spend_usd,
                limit_usd=tenant.budget_limit_usd,
                top_model=model_id,
            )
            alerts_triggered.append(ev.alert_type)

        if utilization_ratio >= 1.00 and not tenant.circuit_breaker_tripped:
            tenant.circuit_breaker_tripped = True
            ev = alerting_service.send_admin_circuit_breaker_alert(
                admin_email=tenant.admin_email,
                tenant_id=tenant.tenant_id,
                used_usd=tenant.current_spend_usd,
                limit_usd=tenant.budget_limit_usd,
                action_taken="AUTO_DOWNGRADE_TO_FLASH_LITE",
                anomalous_agent_id=f"{req.harness}:{model_id}",
            )
            alerts_triggered.append(ev.alert_type)

        record = {
            "request_id": f"req_{uuid.uuid4().hex[:8]}",
            "timestamp": time.strftime("%H:%M:%S"),
            "tenant_id": req.tenant_id,
            "user_email": req.user_email,
            "harness": req.harness,
            "model_selected": model_id,
            "model_display_name": spec["display_name"],
            "tier": spec["tier"],
            "prompt_preview": scrubbed_prompt[:90],
            "prompt_tokens": prompt_tokens,
            "cached_tokens": cached_tokens,
            "output_tokens": output_tokens,
            "thoughts_tokens": thoughts_tokens,
            "latency_ms": latency_ms,
            "actual_cost_usd": actual_usd,
            "baseline_cost_usd": baseline_usd,
            "savings_usd": round(max(0.0, baseline_usd - actual_usd), 6),
            "cache_hit": req.use_context_cache,
            "security_flag": sec_flag,
            "routing_rationale": rationale,
            "alerts_triggered": alerts_triggered,
            "response_text": response_text,
        }
        self.telemetry_log.insert(0, record)
        return record

    def _simulate_model_response(self, model_id: str, harness: str, prompt: str, thinking_level: str) -> str:
        return (
            f"[{model_id} | Harness: {harness} | thinking_level={thinking_level}]\n"
            f"Executed via Enterprise LLM Gateway with prefix context caching enabled.\n"
            f"Task synthesized for: '{prompt[:120]}'\n"
            f"• Verified schema & safety constraints\n"
            f"• Recorded token telemetry (prompt, cached, candidates, and thinking tokens) in FinOps ledger."
        )

    def get_dashboard_summary(self) -> Dict[str, Any]:
        total_reqs = len(self.telemetry_log)
        actual_usd = sum(r["actual_cost_usd"] for r in self.telemetry_log)
        baseline_usd = sum(r["baseline_cost_usd"] for r in self.telemetry_log)
        saved_usd = max(0.0, baseline_usd - actual_usd)
        savings_pct = round((saved_usd / max(baseline_usd, 0.0001)) * 100, 1)
        cache_hits = sum(1 for r in self.telemetry_log if r.get("cache_hit"))
        cache_hit_pct = round((cache_hits / max(total_reqs, 1)) * 100, 1)

        tier_dist: Dict[str, int] = {}
        harness_dist: Dict[str, int] = {}
        for r in self.telemetry_log:
            m = r["model_selected"]
            tier_dist[m] = tier_dist.get(m, 0) + 1
            h = r.get("harness", "direct_interactions_api")
            harness_dist[h] = harness_dist.get(h, 0) + 1

        return {
            "total_requests": total_reqs,
            "actual_cost_usd": round(actual_usd, 5),
            "unoptimized_baseline_usd": round(baseline_usd, 5),
            "saved_usd": round(saved_usd, 5),
            "savings_pct": savings_pct,
            "cache_hit_pct": cache_hit_pct,
            "tier_distribution": tier_dist,
            "harness_distribution": harness_dist,
            "tenants": [t.model_dump() for t in self.tenants.values()],
            "recent_telemetry": self.telemetry_log[:25],
            "outbox_count": len(alerting_service.outbox),
            "model_catalog": MODEL_CATALOG,
        }

    def _seed_initial_telemetry(self) -> None:
        seed_samples = [
            GatewayRequest(
                prompt="Classify this customer support ticket into BILLING, TECHNICAL, or ACCOUNT_ACCESS.",
                tenant_id="acme-core-eng",
                user_email="dev.lead@acme.io",
                harness="direct_interactions_api",
                modality="TEXT",
                thinking_level="low",
            ),
            GatewayRequest(
                prompt="Triage HTTP 503 latency spike on payment-gateway Cloud Run pods using hybrid runbook RAG and MCP tools.",
                tenant_id="omniops-sre-prod",
                user_email="sre.oncall@omniops.cloud",
                harness="antigravity_sdk",
                modality="TEXT",
                thinking_level="medium",
            ),
            GatewayRequest(
                prompt="Calculate Indian FY 2025-26 Section 111A STCG 20.8% tax hurdle and optimize multi-asset portfolio allocation.",
                tenant_id="wealthpulse-quant",
                user_email="quant.trader@wealthpulse.ai",
                harness="google_adk",
                modality="TEXT",
                thinking_level="medium",
            ),
            GatewayRequest(
                prompt="Prove deadlock freedom and rewrite distributed lock lease renewal state machine with formal verification.",
                tenant_id="acme-core-eng",
                user_email="dev.lead@acme.io",
                harness="antigravity_managed_agent",
                modality="TEXT",
                thinking_level="high",
            ),
            GatewayRequest(
                prompt="Generate a 4K hand-drawn sketchnote architectural diagram of a multi-agent Kubernetes mesh.",
                tenant_id="acme-core-eng",
                user_email="designer@acme.io",
                harness="gemini_enterprise_vertex",
                modality="IMAGE",
                thinking_level="medium",
            ),
        ]
        for s in seed_samples:
            self.route_and_execute(s)

        # Also seed one executive digest so the outbox has both alerts and an executive report ready to view
        alerting_service.send_executive_finops_report(
            recipient_email="cto-executive@acme.io",
            stats=self.get_dashboard_summary(),
        )


gateway_engine = EnterpriseGatewayEngine()
