from django.urls import path
from . import views

urlpatterns = [
    path('agenda/',                                  views.agenda_tatuador,         name='agenda_tatuador'),
    path('agendar/<int:cotizacion_id>/',             views.confirmar_y_agendar,     name='agendar_cita'),
    path('cancelar/<int:cita_id>/',                  views.cancelar_cita,           name='cancelar_cita'),

    # Bloqueos de agenda
    path('bloqueos/',                                views.gestionar_bloqueos,      name='gestionar_bloqueos'),
    path('bloqueos/crear/',                          views.crear_bloqueo,           name='crear_bloqueo'),
    path('bloqueos/eliminar/<int:bloqueo_id>/',      views.eliminar_bloqueo,        name='eliminar_bloqueo'),

    # API para el datepicker del formulario de cotización
    path('api/periodos-bloqueados/<int:tatuador_id>/', views.api_periodos_bloqueados, name='api_periodos_bloqueados'),
]
