# This file can be in ~/.django/my_config.py for all apps or create a local copy
EMAIL_USE_TLS       = False
EMAIL_HOST          = ''
EMAIL_PORT          = 25
DEFAULT_FROM_EMAIL  = ""
EMAIL_HOST_USER     = ""
EMAIL_HOST_PASSWORD = ""
NO_PROXY=""
PROXIES=None
PROXY=""

proxies = { "http"  : PROXY, "https" : PROXY, "ftp"   : PROXY }
certs="" #try os.path.expanduser(myconfig.certs)
verify=False
verify=certs
# --------------------------------------------------------------------------------
# -- For Single Sign on below
OIDC_RP_CLIENT_ID = 'your-oauth'
OIDC_RP_CLIENT_SECRET = 'jkSIDbfvK7WFkyeSEEbB91Nk0vZf5uJl2aRnkuVy'
OIDC_OP_AUTHORIZATION_ENDPOINT = 'auth_endpoint'
OIDC_OP_TOKEN_ENDPOINT = 'token_endpoint'
OIDC_OP_USER_ENDPOINT = 'user_endpoint'
OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_OP_JWKS_ENDPOINT = 'jwks'
OIDC_RP_SCOPES = "openid profile email"
OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = 15
OIDC_CREATE_USER = True
OIDC_VERIFY_SSL = True
DEFAULT_DOMAIN="http://www.example.com"

#---------------------------------------------------------------------------------
def appcontext(request):
    context = {
        "appname"           : "My Application Name",
        "weburl"            : "https://myurl.forexample.com/",
        "top_url"           : "example_app/topbar.html",
        #"entire_top_url"   : "mainapp/topbar.html",   # If you want the entire top URL replaced
        "NO_LOGIN_MENU"     : 0,                            # 1: to show login menu in topbar right corner
        "APP_MENU"          : 0,                            # 1: show applications menu in top bar
        "SSO"               : 0,                            # 1: to show single signon during login
        "DO_NOT_SHOW_LOGIN" : 0,                            # 1: do not allow users to enter username/passwd
        "ALLOW_REGISTRATION": 1,                            # 1: allow users to register
    }
    #analytics.loganalytics(request);

    return context
#---------------------------------------------------------------------------------
INCLUDE_APPS = ["example_app"]