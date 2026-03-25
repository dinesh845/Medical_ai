"""
Privacy and security utilities for healthcare-style data handling.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any, List

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False


class DataPrivacyFramework:
    """Provides anonymization, encryption, and simple audit hooks."""

    def __init__(self) -> None:
        self.key_path = os.path.join("data", "secure.key")
        self.audit_path = os.path.join("data", "audit_log.json")
        os.makedirs("data", exist_ok=True)
        self.fernet = self._load_or_create_fernet()

    def _load_or_create_fernet(self):
        if not CRYPTO_AVAILABLE:
            return None
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as f:
                key = f.read().strip()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as f:
                f.write(key)
        return Fernet(key)

    def anonymize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        safe = dict(record)
        patient_id = safe.get("patient_id", "unknown")
        name = safe.get("patient_name", "")

        safe["patient_hash"] = self._hash_text(f"{patient_id}|{name}")
        safe.pop("patient_name", None)

        if "email" in safe:
            safe["email"] = self._mask_email(str(safe["email"]))
        if "phone" in safe:
            safe["phone"] = self._mask_phone(str(safe["phone"]))

        safe["privacy"] = {
            "anonymized": True,
            "anonymized_at": datetime.utcnow().isoformat(),
        }
        return safe

    def encrypt_json(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        blob = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        if self.fernet:
            encrypted = self.fernet.encrypt(blob)
            mode = "fernet"
        else:
            encrypted = base64.b64encode(blob)
            mode = "base64-fallback"

        return {
            "mode": mode,
            "payload": encrypted.decode("utf-8"),
            "created_at": datetime.utcnow().isoformat(),
        }

    def decrypt_json(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raw = payload.get("payload", "").encode("utf-8")
        mode = payload.get("mode")

        if mode == "fernet" and self.fernet:
            blob = self.fernet.decrypt(raw)
        else:
            blob = base64.b64decode(raw)
        return json.loads(blob.decode("utf-8"))

    def enforce_role(self, role: str, allowed_roles: List[str]) -> bool:
        return role in allowed_roles

    def write_audit_event(self, action: str, role: str, metadata: Dict[str, Any] | None = None) -> None:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "role": role,
            "metadata": metadata or {},
        }
        logs = []
        if os.path.exists(self.audit_path):
            try:
                with open(self.audit_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(entry)
        with open(self.audit_path, "w", encoding="utf-8") as f:
            json.dump(logs[-2000:], f, indent=2)

    @staticmethod
    def _hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _mask_email(email: str) -> str:
        if "@" not in email:
            return "***"
        username, domain = email.split("@", 1)
        visible = username[:2] if len(username) > 2 else username[:1]
        return f"{visible}***@{domain}"

    @staticmethod
    def _mask_phone(phone: str) -> str:
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) < 4:
            return "***"
        return "***-***-" + digits[-4:]
