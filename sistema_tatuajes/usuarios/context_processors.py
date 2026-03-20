"""
Context processor que inyecta el conteo de notificaciones no leídas
en todos los templates. Disponible como {{ notificaciones_no_leidas }}.
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
