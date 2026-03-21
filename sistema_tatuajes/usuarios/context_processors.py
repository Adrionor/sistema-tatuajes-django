"""
Context processors globales para todos los templates:
  - notificaciones: conteo de notificaciones no leídas.
  - estudio:        config del estudio + CSS del skin activo + idiomas disponibles.
"""
from .models import Notificacion


def notificaciones(request):
    if request.user.is_authenticated:
        count = Notificacion.objects.filter(
            usuario=request.user, leida=False
        ).count()
        recientes = Notificacion.objects.filter(
            usuario=request.user
        )[:5]
        return {
            'notificaciones_no_leidas': count,
            'notificaciones_recientes': recientes,
        }
    return {
        'notificaciones_no_leidas': 0,
        'notificaciones_recientes': [],
    }


def estudio(request):
    """
    Inyecta en todos los templates:
      {{ estudio_config }}  — instancia ConfiguracionEstudio
      {{ skin_css }}        — bloque :root { ... } con las variables CSS del skin activo
      {{ skin_data }}       — dict con label, fonts_url, preview_bg, preview_accent
      {{ skins_disponibles }} — lista de (key, skin_dict) para el selector del panel
    """
    from .models import ConfiguracionEstudio
    from .skins import get_skin, render_skin_css, SKINS
    config   = ConfiguracionEstudio.get_config()
    skin_key = config.skin or 'noir'
    skin_d   = get_skin(skin_key)
    return {
        'estudio_config':      config,
        'skin_css':            render_skin_css(skin_key),
        'skin_data':           skin_d,
        'skins_disponibles':   list(SKINS.items()),
    }
