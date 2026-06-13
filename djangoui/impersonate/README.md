# `impersonate` — portable Django app

OIDC-backed "log in as a resource account" for admins.

A privileged real user authenticates normally via OIDC, then can swap their
session to a configured service / resource account. The real user's identity
is snapshotted server-side for audit and one-click restore.

---

## Drop-in install (other projects)

1. **Copy** this `impersonate/` directory next to your other Django apps.
2. **Register** the app in `settings.py`:
   ```python
   INSTALLED_APPS = [
       ...,
       "impersonate",
   ]
   ```
3. **Include** the URLs (root urlconf):
   ```python
   from django.urls import include, path
   urlpatterns = [
       ...,
       path("impersonate/", include("impersonate.urls")),
   ]
   ```
4. **Configure** in `settings.py` (or `my_config.py`):
   ```python
   # Who may impersonate
   IMPERSONATION_ALLOWED_GROUPS = ["us\\eo.aifoundry.admin"]
   IMPERSONATION_ALLOWED_USERS  = []   # optional fallback by username

   # Resource accounts available
   IMPERSONATION_ACCOUNTS = {
       "aifoundry": {
           "label":         "AI Foundry Resource",
           "grant":         "client_credentials",   # default
           "client_id":     "eo-aifoundry-space-aries-aifoundry-svc",
           "client_secret": "*****",
       },
   }
   ```
   Required OIDC settings (reused, not duplicated):
   `OIDC_OP_TOKEN_ENDPOINT`, `OIDC_OP_USER_ENDPOINT`,
   `OIDC_RP_CLIENT_ID`, `OIDC_RP_CLIENT_SECRET`, `OIDC_RP_SCOPES`,
   `OIDC_VERIFY_SSL`.

5. **Render** the widgets in your base/topbar template:
   ```html
   {% load impersonate_tags %}

   {# Floating bottom-right pill while a session is impersonating, with Exit #}
   {% impersonation_banner %}

   {# Admin-only menu entry with per-account quick-start buttons #}
   {% impersonation_menu %}
   ```

That's it. Visit `/impersonate/` to see the picker page.

---

## Supported OAuth grants per account

Declared via the `"grant"` key in each `IMPERSONATION_ACCOUNTS` entry.

| Grant | Required keys | Notes |
|---|---|---|
| `client_credentials` (default) | `client_id`, `client_secret` | Token is bound to whatever AD account the OAuth client is linked to (e.g. PingFederate "Linked Resource Account"). Best fit when ROPC is disabled at the IdP. |
| `password` (ROPC) | `username`, `password`, plus client credentials | Requires the OAuth client to allow the password grant — many IdPs disable this. |
| `refresh_token` | `refresh_token`, plus client credentials | Pre-bootstrap a refresh token via an interactive login with `offline_access`. |

---

## Optional advanced settings

| Setting | Default | Purpose |
|---|---|---|
| `IMPERSONATION_AUTH_BACKEND` | first entry in `AUTHENTICATION_BACKENDS` | Auth backend label passed to `django.contrib.auth.login()` during user swap. |
| `IMPERSONATION_PICKER_TEMPLATE` | `"impersonate/picker.html"` | Override the picker page (e.g. to wrap in your project's base layout). |
| `IMPERSONATION_SESSION_KEYS` | see `impersonate/conf.py` | Override the session-key names this app writes to (so the rest of your app reads the impersonated identity from the same keys it normally does). |

---

## How it works

1. **Gate** (`impersonate.auth.is_allowed`): superuser ✔ / allowed username ✔ /
   allowed AD group ✔. While impersonating, the gate evaluates the *snapshot*
   of the real user's groups, so an impersonated account cannot re-impersonate.
2. **Token** (`impersonate.tokens.acquire_token`): POST to
   `OIDC_OP_TOKEN_ENDPOINT` with the per-account grant.
3. **Userinfo** (`impersonate.userinfo.get_userinfo`): GET
   `OIDC_OP_USER_ENDPOINT` with the new access token.
4. **Swap** (`impersonate.views.start`): snapshot real user pk + session keys
   into `session['impersonator_snapshot']`, then `login()` as the impersonated
   user with the configured backend. Overwrite the session keys with the new
   identity's user_info / groups / employee_id / tokens.
5. **Restore** (`impersonate.views.stop`): inverse — re-`login()` as the
   original user, restore the snapshot's session keys, drop the snapshot.

Every start and stop is logged at WARNING level under logger `impersonate`.

---

## Security notes

* Credentials in `IMPERSONATION_ACCOUNTS` are sensitive. Keep them in a
  vault / git-ignored config (e.g. `~/.django/my_config.py`), not the repo.
* Prefer `client_credentials` with a Linked Resource Account over ROPC.
* `groups` / `employee_id` claims may be missing for client-credentials
  tokens depending on the IdP — the impersonated session will then carry an
  empty AD-groups list, which is the safe default.
