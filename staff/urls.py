from django.contrib import admin
from django.urls import path, include
from .views import *
from django.conf import settings

urlpatterns = [
    path('authentication/', staff_authentication, name='staff_authentication_url'),
    path('logout/', staff_logout, name='staff_logout_url'),
]

# If we are in production, turn on admin page by /staff/admin/ instead of just /admin/
if not settings.DEBUG:
    urlpatterns.append(path('admin/', admin.site.urls))
    urlpatterns.append(path('rosetta/', include('rosetta.urls')))
