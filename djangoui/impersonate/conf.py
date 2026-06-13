"""Read all configuration from Django settings with sane fallbacks.

Every getter is a function so settings can be reloaded in tests without
re-importing modules that captured values at import time.
"""
from __future__ import annotations

from django.conf import settings


# ---------------------------------------------------------------------------
# OIDC OP endpoints / client defaults (reuse the host project's OIDC settings).
# ---------------------------------------------------------------------------
def token_endpoint() -> str | None:
    return getattr(settings, "OIDC_OP_TOKEN_ENDPOINT", None)


def userinfo_endpoint() -> str | None:
    return getattr(settings, "OIDC_OP_USER_ENDPOINT", None)


def default_client_id() -> str:
    return getattr(settings, "OIDC_RP_CLIENT_ID", "")


def default_client_secret() -> str:
    return getattr(settings, "OIDC_RP_CLIENT_SECRET", "")


def default_scopes() -> str:
    return getattr(settings, "OIDC_RP_SCOPES",
                   "openid email profile groups preferred_username")


def verify_ssl():
    return getattr(settings, "OIDC_VERIFY_SSL", True)


# ---------------------------------------------------------------------------
# Authorization gate.
# ---------------------------------------------------------------------------
def allowed_groups() -> list[str]:
    return [
        g.lower().replace("\\\\", "\\")
        for g in (getattr(settings, "IMPERSONATION_ALLOWED_GROUPS", []) or [])
    ]


def allowed_users() -> set[str]:
    return set(getattr(settings, "IMPERSONATION_ALLOWED_USERS", []) or [])


# ---------------------------------------------------------------------------
# Accounts catalog.
# ---------------------------------------------------------------------------
def accounts() -> dict:
    return getattr(settings, "IMPERSONATION_ACCOUNTS", {}) or {}


# ---------------------------------------------------------------------------
# Auth backend used when swapping users via django.contrib.auth.login().
# Defaults to the first entry in AUTHENTICATION_BACKENDS.
# ---------------------------------------------------------------------------
def auth_backend() -> str:
    explicit = getattr(settings, "IMPERSONATION_AUTH_BACKEND", None)
    if explicit:
        return explicit
    backends = getattr(settings, "AUTHENTICATION_BACKENDS", []) or []
    if backends:
        return backends[0]
    return "django.contrib.auth.backends.ModelBackend"


# ---------------------------------------------------------------------------
# Session-key names. Override these if your host project reads user_info /
# ad_groups from different session keys.
# ---------------------------------------------------------------------------
_DEFAULT_SESSION_KEYS = {
    "user_info":      "user_info",
    "ad_groups":      "ad_groups",
    "employee_id":    "employee_id",
    "user_info_ts":   "user_info_ts",
    "access_token":   "oidc_access_token",
    "id_token":       "oidc_id_token",
}


def session_keys() -> dict:
    overrides = getattr(settings, "IMPERSONATION_SESSION_KEYS", {}) or {}
    merged = dict(_DEFAULT_SESSION_KEYS)
    merged.update(overrides)
    return merged


# Internal session keys (always namespaced; not user-overridable).
SESSION_SNAPSHOT_KEY = "impersonator_snapshot"
SESSION_IMPERSONATING_AS_KEY = "impersonating_as"


# ---------------------------------------------------------------------------
# Template used by /impersonate/ picker. Override to wrap in your own layout.
# ---------------------------------------------------------------------------
def picker_template() -> str:
    return getattr(settings, "IMPERSONATION_PICKER_TEMPLATE",
                   "impersonate/picker.html")
