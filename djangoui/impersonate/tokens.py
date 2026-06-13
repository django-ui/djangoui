"""Acquire OIDC access tokens for an impersonation target.

Supported grants per account (declared via the ``grant`` key):

  * ``client_credentials`` (default) - requires ``client_id`` / ``client_secret``.
    If the OAuth client is bound to an AD account (e.g. PingFederate's
    "Linked Resource Account"), the token will carry that account's identity.
  * ``password`` (ROPC) - requires ``username`` / ``password``. Requires the
    OP client to allow this grant; many orgs disable it.
  * ``refresh_token`` - requires a pre-captured ``refresh_token`` (e.g. one
    bootstrapped via an interactive login with ``offline_access`` scope).
"""
from __future__ import annotations

import logging

import requests

from . import conf

logger = logging.getLogger("impersonate")


def acquire_token(account_cfg: dict) -> dict | None:
    endpoint = conf.token_endpoint()
    if not endpoint:
        logger.error("OIDC_OP_TOKEN_ENDPOINT is not configured.")
        return None

    grant = (account_cfg.get("grant") or "client_credentials").lower()
    client_id     = account_cfg.get("client_id",     conf.default_client_id())
    client_secret = account_cfg.get("client_secret", conf.default_client_secret())
    scope         = account_cfg.get("scope",         conf.default_scopes())

    if grant == "client_credentials":
        data = {
            "grant_type":    "client_credentials",
            "scope":         scope,
            "client_id":     client_id,
            "client_secret": client_secret,
        }
    elif grant == "password":
        data = {
            "grant_type":    "password",
            "username":      account_cfg["username"],
            "password":      account_cfg["password"],
            "scope":         scope,
            "client_id":     client_id,
            "client_secret": client_secret,
        }
    elif grant == "refresh_token":
        data = {
            "grant_type":    "refresh_token",
            "refresh_token": account_cfg["refresh_token"],
            "scope":         scope,
            "client_id":     client_id,
            "client_secret": client_secret,
        }
    else:
        logger.error("Unsupported grant for impersonation: %r", grant)
        return None

    try:
        resp = requests.post(
            endpoint,
            data=data,
            timeout=15,
            verify=conf.verify_ssl(),
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        body = getattr(getattr(e, "response", None), "text", "")
        logger.error("Token request (grant=%s) failed: %s | body=%s",
                     grant, e, body)
        return None
