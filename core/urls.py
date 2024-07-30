from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core import settings

handler404 = 'apps.views.error_404'     
handler500 = 'apps.views.error_500'

urlpatterns = ([
                   path('admin/', admin.site.urls),
                   path('', include('apps.urls')),
                   path("ckeditor5/", include('django_ckeditor_5.urls')),
                   path('accounts/', include('allauth.urls')),
               ] + debug_toolbar_urls() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
               + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))







