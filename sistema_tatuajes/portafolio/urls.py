from django.urls import path
from . import views

urlpatterns = [
    path('',                               views.galeria_portafolio, name='galeria'),
    path('artista/<int:tatuador_id>/',     views.perfil_tatuador,   name='perfil_tatuador'),

    # Gestión privada del tatuador
    path('mi-portafolio/',                             views.mi_portafolio,    name='mi_portafolio'),
    path('mi-portafolio/subir/',                       views.subir_trabajo,    name='subir_trabajo'),
    path('mi-portafolio/eliminar/<int:trabajo_id>/',   views.eliminar_trabajo, name='eliminar_trabajo'),
    path('mi-portafolio/perfil/',                      views.editar_perfil,    name='editar_perfil'),
]
