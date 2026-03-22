"""
TenantMiddleware — resuelve el estudio activo desde el subdominio del Host.

Cómo funciona:
  studio33.midominio.com  →  ConfiguracionEstudio.objects.get(subdominio='studio33')
  midominio.com / www     →  primer estudio registrado (fallback / desarrollo)
  127.0.0.1:8000          →  primer estudio registrado (desarrollo local)

El resultado se guarda en request.studio y queda disponible en toda la
cadena de views, context processors y middlewares posteriores.
"""

from django.http import Http404


def _extract_subdomain(request) -> str | None:
    """Devuelve el subdominio del host o None si es raíz / IP / localhost."""
    host = request.get_host().lower().split(':')[0]       # quitar puerto
    # hosts que se consideran "raíz" → sin tenant específico
    root_hosts = {'localhost', '127.0.0.1', 'www'}
    parts = host.split('.')
    if len(parts) >= 2 and parts[0] not in root_hosts:
        return parts[0]
    return None


class TenantMiddleware:
    """
    Identifica el estudio (tenant) a partir del subdominio y lo adjunta
    al objeto request como `request.studio`.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from .models import ConfiguracionEstudio

        subdomain = _extract_subdomain(request)

        if subdomain:
            # Busca el estudio por su slug de subdominio
            studio = ConfiguracionEstudio.objects.filter(subdominio=subdomain).first()
            if studio is None:
                # Subdominio desconocido — opcionalmente devuelve 404
                # Por ahora, caemos al estudio por defecto para no romper nada
                studio = ConfiguracionEstudio.objects.first()
        else:
            # Sin subdominio (desarrollo / dominio raíz) → primer estudio
            studio = ConfiguracionEstudio.objects.first()

        # Si no existe ningún estudio aún, creamos uno vacío
        if studio is None:
            studio = ConfiguracionEstudio.objects.create()

        request.studio = studio
        response = self.get_response(request)
        return response
