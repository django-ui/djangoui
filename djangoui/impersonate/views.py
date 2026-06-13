"""Picker, start, and stop views."""
from __future__ import annotations

import logging
from datetime import datetime

from django.contrib.auth import get_user_model, login, logout
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from . import conf
from .auth import is_allowed
from .tokens import acquire_token
from .userinfo import get_userinfo

logger = logging.getLogger("impersonate")


# ---------------------------------------------------------------------------
@require_http_methods(["GET"])
def picker(request):
    if not is_allowed(request):
        return HttpResponseForbidden("Not authorized to impersonate.")
    accounts = [
        {"name": k, "label": (v or {}).get("label", k)}
        for k, v in conf.accounts().items()
    ]
    snap = request.session.get(conf.SESSION_SNAPSHOT_KEY)
    return render(request, conf.picker_template(), {
        "accounts":          accounts,
        "impersonating_as":  request.session.get(conf.SESSION_IMPERSONATING_AS_KEY),
        "original_username": (snap or {}).get("username"),
    })


# ---------------------------------------------------------------------------
@csrf_protect
@require_http_methods(["POST"])
def start(request):
    if not is_allowed(request):
        return HttpResponseForbidden("Not authorized to impersonate.")

    if request.session.get(conf.SESSION_SNAPSHOT_KEY):
        return HttpResponse("Already impersonating; stop first.", status=409)

    name = (request.POST.get("account") or "").strip()
    cfg = conf.accounts().get(name)
    if not cfg:
        return HttpResponse(f"Unknown account: {name}", status=400)

    tok = acquire_token(cfg)
    if not tok or "access_token" not in tok:
        return HttpResponse("Token exchange failed; check server logs.",
                            status=502)

    user_info = get_userinfo(tok["access_token"]) or {}
    target_username = (
        user_info.get("preferred_username")
        or (user_info.get("email") or "").split("@")[0]
        or cfg.get("username")
        or name
    ).lower()

    User = get_user_model()
    target_user, _created = User.objects.get_or_create(
        username=target_username,
        defaults={
            "email":      user_info.get("email", "") or "",
            "first_name": user_info.get("given_name", "") or "",
            "last_name":  user_info.get("family_name", "") or "",
        },
    )

    keys = conf.session_keys()
    snap = {
        "user_pk":      request.user.pk,
        "username":     request.user.username,
        "ad_groups":    list(request.session.get(keys["ad_groups"]) or []),
        "employee_id":  request.session.get(keys["employee_id"], ""),
        "user_info":    request.session.get(keys["user_info"]),
        "access_token": request.session.get(keys["access_token"]),
        "id_token":     request.session.get(keys["id_token"]),
    }

    logger.warning(
        "IMPERSONATION START: %s -> %s (account=%s)",
        snap["username"], target_username, name,
    )

    login(request, target_user, backend=conf.auth_backend())

    request.session[keys["user_info"]]    = user_info
    request.session[keys["ad_groups"]]    = [
        g.lower() for g in (user_info.get("groups") or [])
    ]
    request.session[keys["employee_id"]]  = (user_info.get("employee_id") or "").lower()
    request.session[keys["user_info_ts"]] = datetime.now().timestamp()
    request.session[keys["access_token"]] = tok.get("access_token")
    request.session[keys["id_token"]]     = tok.get("id_token")
    request.session[conf.SESSION_SNAPSHOT_KEY]         = snap
    request.session[conf.SESSION_IMPERSONATING_AS_KEY] = target_username
    request.session.modified = True

    return redirect(request.POST.get("next") or "/")


# ---------------------------------------------------------------------------
@csrf_protect
@require_http_methods(["POST"])
def stop(request):
    snap = request.session.get(conf.SESSION_SNAPSHOT_KEY)
    if not snap:
        return redirect("/")

    User = get_user_model()
    try:
        original = User.objects.get(pk=snap["user_pk"])
    except User.DoesNotExist:
        logger.error(
            "IMPERSONATION STOP failed: original user pk=%s missing; "
            "forcing re-login.", snap.get("user_pk"),
        )
        logout(request)
        return redirect("/")

    logger.warning(
        "IMPERSONATION STOP: %s -> %s",
        request.user.username, original.username,
    )

    keys = conf.session_keys()
    login(request, original, backend=conf.auth_backend())

    request.session[keys["user_info"]]    = snap.get("user_info")
    request.session[keys["ad_groups"]]    = snap.get("ad_groups") or []
    request.session[keys["employee_id"]]  = snap.get("employee_id") or ""
    request.session[keys["user_info_ts"]] = datetime.now().timestamp()
    request.session[keys["access_token"]] = snap.get("access_token")
    request.session[keys["id_token"]]     = snap.get("id_token")
    request.session.pop(conf.SESSION_SNAPSHOT_KEY, None)
    request.session.pop(conf.SESSION_IMPERSONATING_AS_KEY, None)
    request.session.modified = True

    return redirect(request.POST.get("next") or "/")
