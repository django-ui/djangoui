from django.urls import path

from . import views

app_name = "impersonate"

urlpatterns = [
    path("",       views.picker, name="picker"),
    path("start/", views.start,  name="start"),
    path("stop/",  views.stop,   name="stop"),
]
