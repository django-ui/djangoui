from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import djangoui, djangoui.utils, logging
from mangorest import mango
from pathlib import Path
from ntpath import basename, dirname
from django.conf import settings
import requests
from datetime import datetime

#------------------------------------------------------------------------------
logger = logging.getLogger("djangoui")

DEFULT_INDEX=None
def index(request):
    global DEFULT_INDEX

    if DEFULT_INDEX is None:
        DEFULT_INDEX = "index.html"
        start_dir = f"{settings.DEFAULT_APP}/templates"
        filename = "index.html"
        main_index = [basename(dirname(p)) for p in Path(start_dir).rglob(filename) if p.is_file()]
        if len(main_index) > 0:
            DEFULT_INDEX = main_index[0] + "/index.html"

    return render(request, DEFULT_INDEX )
# -----------------------------------------------------------------------
def uploadfile(request):
    par = dict(request.GET)
    par.update(request.POST)

    savedir =  par.get("savedir", "/");
    if not savedir.endswith("/") or not savedir.endswith("\\"):
        savedir += "/"
    
    ret = "Uploading Files:\n "
    for f in request.FILES.getlist('file'):
        content = f.read()
        filename = f"/tmp/{savedir}/{str(f)}"
        print(f"++ Save file {filename} Content: {len(content)} :")
        with open(filename, "wb") as f:
            f.write(content)
        ret += filename + "\n"


    return HttpResponse(ret)

# -----------------------------------------------------------------------
def contactusemail(name="", email="", phone="", msg="", dfrom="a@example.com", **kwargs):
    sub= "Thank you for reaching out."
    ret = f'''
Dear {name or "sir/madam"},

{sub}

We will review your message and get back at the contact information you provided.

Best Regards,
Admin


C O N T A C T   I N F O R M A T I O N  & M E S S A G E:
-------------------------------------------------------

Name : {name}
Email: {email}
Phone: {phone}
Message:
{msg}


If you did not sign up for this, please ignore this message as your email 
is not subscribed or stored in our system.
'''
    djangoui.utils.demail(subject=sub, msg=ret, to=email, dfrom=dfrom)
    return ret

def contactus(request):
    parms = mango.getparms(request)

    ret = contactusemail(**parms)
    return HttpResponse(ret)


# -----------------------------------------------------------------------
import allauth.account.views
import allauth.account.forms
from   allauth.account.forms import ResetPasswordForm
from   allauth.account.views import PasswordResetView

from allauth.account.utils import (filter_users_by_email, user_pk_to_url_str, user_username)
from allauth.utils import build_absolute_uri
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account import app_settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse, reverse_lazy

class MyResetPasswordForm(ResetPasswordForm):
    def save(self, request, **kwargs):
        current_site = get_current_site(request)
        email = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator", default_token_generator)

        for user in self.users:

            temp_key = token_generator.make_token(user)

            # save it to the password reset model
            # password_reset = PasswordReset(user=user, temp_key=temp_key)
            # password_reset.save()

            # send the password reset email
            path = reverse(
                "account_reset_password_from_key",
                kwargs=dict(uidb36=user_pk_to_url_str(user), key=temp_key),
            )
            url = build_absolute_uri(request, path)
            url1 = request.POST.get("DOMAIN") + path
            #url1 = settings.DEFAULT_DOMAIN + path

            context = {
                "current_site": current_site,
                "user": user,
                "password_reset_url": url,
                "password_reset_url1": url1,
                "request": request,
                "domain": settings.DEFAULT_DOMAIN
            }

            #print(f"===> {context}")
            get_adapter(request).send_mail(
                "account/email/password_reset_key", email, context
            )
        return self.cleaned_data["email"]
        
class myPasswordResetView(PasswordResetView):
    form_class = MyResetPasswordForm

allauth.account.views.password_reset = myPasswordResetView.as_view()
#print( f"===> {allauth.account.views.password_reset}")

