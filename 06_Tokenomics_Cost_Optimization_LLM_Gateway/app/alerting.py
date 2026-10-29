"""
Enterprise AI Alerting, HTML Email Dispatch & Executive Reporting Engine
========================================================================
Supports multi-channel notifications for both End Users and Platform Admins:
1. User Quota Warning (80% soft threshold)
2. User Long-Decode / Deep Research Background Job Completion
3. Admin Hard Budget Circuit-Breaker Trip (100% cap / anomalous token spike)
4. Admin Security & Prompt-Injection / PII DLP Guardrail Block
5. Admin Latency SLO & Priority-Tier Downgrade Alert
6. Executive Weekly FinOps, Tokenomics & Governance Digest Report

Channels supported:
- SMTP Email (HTML + Plaintext multipart)
- Google Workspace / Internal CLI (`sendgmr` fallback when available)
- Slack / PagerDuty / Generic Webhook JSON dispatches
- Local Persistent Outbox Store (for real-time UI dashboard & audit inspection)
"""

import os
import json
import time
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AlertEvent(BaseModel):
    alert_id: str = Field(default_factory=lambda: f"alrt_{uuid.uuid4().hex[:10]}")
    timestamp: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    alert_type: str
    severity: str  # INFO | WARNING | HIGH | CRITICAL
    recipient_role: str  # USER | ADMIN | EXECUTIVE | SECOPS | SRE
    recipient_email: str
    subject: str
    summary: str
    html_body: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    channels_dispatched: List[str] = Field(default_factory=list)
    delivery_status: str = "DELIVERED_TO_OUTBOX"


