import pytest
from unittest.mock import patch, MagicMock
from backend.services.turnstile_service import verify_turnstile_token
from backend.config import settings

@pytest.mark.asyncio
async def test_verify_turnstile_token_empty():
    res = await verify_turnstile_token(None)
    assert res is False

    res_empty = await verify_turnstile_token("   ")
    assert res_empty is False

@pytest.mark.asyncio
async def test_verify_turnstile_token_always_pass_key():
    # Official Cloudflare Turnstile test key 1x0000000000000000000000000000000AA always passes
    with patch.object(settings, "DISABLE_CAPTCHA_VERIFICATION", False):
        res = await verify_turnstile_token("1x0000000000000000000000000000000AA")
        assert res is True

@pytest.mark.asyncio
async def test_verify_turnstile_token_disabled_setting():
    with patch.object(settings, "DISABLE_CAPTCHA_VERIFICATION", True):
        res = await verify_turnstile_token(None)
        assert res is True

@pytest.mark.asyncio
async def test_verify_turnstile_token_api_failure():
    with patch.object(settings, "DISABLE_CAPTCHA_VERIFICATION", False):
        with patch.object(settings, "CLOUDFLARE_TURNSTILE_SECRET_KEY", "2x0000000000000000000000000000000AA"):
            # Secret key 2x... always fails on siteverify
            res = await verify_turnstile_token("some_invalid_token")
            assert res is False
