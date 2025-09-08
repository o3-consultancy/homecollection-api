import time
import hmac
import hashlib
import base64
from app.core.config import settings


def sign_action(container_id: str, now: int | None = None) -> str:
    now = now or int(time.time())
    msg = f"{container_id}.{now}".encode()
    mac = hmac.new(settings.QR_HMAC_SECRET.encode(),
                   msg, hashlib.sha256).digest()
    tok = base64.urlsafe_b64encode(mac).decode().rstrip("=")
    return f"{now}.{tok}"


def verify_action(container_id: str, token: str) -> bool:
    try:
        ts_str, mac_b64 = token.split(".", 1)
        ts = int(ts_str)
        if int(time.time()) - ts > settings.QR_SIG_TTL_SECONDS:
            return False
        msg = f"{container_id}.{ts}".encode()
        expected = base64.urlsafe_b64encode(
            hmac.new(settings.QR_HMAC_SECRET.encode(),
                     msg, hashlib.sha256).digest()
        ).decode().rstrip("=")
        return hmac.compare_digest(mac_b64, expected)
    except Exception:
        return False
