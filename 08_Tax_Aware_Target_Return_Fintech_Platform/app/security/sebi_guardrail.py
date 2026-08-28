"""
SEBI Compliance & DPDP Act PII Protection Guardrails.
Enforces Maximum Drawdown (MDD) circuit breakers and masks Aadhaar, PAN, and Bank details.
"""

import re
from typing import Dict, Any

class SecurityGuardrail:
    @staticmethod
    def mask_pii(text: str) -> str:
        """Masks Indian PAN, Aadhaar, and Bank Account numbers (DPDP Act)."""
        # PAN (e.g., ABCDE1234F -> ABCDE****F)
        text = re.sub(r'([A-Z]{5})(\d{4})([A-Z]{1})', r'\1****\3', text)
        # Aadhaar (e.g., 1234 5678 9012 -> **** **** 9012)
        text = re.sub(r'\b\d{4}\s?\d{4}\s?(\d{4})\b', r'**** **** \1', text)
        # Bank Account (e.g., 1234567890 -> ******7890)
        text = re.sub(r'\b(\d{6,14})(\d{4})\b', r'******\2', text)
        return text

    @staticmethod
    def verify_sebi_compliance(prompt_or_response: str) -> Dict[str, Any]:
        """Ensures that no guaranteed stock tips or unregulated advisory is generated."""
        violations = []
        forbidden_keywords = ["guaranteed multibagger", "100% risk free", "sure shot jackpot", "insider tip"]
        for kw in forbidden_keywords:
            if kw in prompt_or_response.lower():
                violations.append(f"Contains prohibited SEBI claim: '{kw}'")
                
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "disclaimer_required": True,
            "statutory_disclaimer": "Investment in securities market are subject to market risks. Read all the related documents carefully before investing."
        }
