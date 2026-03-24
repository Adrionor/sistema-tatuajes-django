from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from usuarios.views import landing

urlpatterns = [
    path('health/',    include('health.urls')),
    path('',          landing,                          name='landing'),
    path('manual/',   TemplateView.as_view(template_name='manual.html'), name='manual'),
    path('admin/',    admin.site.urls),
    path('portafolio/', include('portafolio.urls')),
    path('cotizar/',    include('cotizaciones.urls')),
    path('citas/',      include('citas.urls')),
    path('panel/',      include('usuarios.urls')),
    path('i18n/',       include('django.conf.urls.i18n')),  # cambio de idioma

    # Sistema de login/logout de Django para tatuadores
    path('cuentas/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
