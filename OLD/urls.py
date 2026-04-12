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
    path('accounts/', include('allauth.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('oidccb/', oidc_callback, name='oidc callback'),
    path(r'uploadfile/', views.uploadfile, name='uploadfile'),
    path(r'contactus/', views.contactus, name='send email'),

    path(r'broadcast/', views_channels.broadcast, name='brodcast'),
    path(r'', views.index, name='index'),
    
    
] + settings.DETECTED_URLS + [
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