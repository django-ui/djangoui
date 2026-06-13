"""Template helpers exposed to host-project templates.

Usage in any base/layout template::

    {% load impersonate_tags %}
    {% impersonation_banner %}      {# floating bottom-right pill, only if active #}
    {% impersonation_menu %}        {# admin-only dropdown submenu of accounts  #}

Or, if you only need the boolean for custom rendering::

    {% can_impersonate request as ok %}
    {% if ok %} ... {% endif %}
"""
from __future__ import annotations

from django import template

from .. import conf
from ..auth import is_allowed

register = template.Library()


@register.simple_tag(name="can_impersonate")
def can_impersonate_tag(request):
    try:
        return bool(is_allowed(request))
    except Exception:
        return False


@register.simple_tag(name="impersonation_accounts")
def impersonation_accounts_tag():
    return [
        {"name": k, "label": (v or {}).get("label", k)}
        for k, v in conf.accounts().items()
    ]


@register.inclusion_tag("impersonate/_banner.html", takes_context=True)
def impersonation_banner(context):
    """Render the floating 'currently impersonating' pill, or nothing."""
    request = context.get("request")
    sess = getattr(request, "session", {}) if request is not None else {}
    return {
        "request":          request,
        "impersonating_as": sess.get(conf.SESSION_IMPERSONATING_AS_KEY),
        "snapshot":         sess.get(conf.SESSION_SNAPSHOT_KEY) or {},
    }


@register.inclusion_tag("impersonate/_menu.html", takes_context=True)
def impersonation_menu(context):
    """Render an admin-gated submenu of resource accounts."""
    request = context.get("request")
    return {
        "request":      request,
        "can_impersonate": bool(request is not None and is_allowed(request)),
        "accounts":     impersonation_accounts_tag(),
    }