# -----------------------------------------------------------------------
def get_userinfo(access_token ):
    import requests

    endPoint = settings.OIDC_OP_USER_ENDPOINT
    if (not endPoint or not access_token):
        return None

    headers = {
        "Authorization": f"Bearer {access_token}",
        #"Accept": "application/json"
    }
    response = ""
    try:
        response = requests.get(endPoint , headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        user_data = response.json()
        #user_groups = user_data.get("groups", []) # Common key, adjust as needed
            
        return user_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user info: {e} : {response} {response.text}")
    except ValueError:
        print("Error decoding JSON response.")
        
    return None

# -----------------------------------------------------------------------
# Session keys used to cache OIDC user info on the Django session.
# We intentionally do NOT write these onto the Django User model because
# the built-in User model has no such fields (and `user.groups` is a
# ManyToMany manager, not a list), so attribute assignments there are
# silently lost after the request.
SESSION_USER_INFO       = "oidc_user_info"
SESSION_AD_GROUPS       = "oidc_ad_groups"
SESSION_EMPLOYEE_ID     = "oidc_employee_id"
SESSION_USER_INFO_TS    = "oidc_user_info_ts"  # epoch seconds


def _attach_user_info_to_user(user, request):
    """Copy cached OIDC user info from the session onto `user` for this request.

    This makes code like `request.user.ad_groups` / `request.user.user_info`
    work for the current request without requiring a custom User model.
    """
    if request is None or not hasattr(request, "session"):
        return
    user.user_info   = request.session.get(SESSION_USER_INFO)
    user.ad_groups   = request.session.get(SESSION_AD_GROUPS, [])
    user.employee_id = request.session.get(SESSION_EMPLOYEE_ID, "")


# -----------------------------------------------------------------------
@csrf_exempt
def checkUserGroupMembership(request):
    group = request.GET.get("group", "")
    if not group:
        return HttpResponse("OK", status=200)

    # Normalize: lowercase + collapse any double-backslashes (e.g. from
    # URL-encoded "%5C%5C") down to a single backslash so it matches the
    # form returned by the OIDC userinfo endpoint (e.g. "us\all.ebs.employees").
    group = group.lower().replace("\\\\", "\\")
    u = request.user

    if not u.is_authenticated:
        return HttpResponse(f"NOT OK {group} - not logged in", status=403)

    ad_groups = request.session.get(SESSION_AD_GROUPS, []) or []

    logger.info(f"Checking group {group} for {u.username}")
    if group in ad_groups:
        return HttpResponse(f"OK {u} in {group}", status=200)
    else:
        return HttpResponse(f"NOT OK '{u}' not in '{group}'", status=403)

@csrf_exempt
def getEmployeeId(request):
    if not request.user.is_authenticated:
        return HttpResponse("NOT OK - not logged in", status=403)
    employee_id = request.session.get(SESSION_EMPLOYEE_ID, "")
    return HttpResponse(f"OK {employee_id}", status=200)


@csrf_exempt
def isInThisGroup(request):
    u = request.user
    if not u.is_authenticated:
        return HttpResponse("NOT OK - not logged in", status=403)

    raw_groups = request.GET.get("groups", "")
    raw_eids   = request.GET.get("employee_ids", "")
    if not raw_groups and not raw_eids:
        return HttpResponse("OK", status=200)

    groups = {g.lower().replace("\\\\", "\\") for g in raw_groups.split(",") if g}
    eids   = {e for e in raw_eids.split(",") if e}

    user_groups = set(request.session.get(SESSION_AD_GROUPS, []) or [])
    user_eid    = request.session.get(SESSION_EMPLOYEE_ID, "")

    if (groups & user_groups) or (user_eid and user_eid in eids):
        return HttpResponse(f"OK {u} in {groups} or {eids}", status=200)

    return HttpResponse(f"NOT OK '{u}' not in '{groups} or {eids}'", status=403)

# -----------------------------------------------------------------------
from django.contrib.auth.signals import user_logged_in
def postLoggedIn(sender, user, request, **kwargs):
    if ( not request.path_info.startswith("/oidc/") ):
        return

    access_token = request.session.get('oidc_access_token','None check: OIDC_STORE_ACCESS_TOKEN')
    #logger.info(f"ACCESS TOKEN: {access_token}")

    log = (f'''
        ***In postLoggedIn - OIDC username: {user.username},
        email: {user.email} ***
        request.path: {request.path}
        User: {user}
        {request.GET}
        {request.POST}
        {sender}
        {kwargs}
        ''')
    logger.info(log)

    try:
        interval = getattr(settings, "UPDATE_USER_INFO_INTERVAL", 10 * 60)
        now_ts   = datetime.now().timestamp()
        last_ts  = request.session.get(SESSION_USER_INFO_TS, 0) or 0
        cached   = request.session.get(SESSION_USER_INFO)

        if cached and (now_ts - last_ts) < interval:
            logger.info(
                f"Skipping get_userinfo; cached {int(now_ts - last_ts)}s ago "
                f"(interval={interval}s)"
            )
        else:
            user_info = get_userinfo(access_token) or {}
            ad_groups = [g.lower() for g in user_info.get("groups", [])]

            # Persist on the session so it survives across requests.
            request.session[SESSION_USER_INFO]    = user_info
            request.session[SESSION_AD_GROUPS]    = ad_groups
            request.session[SESSION_EMPLOYEE_ID]  = user_info.get("employee_id", "").lower()
            request.session[SESSION_USER_INFO_TS] = now_ts
            request.session.modified = True

            #logger.info(f"AD Groups: {ad_groups}")
    except Exception as e:
        logger.warning(f"Error getting user info: {e}")

    # Attach cached info onto the user object for this request's convenience.
    _attach_user_info_to_user(user, request)

    if ( not user.email.startswith(user.username)):
        print("******** UPDATING USERNAME")
        user.username=user.email.split("@")[0]
        user.save()

def postLogOff(sender, user, request, **kwargs):
    #global ACCESS_TOKEN
    #ACCESS_TOKEN = None
    pass

user_logged_in.connect(postLoggedIn)
user_logged_in.disconnect(postLogOff)
