from django.urls import path
from . import views

urlpatterns = [
    path('agendar/<int:cotizacion_id>/', views.confirmar_y_agendar, name='agendar_cita'),
    # NUEVA RUTA PARA LA API DE CALENDARIO
    path('api/fechas-ocupadas/<int:tatuador_id>/', views.obtener_fechas_ocupadas, name='api_fechas_ocupadas'),
]