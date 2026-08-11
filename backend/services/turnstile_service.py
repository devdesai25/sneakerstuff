import httpx
import logging
from typing import Optional
from backend.config import settings

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

async def verify_turnstile_token(token: Optional[str], remote_ip: Optional[str] = None) -> bool:
    """
    Verifies a Cloudflare Turnstile token against Cloudflare's siteverify endpoint.
    Returns True if valid, False otherwise.
    """
    if getattr(settings, "DISABLE_CAPTCHA_VERIFICATION", False):
        return True

    if not token or not token.strip():
        return False

    payload = {
        "secret": settings.CLOUDFLARE_TURNSTILE_SECRET_KEY,
        "response": token.strip(),
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(TURNSTILE_VERIFY_URL, data=payload)
            if resp.status_code != 200:
                logger.warning(f"Cloudflare Turnstile API returned status code {resp.status_code}")
                return False
            data = resp.json()
            return bool(data.get("success", False))
    except Exception as exc:
        logger.error(f"Error communicating with Cloudflare Turnstile API: {exc}")
        return False
