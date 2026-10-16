from django.contrib import admin
from django.urls import path, include, re_path
from mangorest import mango
from . import views
from . import views_channels
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

app_name = 'djangoui' 

@csrf_exempt
def catchAll(request):
    return mango.Common(request)    

# -----------------------------------------------------------------------
def oidc_callback(request):
    print( f'''
    +++++++++++++++++++ OIDC CALLBACK
    {request.build_absolute_uri()}
    {request.GET}
    {request.POST}
    {request.headers}
    
    ''')
    return HttpResponse('{"access_token": 1, "refresh_token": 2}', status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Must come before the allauth.urls include below: same name/pattern as
    # allauth's own account_confirm_email, but tolerates a stale/reused/
    # double-submitted confirmation key on POST instead of raising a raw
    # 404 (see ConfirmEmailView in views.py).
    re_path(r'^accounts/confirm-email/(?P<key>[-:\w]+)/$', views.ConfirmEmailView.as_view(), name='account_confirm_email'),
    # allauth itself has no "delete your account" flow built in.
    path('accounts/delete/', views.AccountDeleteView.as_view(), name='account_delete'),
    path('accounts/', include('allauth.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('oidccb/', oidc_callback, name='oidc callback'),
    path(r'uploadfile/', views.uploadfile, name='uploadfile'),
    path(r'contactus/', views.contactus, name='send email'),
    path(r'checkUserGroupMembership/', views.checkUserGroupMembership, name='check user group membership'),
    path(r'getEmployeeId/', views.getEmployeeId, name='getEmployeeId'),
    path(r'isInThisGroup/', views.isInThisGroup, name='isInThisGroup'),

    path(r'broadcast/', views_channels.broadcast, name='brodcast'),
] + (
    # Optional: only wire up the portable impersonate app when it is available
    # and configured (see IMPERSONATION_ENABLED in settings.py).
    [path('impersonate/', include('djangoui.impersonate.urls', namespace='impersonate'))]
    if getattr(settings, 'IMPERSONATION_ENABLED', False) else []
) + [
    path(r'', views.index, name='index'),
    
    
] + settings.DETECTED_URLS + [
    # App registry is ready at this point (urls.py is only loaded once
    # Django's apps.populate() has finished), so it's safe to build the
    # include() objects for INCLUDE_APPS_WITH_URLS here -- unlike building
    # them eagerly in settings.py, which would blow up for any app with a
    # models.py (see settings.py comment next to INCLUDE_APPS_WITH_URLS).
    path(f'{a}/', include(f'{a}.urls'), name=a)
    for a in getattr(settings, 'INCLUDE_APPS_WITH_URLS', [])
] + [
    path('oidc/', include('mozilla_django_oidc.urls')),
    re_path(r'^.*/$', catchAll, name='catchall'),
]

#urlpatterns = staticfiles_urlpatterns() + urlpatterns
urlpatterns =  urlpatterns
#print("++ djangoui/urls.py: urlpatterns:", urlpatterns)
'''
To enable single sign on: 

Step 1: Add following line to urlpatterns:
    path('oidc/', include('mozilla_django_oidc.urls')),

Step 2: 
'''