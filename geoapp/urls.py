from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from . import views_channels
from mangorest import mango
from django.conf import settings
#from . import settings

app_name = 'geoapp' 

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def catchAll(request):
    return mango.Common(request)    


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path(r'uploadfile/', views.uploadfile, name='uploadfile'),
    path(r'contactus/', views.contactus, name='send email'),

    path(r'broadcast/', views_channels.broadcast, name='brodcast'),
    
    path(r'example_app/', include('example_app.urls')),

    path(r'', views.index, name='index'),
    
    
] + settings.DETECTED_URLS + [
    path('oidc/', include('mozilla_django_oidc.urls')),
    re_path(r'^.*/$', catchAll, name='catchall'),
]

#urlpatterns = staticfiles_urlpatterns() + urlpatterns
urlpatterns =  urlpatterns
#print("++ geoapp/urls.py: urlpatterns:", urlpatterns)
'''
To enable single sign on: 

Step 1: Add following line to urlpatterns:
    path('oidc/', include('mozilla_django_oidc.urls')),

Step 2: 
'''