"""
Authentication & Authorization Security Module.
Provides JWT session token generation, verification, and built-in Demo User credentials.
"""

import time, hmac, hashlib, base64, json
from typing import Dict, Any, Optional

SECRET_KEY = "wealthpulse_enterprise_super_secret_jwt_key_2026"

def create_jwt_token(payload: Dict[str, Any], expires_in_seconds: int = 86400) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = payload.copy()
    payload["exp"] = int(time.time()) + expires_in_seconds
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signature_raw = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signature_raw, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        
        # Verify Signature
        sig_raw = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(SECRET_KEY.encode(), sig_raw, hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(sig_b64 + "==")
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
            
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "==").decode())
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None
