from django.contrib import admin
from django.urls import path, include

import Tracker

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Login.urls')),
    path('',include('django.contrib.auth.urls')),
    path('',include("Tracker.urls")),
]
