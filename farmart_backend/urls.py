from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Your custom API (events, animals, users, etc.)
    path('api/', include('api.urls')),

    # Djoser handles registration, login, password reset, JWT, etc.
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
]

# Serve media files in development (for user-uploaded images, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
