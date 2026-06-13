"""Authorization gate: who is allowed to impersonate."""
from __future__ import annotations

from . import conf


def is_allowed(request) -> bool:
    """True if the request's *real* user may impersonate.

    * Django superusers always pass.
    * Usernames listed in IMPERSONATION_ALLOWED_USERS pass.
    * Users in any IMPERSONATION_ALLOWED_GROUPS AD group pass.

    While impersonating, the AD-group check evaluates against the snapshot of
    the real user's groups, so an impersonated account cannot re-impersonate.
    """
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True

    snap = request.session.get(conf.SESSION_SNAPSHOT_KEY)
    real_username = (snap or {}).get("username") or user.username
    if real_username in conf.allowed_users():
        return True

    groups = set(conf.allowed_groups())
    if not groups:
        return False

    if snap:
        my_groups = set(snap.get("ad_groups") or [])
    else:
        ad_groups_key = conf.session_keys()["ad_groups"]
        my_groups = set(request.session.get(ad_groups_key) or [])

    return bool(groups & my_groups)
