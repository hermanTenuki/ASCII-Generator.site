from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('staff/', include('staff.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
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
    urlpatterns.append(path('rosetta/', include('rosetta.urls')))  # Also add "rosetta" for translation
