from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Trabajo
from .forms import TrabajoForm, PerfilForm


def galeria_portafolio(request):
    tatuadores = (
        User.objects
        .filter(perfil__rol='tatuador')
        .prefetch_related('trabajos_portafolio')
        .distinct()
    )
    artistas = []
    for tatuador in tatuadores:
        trabajos = list(tatuador.trabajos_portafolio.all())
        if trabajos:
            artistas.append({
                'tatuador': tatuador,
                'preview':  trabajos[:3],
                'total':    len(trabajos),
                'estilos':  list({t.estilo for t in trabajos}),
            })
    return render(request, 'portafolio/galeria.html', {'artistas': artistas})


def perfil_tatuador(request, tatuador_id):
    tatuador = get_object_or_404(User, pk=tatuador_id, perfil__rol='tatuador')
    trabajos = tatuador.trabajos_portafolio.all()
    estilos  = list({t.estilo for t in trabajos})
    return render(request, 'portafolio/perfil_tatuador.html', {
        'tatuador': tatuador,
        'trabajos': trabajos,
        'estilos':  estilos,
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
