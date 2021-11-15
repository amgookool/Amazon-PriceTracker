from django.urls import path
from . import views

urlpatterns=[
    path("home/",views.HomeView,name="Home"),
    path("settings/",views.SettingsView,name="Settings"),
    path("trackingprods/",views.TrackingView,name="Tracking"),
]

