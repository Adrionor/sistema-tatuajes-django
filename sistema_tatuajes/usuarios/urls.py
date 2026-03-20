from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('',                                  views.panel_dashboard,        name='panel_dashboard'),
    # Tatuadores
    path('tatuadores/',                       views.panel_tatuadores,       name='panel_tatuadores'),
    path('tatuadores/nuevo/',                 views.panel_crear_tatuador,   name='panel_crear_tatuador'),
    path('tatuadores/<int:user_id>/editar/',  views.panel_editar_usuario,   name='panel_editar_usuario'),
    path('tatuadores/<int:user_id>/toggle/',  views.panel_toggle_activo,    name='panel_toggle_activo'),
    path('tatuadores/<int:user_id>/eliminar/',views.panel_eliminar_tatuador,name='panel_eliminar_tatuador'),
    # Clientes
    path('clientes/',                         views.panel_clientes,         name='panel_clientes'),
    # Cotizaciones
    path('cotizaciones/',                     views.panel_cotizaciones,     name='panel_cotizaciones'),
    # Configuración
    path('configuracion/',                    views.panel_configuracion,    name='panel_configuracion'),
]
