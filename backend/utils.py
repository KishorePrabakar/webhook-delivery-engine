import hmac
import hashlib
import time
import json
from typing import Any, Dict

def sign_payload(payload: Dict[str, Any], secret: str) -> str:
    timestamp = str(int(time.time()))
    payload_str = json.dumps(payload, sort_keys=True)
    signed_payload = f"{timestamp}.{payload_str}"
    
    signature = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return f"t={timestamp},v1={signature}"

def verify_signature(header: str, payload: Dict[str, Any], secret: str) -> bool:
    try:
        parts = dict(x.split('=') for x in header.split(','))
        timestamp = parts.get('t')
        signature = parts.get('v1')
        
        if not timestamp or not signature:
            return False
            
        # Check timestamp expiration (5 mins)
        if int(time.time()) - int(timestamp) > 300:
            return False
            
        payload_str = json.dumps(payload, sort_keys=True)
        expected_signature = hmac.new(
            secret.encode(),
            f"{timestamp}.{payload_str}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception:
        return False
