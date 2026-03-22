from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Trabajo
from .forms import TrabajoForm, PerfilForm
from citas.models import BloqueoAgenda
from usuarios.models import ConfiguracionEstudio


def _layout(studio):
    """Return the active layout slug from the given studio config."""
    return (studio.plantilla_layout if studio else None) or 'clasico'


def galeria_portafolio(request):
    studio = request.studio
    tatuadores = (
        User.objects
        .filter(perfil__rol='tatuador', perfil__estudio=studio)
        .prefetch_related('trabajos_portafolio')
        .distinct()
    )
    hoy = timezone.localdate()
    artistas = []
    for tatuador in tatuadores:
        trabajos = list(tatuador.trabajos_portafolio.all())
        if trabajos:
            # Próximos viajes públicos del artista (para badge "tatúa cerca")
            viajes = list(
                BloqueoAgenda.objects.filter(
                    tatuador=tatuador,
                    publico=True,
                    tipo__in=('viaje_nacional', 'viaje_internacional'),
                    fecha_fin__gte=hoy,
                ).order_by('fecha_inicio')[:2]
            )
            artistas.append({
                'tatuador': tatuador,
                'preview':  trabajos[:3],
                'total':    len(trabajos),
                'estilos':  list({t.estilo for t in trabajos}),
                'viajes':   viajes,
            })
    return render(request, f'portafolio/galeria_{_layout(studio)}.html', {'artistas': artistas})


def perfil_tatuador(request, tatuador_id):
    studio   = request.studio
    tatuador = get_object_or_404(User, pk=tatuador_id, perfil__rol='tatuador', perfil__estudio=studio)
    trabajos = tatuador.trabajos_portafolio.all()
    estilos  = list({t.estilo for t in trabajos})
    hoy      = timezone.localdate()

    # Periodos públicos activos o próximos (90 días)
    bloqueos_publicos = BloqueoAgenda.objects.filter(
        tatuador=tatuador,
        publico=True,
        fecha_fin__gte=hoy,
    ).order_by('fecha_inicio')[:6]

    return render(request, f'portafolio/perfil_{_layout(studio)}.html', {
        'tatuador':          tatuador,
        'trabajos':          trabajos,
        'estilos':           estilos,
        'bloqueos_publicos': bloqueos_publicos,
    })


# ─── GESTIÓN PRIVADA ─────────────────────────────────────────────────────────

@login_required
def mi_portafolio(request):
    """Panel donde el tatuador gestiona su portafolio y su perfil público."""
    perfil   = request.user.perfil
    trabajos = request.user.trabajos_portafolio.all()
    return render(request, 'portafolio/mi_portafolio.html', {
        'trabajos':     trabajos,
        'trabajo_form': TrabajoForm(),
        'perfil_form':  PerfilForm(instance=perfil, user=request.user),
    })


@login_required
def subir_trabajo(request):
    """POST: agrega una nueva foto al portafolio."""
    if request.method == 'POST':
        form = TrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            t = form.save(commit=False)
            t.tatuador = request.user
            t.save()
    return redirect('mi_portafolio')


@login_required
def eliminar_trabajo(request, trabajo_id):
    """POST: elimina un trabajo del portafolio."""
    trabajo = get_object_or_404(Trabajo, id=trabajo_id)
    if trabajo.tatuador != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        trabajo.imagen.delete(save=False)
        trabajo.delete()
    return redirect('mi_portafolio')


@login_required
def editar_perfil(request):
    """POST: guarda los datos de perfil del tatuador."""
    perfil = request.user.perfil
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil, user=request.user)
        if form.is_valid():
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name  = form.cleaned_data.get('last_name',  '')
            request.user.email      = form.cleaned_data.get('email',      '')
            request.user.save()
            form.save()
    return redirect('mi_portafolio')
