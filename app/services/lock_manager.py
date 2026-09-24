import time
import threading
from typing import Optional, Tuple, Dict, Any


class FieldLockManager:
    def __init__(self):
        self._lock = threading.Lock()
        # Key: (record_id, field_name) -> {"user_id": str, "expires_at": float}
        self._registry: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def acquire_field_lock(
        self,
        record_id: str,
        field_name: str,
        user_id: str,
        ttl_seconds: int = 30,
    ) -> Tuple[bool, Optional[str]]:
        now = time.time()
        key = (str(record_id), str(field_name))

        with self._lock:
            existing = self._registry.get(key)
            if existing:
                if existing["expires_at"] > now:
                    if existing["user_id"] != user_id:
                        return False, existing["user_id"]
                    # Same user renewing lock
                    existing["expires_at"] = now + ttl_seconds
                    return True, user_id
                else:
                    # Expired lock
                    del self._registry[key]

            # Lock is free or expired; acquire new lock
            self._registry[key] = {
                "user_id": user_id,
                "expires_at": now + ttl_seconds,
            }
            return True, user_id

    def release_field_lock(
        self,
        record_id: str,
        field_name: str,
        user_id: str,
    ) -> bool:
        now = time.time()
        key = (str(record_id), str(field_name))

        with self._lock:
            existing = self._registry.get(key)
            if not existing:
                return True
            if existing["expires_at"] <= now:
                del self._registry[key]
                return True
            if existing["user_id"] == user_id:
                del self._registry[key]
                return True
            return False

    def get_active_locks(self, record_id: str) -> Dict[str, Dict[str, Any]]:
        now = time.time()
        rec_id = str(record_id)
        result: Dict[str, Dict[str, Any]] = {}

        with self._lock:
            keys_to_delete = []
            for (rid, fname), data in self._registry.items():
                if rid == rec_id:
                    if data["expires_at"] > now:
                        result[fname] = {
                            "user_id": data["user_id"],
                            "expires_in": max(0.0, round(data["expires_at"] - now, 2)),
                        }
                    else:
                        keys_to_delete.append((rid, fname))

            for k in keys_to_delete:
                del self._registry[k]

        return result

    def clear(self):
        with self._lock:
            self._registry.clear()


# Global in-memory lock manager instance
lock_manager = FieldLockManager()