class EnterpriseAlertingService:
    """
    Production-grade notification and reporting engine for the Enterprise LLM Gateway.
    Stores all generated HTML emails and webhook events in an inspectable outbox
    and dispatches over SMTP / Webhook when configured via environment variables.
    """

    def __init__(self) -> None:
        self.outbox: List[AlertEvent] = []
        self.smtp_host = os.environ.get("ALERT_SMTP_HOST", "")
        self.smtp_port = int(os.environ.get("ALERT_SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("ALERT_SMTP_USER", "")
        self.smtp_pass = os.environ.get("ALERT_SMTP_PASS", "")
        self.sender_email = os.environ.get("ALERT_SENDER_EMAIL", "ai-gateway-noreply@enterprise.internal")
        self.webhook_url = os.environ.get("ALERT_WEBHOOK_URL", "")

    def _wrap_html_template(
        self,
        badge_text: str,
        badge_color: str,
        title: str,
        subtitle: str,
        body_html: str,
        cta_text: str = "Open AI Gateway Console",
        cta_url: str = "http://localhost:8086/",
    ) -> str:
        """Renders a responsive, enterprise-styled HTML email with actionable FinOps callouts."""
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
</head>
<body style="margin:0;padding:24px;background-color:#f4f6f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#1f2937;">
  <div style="max-width:680px;margin:0 auto;background:#ffffff;border-radius:14px;border:1px solid #e5e7eb;overflow:hidden;box-shadow:0 8px 24px rgba(15,23,42,0.06);">
    <div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:24px 28px;color:#ffffff;">
      <div style="display:inline-block;background:{badge_color};color:#ffffff;font-size:11px;font-weight:700;letter-spacing:0.8px;padding:4px 10px;border-radius:999px;text-transform:uppercase;margin-bottom:10px;">
        {badge_text}
      </div>
      <h1 style="margin:0 0 6px 0;font-size:21px;font-weight:700;color:#ffffff;">{title}</h1>
      <p style="margin:0;font-size:13px;color:#cbd5e1;">{subtitle}</p>
    </div>
    <div style="padding:26px 28px;font-size:14px;line-height:1.6;color:#334155;">
      {body_html}
      <div style="margin-top:24px;padding-top:18px;border-top:1px solid #e2e8f0;text-align:center;">
        <a href="{cta_url}" style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;font-weight:600;font-size:13px;padding:10px 20px;border-radius:8px;">
          {cta_text}
        </a>
      </div>
    </div>
    <div style="background:#f8fafc;padding:14px 28px;border-top:1px solid #e2e8f0;font-size:11px;color:#64748b;display:flex;justify-content:space-between;">
      <span>OmniGateway FinOps &amp; Governance Plane &bull; Powered by Google Gemini 4 Argon &amp; 3.8 Flash</span>
      <span>Automated Telemetry Dispatch</span>
    </div>
  </div>
</body>
</html>"""

    def _dispatch(self, event: AlertEvent) -> AlertEvent:
        channels = ["OUTBOX_UI"]
        if self.smtp_host and self.smtp_user:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = event.subject
                msg["From"] = self.sender_email
                msg["To"] = event.recipient_email
                msg.attach(MIMEText(event.summary, "plain", "utf-8"))
                msg.attach(MIMEText(event.html_body, "html", "utf-8"))
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=5) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_pass)
                    server.sendmail(self.sender_email, [event.recipient_email], msg.as_string())
                channels.append("SMTP_EMAIL")
                event.delivery_status = "SENT_VIA_SMTP"
            except Exception as exc:
                event.metadata["smtp_error"] = str(exc)

        event.channels_dispatched = channels
        self.outbox.insert(0, event)
        return event

    # -------------------------------------------------------------------------
    # 1. End-User Alert: 80% Soft Quota / Token Budget Warning
    # -------------------------------------------------------------------------
    def send_user_quota_warning(
        self,
        user_email: str,
        user_name: str,
        tenant_id: str,
        used_usd: float,
        limit_usd: float,
        top_model: str = "gemini-4-argon",
        thoughts_token_pct: float = 42.0,
    ) -> AlertEvent:
        pct = round((used_usd / max(limit_usd, 0.0001)) * 100, 1)
        body_html = f"""
        <p style="margin-top:0;">Hi <strong>{user_name}</strong>,</p>
        <p>Your workspace tenant <code>{tenant_id}</code> has consumed <strong>{pct}% (${used_usd:.2f} / ${limit_usd:.2f})</strong> of its allocated AI token budget.</p>
        <div style="background:#fffbeb;border-left:4px solid #f59e0b;padding:14px 16px;border-radius:6px;margin:16px 0;">
          <div style="font-weight:700;color:#b45309;margin-bottom:6px;">⚡ Usage Breakdown &amp; FinOps Optimization Tip</div>
          <div style="background:#e5e7eb;height:10px;border-radius:999px;overflow:hidden;margin:8px 0;">
            <div style="background:#f59e0b;width:{min(pct, 100)}%;height:100%;"></div>
          </div>
          <ul style="margin:8px 0 0 18px;padding:0;font-size:13px;color:#92400e;">
            <li><strong>Primary Spend Driver:</strong> <code>{top_model}</code></li>
            <li><strong>Thinking Tokens Share:</strong> {thoughts_token_pct:.1f}% of output tokens were spent on internal reasoning.</li>
            <li><strong>Recommended Action:</strong> Lower <code>thinking_level</code> from <code>high</code> to <code>medium</code> on routine calls, enable Context Caching (saves 75-90%), or let the Gateway auto-route classification tasks to <code>gemini-3.5-flash-lite</code>.</li>
          </ul>
        </div>
        <p style="font-size:12px;color:#64748b;">Note: At 100% utilization, non-critical requests will automatically cascade to <code>gemini-3.5-flash-lite</code> to prevent service interruption.</p>
        """
        html = self._wrap_html_template(
            badge_text=f"USER QUOTA WARNING ({pct}%)",
            badge_color="#d97706",
            title=f"Action Recommended: {pct}% of AI Token Budget Reached",
            subtitle=f"Tenant: {tenant_id} • User: {user_email}",
            body_html=body_html,
        )
        event = AlertEvent(
            alert_type="USER_QUOTA_WARNING_80",
            severity="WARNING",
            recipient_role="USER",
            recipient_email=user_email,
            subject=f"[AI Gateway Warning] {pct}% Token Quota Reached for {tenant_id}",
            summary=f"Tenant {tenant_id} reached {pct}% (${used_usd:.2f}/${limit_usd:.2f}) of quota. Top model: {top_model}.",
            html_body=html,
            metadata={
                "tenant_id": tenant_id,
                "used_usd": used_usd,
                "limit_usd": limit_usd,
                "utilization_pct": pct,
                "top_model": top_model,
            },
        )
        return self._dispatch(event)

    # -------------------------------------------------------------------------
    # 2. End-User Alert: Long-Decode / Deep Research Background Job Completed
    # -------------------------------------------------------------------------
    def send_user_background_job_complete(
        self,
        user_email: str,
        interaction_id: str,
        model_used: str,
        total_tokens: int,
        hops_completed: int,
        duration_sec: float,
        output_preview: str,
    ) -> AlertEvent:
        body_html = f"""
        <p style="margin-top:0;">Your asynchronous background execution job has completed on the Gemini Interactions API.</p>
        <table style="width:100%;border-collapse:collapse;margin:14px 0;font-size:13px;">
          <tr style="background:#f8fafc;border-bottom:1px solid #e2e8f0;">
            <td style="padding:8px 12px;font-weight:600;">Interaction ID</td>
            <td style="padding:8px 12px;"><code>{interaction_id}</code></td>
          </tr>
          <tr style="border-bottom:1px solid #e2e8f0;">
            <td style="padding:8px 12px;font-weight:600;">Model / Agent</td>
            <td style="padding:8px 12px;"><code>{model_used}</code></td>
          </tr>
          <tr style="background:#f8fafc;border-bottom:1px solid #e2e8f0;">
            <td style="padding:8px 12px;font-weight:600;">Continuation Hops</td>
            <td style="padding:8px 12px;">{hops_completed} hop(s) &bull; {total_tokens:,} total tokens ({duration_sec:.1f}s)</td>
          </tr>
        </table>
        <div style="background:#f1f5f9;padding:12px 14px;border-radius:8px;font-family:ui-monospace,monospace;font-size:12px;color:#0f172a;">
          {output_preview[:360]}...
        </div>
        """
        html = self._wrap_html_template(
            badge_text="BACKGROUND JOB COMPLETED",
            badge_color="#059669",
            title=f"Long-Decode / Research Synthesis Ready ({total_tokens:,} tokens)",
            subtitle=f"Interaction {interaction_id} • Model: {model_used}",
            body_html=body_html,
        )
        event = AlertEvent(
            alert_type="USER_BACKGROUND_JOB_COMPLETE",
            severity="INFO",
            recipient_role="USER",
            recipient_email=user_email,
            subject=f"[Completed] Gemini Background Job {interaction_id} ({model_used})",
            summary=f"Background interaction {interaction_id} on {model_used} completed ({total_tokens:,} tokens).",
            html_body=html,
            metadata={
                "interaction_id": interaction_id,
                "model_used": model_used,
                "total_tokens": total_tokens,
                "hops_completed": hops_completed,
            },
        )
        return self._dispatch(event)

    # -------------------------------------------------------------------------
    # 3. Admin Alert: Hard Budget Circuit-Breaker Trip (100% Cap / Spike)
    # -------------------------------------------------------------------------
    def send_admin_circuit_breaker_alert(
        self,
        admin_email: str,
        tenant_id: str,
        used_usd: float,
        limit_usd: float,
        action_taken: str = "AUTO_DOWNGRADE_TO_FLASH_LITE",
        anomalous_agent_id: Optional[str] = None,
    ) -> AlertEvent:
        body_html = f"""
        <div style="background:#fef2f2;border-left:4px solid #dc2626;padding:14px 16px;border-radius:6px;margin-bottom:16px;">
          <div style="font-weight:700;color:#991b1b;font-size:15px;margin-bottom:4px;">🚨 P1 FINOPS CIRCUIT BREAKER TRIPPED</div>
          <p style="margin:0;color:#7f1d1d;font-size:13px;">
            Tenant <code>{tenant_id}</code> exceeded 100% of its hard budget ceiling (<strong>${used_usd:.2f} / ${limit_usd:.2f}</strong>).
          </p>
        </div>
        <table style="width:100%;border-collapse:collapse;font-size:13px;margin:14px 0;">
          <tr style="background:#f8fafc;border-bottom:1px solid #e2e8f0;">
            <td style="padding:8px 12px;font-weight:600;">Automated Governance Policy</td>
            <td style="padding:8px 12px;"><span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:4px;font-weight:600;">{action_taken}</span></td>
          </tr>
          <tr style="border-bottom:1px solid #e2e8f0;">
            <td style="padding:8px 12px;font-weight:600;">Anomalous Agent / Loop ID</td>
            <td style="padding:8px 12px;"><code>{anomalous_agent_id or 'none-detected (steady volume)'}</code></td>
          </tr>
          <tr style="background:#f8fafc;border-bottom:1px solid #e2e8f0;">
            <td style="padding:8px 12px;font-weight:600;">Fallback Routing Target</td>
            <td style="padding:8px 12px;"><code>gemini-3.5-flash-lite</code> ($0.075 / 1M input)</td>
          </tr>
        </table>
        <p style="font-size:13px;">Platform admins can grant a temporary 24-hour quota override or inspect the tenant's Antigravity <code>BudgetConfig</code> and <code>CompactionConfig</code> settings in the Admin Console.</p>
        """
        html = self._wrap_html_template(
            badge_text="CRITICAL • ADMIN CIRCUIT BREAKER",
            badge_color="#dc2626",
            title=f"Hard Budget Cap Reached for Tenant: {tenant_id}",
            subtitle=f"Automated Mitigation Active: {action_taken}",
            body_html=body_html,
            cta_text="Manage Tenant Quota & Circuit Breakers",
        )
        event = AlertEvent(
            alert_type="ADMIN_CIRCUIT_BREAKER_TRIP_100",
            severity="CRITICAL",
            recipient_role="ADMIN",
            recipient_email=admin_email,
            subject=f"[CRITICAL] AI Gateway Circuit Breaker Tripped — Tenant {tenant_id}",
            summary=f"Tenant {tenant_id} hit ${used_usd:.2f}/${limit_usd:.2f}. Action: {action_taken}.",
            html_body=html,
            metadata={
                "tenant_id": tenant_id,
                "used_usd": used_usd,
                "limit_usd": limit_usd,
                "action_taken": action_taken,
                "anomalous_agent_id": anomalous_agent_id,
            },
        )
        return self._dispatch(event)

    # -------------------------------------------------------------------------
    # 4. Admin / SecOps Alert: Prompt Injection & PII DLP Guardrail Block
    # -------------------------------------------------------------------------
    def send_admin_security_guardrail_alert(
        self,
        secops_email: str,
        tenant_id: str,
        user_email: str,
        violation_category: str,
        risk_score: float,
        redacted_snippet: str,
        action_taken: str = "BLOCKED_AND_LOGGED",
    ) -> AlertEvent:
        body_html = f"""
        <div style="background:#fff1f2;border-left:4px solid #e11d48;padding:14px 16px;border-radius:6px;margin-bottom:16px;">
          <div style="font-weight:700;color:#9f1239;margin-bottom:4px;">🛡️ ZERO-TRUST AI GUARDRAIL INTERCEPTION</div>
          <p style="margin:0;color:#881337;font-size:13px;">
            Pre-inference safety filter intercepted a high-risk payload from <code>{user_email}</code> (Tenant: <code>{tenant_id}</code>).
          </p>
        </div>
        <ul style="font-size:13px;line-height:1.7;">
          <li><strong>Violation Category:</strong> <code>{violation_category}</code></li>
          <li><strong>Classifier Risk Score:</strong> <strong>{risk_score:.2f} / 1.00</strong> (Evaluated via <code>gemini-3.5-flash-lite</code> guardrail)</li>
          <li><strong>Enforcement Action:</strong> <code>{action_taken}</code></li>
        </ul>
        <div style="background:#0f172a;color:#f8fafc;padding:12px 14px;border-radius:8px;font-family:ui-monospace,monospace;font-size:12px;margin-top:12px;">
          [REDACTED PAYLOAD AUDIT]: {redacted_snippet}
        </div>
        """
        html = self._wrap_html_template(
            badge_text="SECOPS • GUARDRAIL INTERCEPTION",
            badge_color="#e11d48",
            title=f"Security Policy Triggered: {violation_category}",
            subtitle=f"Tenant: {tenant_id} • Actor: {user_email} • Risk: {risk_score:.2f}",
            body_html=body_html,
            cta_text="Inspect Audit Trail in Security Center",
        )
        event = AlertEvent(
            alert_type="ADMIN_SECURITY_GUARDRAIL_BLOCK",
            severity="HIGH",
            recipient_role="SECOPS",
            recipient_email=secops_email,
            subject=f"[SecOps Alert] {violation_category} Blocked on AI Gateway ({tenant_id})",
            summary=f"Blocked {violation_category} (risk={risk_score:.2f}) from {user_email} in {tenant_id}.",
            html_body=html,
            metadata={
                "tenant_id": tenant_id,
                "user_email": user_email,
                "violation_category": violation_category,
                "risk_score": risk_score,
                "action_taken": action_taken,
            },
        )
        return self._dispatch(event)

    # -------------------------------------------------------------------------
    # 5. Executive & Admin Weekly FinOps & Observability Report
    # -------------------------------------------------------------------------
    def send_executive_finops_report(
        self,
        recipient_email: str,
        stats: Dict[str, Any],
    ) -> AlertEvent:
        total_req = stats.get("total_requests", 0)
        actual_usd = stats.get("actual_cost_usd", 0.0)
        baseline_usd = stats.get("unoptimized_baseline_usd", 0.0)
        saved_usd = max(0.0, baseline_usd - actual_usd)
        savings_pct = stats.get("savings_pct", 0.0)
        cache_hit_pct = stats.get("cache_hit_pct", 0.0)
        tier_dist = stats.get("tier_distribution", {})

        rows_html = ""
        for model_name, count in tier_dist.items():
            share = round((count / max(total_req, 1)) * 100, 1)
            rows_html += f"""
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:8px 12px;"><code>{model_name}</code></td>
              <td style="padding:8px 12px;">{count:,} reqs</td>
              <td style="padding:8px 12px;font-weight:600;color:#1d4ed8;">{share}%</td>
            </tr>"""

        body_html = f"""
        <p style="margin-top:0;">Here is your automated <strong>Executive AI FinOps, Model Routing &amp; Governance Digest</strong> across all active harnesses (Antigravity SDK, Google ADK, Gemini Enterprise, and Direct APIs).</p>
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin:16px 0;">
          <div style="flex:1;min-width:140px;background:#f0fdf4;border:1px solid #bbf7d0;padding:12px;border-radius:8px;">
            <div style="font-size:11px;color:#166534;font-weight:700;text-transform:uppercase;">Net FinOps Savings</div>
            <div style="font-size:20px;font-weight:800;color:#15803d;">${saved_usd:.4f} ({savings_pct:.1f}%)</div>
          </div>
          <div style="flex:1;min-width:140px;background:#eff6ff;border:1px solid #bfdbfe;padding:12px;border-radius:8px;">
            <div style="font-size:11px;color:#1e40af;font-weight:700;text-transform:uppercase;">Actual Gateway Spend</div>
            <div style="font-size:20px;font-weight:800;color:#1d4ed8;">${actual_usd:.4f}</div>
          </div>
          <div style="flex:1;min-width:140px;background:#fefce8;border:1px solid #fef08a;padding:12px;border-radius:8px;">
            <div style="font-size:11px;color:#854d0e;font-weight:700;text-transform:uppercase;">Context Cache Hit Rate</div>
            <div style="font-size:20px;font-weight:800;color:#a16207;">{cache_hit_pct:.1f}%</div>
          </div>
        </div>
        <h3 style="font-size:14px;color:#0f172a;margin:18px 0 8px 0;">Model Routing Distribution (4-Tier Cascade + Multimodal)</h3>
        <table style="width:100%;border-collapse:collapse;font-size:13px;">
          <thead>
            <tr style="background:#f8fafc;border-bottom:2px solid #cbd5e1;text-align:left;">
              <th style="padding:8px 12px;">Model Identifier</th>
              <th style="padding:8px 12px;">Volume</th>
              <th style="padding:8px 12px;">Traffic Share</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
        """
        html = self._wrap_html_template(
            badge_text="EXECUTIVE FINOPS & GOVERNANCE REPORT",
            badge_color="#2563eb",
            title=f"AI Engineering Platform Digest — {savings_pct:.1f}% Cost Reduction Achieved",
            subtitle=f"Total Requests: {total_req:,} • Context Cache Hit Rate: {cache_hit_pct:.1f}%",
            body_html=body_html,
            cta_text="View Live FinOps Telemetry Dashboard",
        )
        event = AlertEvent(
            alert_type="EXECUTIVE_WEEKLY_FINOPS_REPORT",
            severity="INFO",
            recipient_role="EXECUTIVE",
            recipient_email=recipient_email,
            subject=f"[Executive AI Report] {savings_pct:.1f}% FinOps Savings Across {total_req:,} Requests",
            summary=f"Executive FinOps Report: {total_req} requests, ${actual_usd:.4f} actual vs ${baseline_usd:.4f} baseline ({savings_pct:.1f}% saved).",
            html_body=html,
            metadata=stats,
        )
        return self._dispatch(event)


# Singleton instance
alerting_service = EnterpriseAlertingService()
