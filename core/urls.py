from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('portafolio/', include('portafolio.urls')),
    path('cotizar/', include('cotizaciones.urls')),
    path('citas/', include('citas.urls')), # NUEVA RUTA AQUÍ
]

# Esto es vital para que las imágenes se vean en tu entorno local
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)