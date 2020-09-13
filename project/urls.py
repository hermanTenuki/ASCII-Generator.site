"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('staff/', include('staff.urls')),
    path('', include('app.urls'))
]

# Handlers
handler400 = 'app.views.handler400_view'
handler404 = 'app.views.handler404_view'
handler500 = 'app.views.handler500_view'

# If DEBUG is True - allow to visit error pages
if settings.DEBUG:
    from app.views import handler400_view, handler404_view, handler500_view

    urlpatterns += [
        path('400/', handler400_view),
        path('404/', handler404_view),
        path('500/', handler500_view)
    ]

# If DEBUG is True - turn on django's admin page and manually serve static/media files
if settings.DEBUG:
    urlpatterns.append(path('admin/', admin.site.urls))
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
