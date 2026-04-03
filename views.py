from django.http import HttpResponse
from django.shortcuts import render
import djangoui, djangoui.utils, logging
from mangorest import mango
from pathlib import Path
from ntpath import basename, dirname

#------------------------------------------------------------------------------
logger = logging.getLogger("djangoui")

DEFULT_INDEX=None
def index(request):
    global DEFULT_INDEX

    if DEFULT_INDEX is None:
        DEFULT_INDEX = "index.html"
        start_dir = "mainapp/templates"
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

from django.conf import settings

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
from django.contrib.auth.signals import user_logged_in
def postLoggedIn(sender, user, request, **kwargs):
    if ( not request.path_info.startswith("/oidc/") ):
        return

    access_token = request.session.get('oidc_access_token','None check: OIDC_STORE_ACCESS_TOKEN')
    log = (f'''
        ***In postLoggedIn - OIDC username: {user.username}, 
        email: {user.email} ***
        Groups: {user.groups} ***
        request.path: {request.path}
        User: {user}
        {request.GET}
        {request.POST}
        {sender}
        {kwargs}
        ''')
    print(log)
    
    #jwt = decode_jwt(access_token)
    #user_info = get_userinfo(access_token)

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
