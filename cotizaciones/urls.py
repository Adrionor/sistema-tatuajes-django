from django.urls import path
from . import views

urlpatterns = [
    path('nueva/', views.solicitar_cotizacion, name='nueva_cotizacion'),
    path('recepcion/', views.recepcion_tatuador, name='recepcion_tatuador'),
    path('aceptar/<int:cotizacion_id>/', views.aceptar_cotizacion, name='aceptar_cotizacion'),
    
    # RUTA DEL MAGIC LINK (Atrapa el UUID en la URL)
    path('estado/<uuid:token>/', views.estado_magico_cliente, name='estado_magico'),
]