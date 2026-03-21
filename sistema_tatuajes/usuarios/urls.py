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
    # Anuncios
    path('anuncios/',                              views.panel_anuncios,          name='panel_anuncios'),
    path('anuncios/nuevo/',                        views.panel_crear_anuncio,     name='panel_crear_anuncio'),
    path('anuncios/<int:anuncio_id>/editar/',       views.panel_editar_anuncio,    name='panel_editar_anuncio'),
    path('anuncios/<int:anuncio_id>/eliminar/',     views.panel_eliminar_anuncio,  name='panel_eliminar_anuncio'),
    # Configuración
    path('configuracion/',                    views.panel_configuracion,    name='panel_configuracion'),
    # Imágenes Hero
    path('hero/subir/',                       views.panel_subir_imagen_hero,    name='panel_subir_imagen_hero'),
    path('hero/<int:imagen_id>/eliminar/',    views.panel_eliminar_imagen_hero, name='panel_eliminar_imagen_hero'),
]
