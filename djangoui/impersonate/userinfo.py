"""Tiny OIDC userinfo client. Self-contained so the app has no dependency on
the host project's OIDC code."""
from __future__ import annotations

import logging

import requests

from . import conf

logger = logging.getLogger("impersonate")


def get_userinfo(access_token: str) -> dict | None:
    endpoint = conf.userinfo_endpoint()
    if not endpoint or not access_token:
        return None
    try:
        resp = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
            verify=conf.verify_ssl(),
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        body = getattr(getattr(e, "response", None), "text", "")
        logger.error("userinfo failed: %s | body=%s", e, body)
    except ValueError:
        logger.error("userinfo returned non-JSON body.")
    return None
