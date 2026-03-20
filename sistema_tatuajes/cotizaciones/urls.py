from django.urls import path
from . import views

urlpatterns = [
    # Públic: nueva cotización (con o sin tatuador pre-seleccionado)
    path('nueva/',                         views.solicitar_cotizacion,        name='nueva_cotizacion'),
    path('nueva/<int:tatuador_id>/',       views.solicitar_cotizacion,        name='nueva_cotizacion_artista'),

    # Panel del tatuador
    path('recepcion/',                     views.recepcion_tatuador,          name='recepcion_tatuador'),
    path('aceptar/<int:cotizacion_id>/',   views.aceptar_cotizacion,          name='aceptar_cotizacion'),
    path('cancelar-tatuador/<int:cotizacion_id>/', views.cancelar_por_tatuador, name='cancelar_por_tatuador'),
    path('detalle/<int:cotizacion_id>/',   views.detalle_cotizacion,          name='detalle_cotizacion'),

    # Panel privado del cliente (magic link)
    path('estado/<uuid:token>/',           views.estado_magico_cliente,       name='estado_magico'),
    path('estado/<uuid:token>/cancelar/',  views.cancelar_por_cliente,        name='cancelar_por_cliente'),
    path('estado/<uuid:token>/abierta/',   views.dejar_abierta,               name='dejar_abierta'),

    # Notificaciones
    path('notificaciones/leer/',           views.marcar_notificaciones_leidas, name='marcar_notificaciones_leidas'),
]
