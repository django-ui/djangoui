from django.urls import path
from . import views

app_name = 'mainapp'

urlpatterns = [
    path('',  views.index , name='mainapp urls'),
    path(r'info/',  views.info , name='mainapp urls'),
    path(r'feedback/',  views.feedback , name='feedback'),
    path(r'submit_feedback/',  views.submit_feedback , name='submit_feedback'),
    path(r'applications/',  views.applications , name='applications'),
    path(r'app_launch/',  views.app_launch , name='app_launch'),
]
