from django.urls import path
from . import views

urlpatterns = [
    path('agenda/',                                views.agenda_tatuador,           name='agenda_tatuador'),
    path('agendar/<int:cotizacion_id>/',           views.confirmar_y_agendar,       name='agendar_cita'),
    path('cancelar/<int:cita_id>/',                views.cancelar_cita,             name='cancelar_cita'),
    path('api/fechas-ocupadas/<int:tatuador_id>/', views.obtener_fechas_ocupadas,   name='api_fechas_ocupadas'),
]
