"""
URL configuration for studydeck_forum project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # Authentication
    path("accounts/", include("allauth.urls")),
    
    # Forum (main app)
    path("forum/", include("forum.urls")),
    
    # Markdownx
    path('markdownx/', include('markdownx.urls')),
    
    # Redirect root to forum
    path("", RedirectView.as_view(url="/forum/", permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns