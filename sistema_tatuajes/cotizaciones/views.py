from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from .models import Cotizacion, ReferenciaImagen
from .forms import CotizacionForm, ComprobanteForm, CancelacionForm
from . import emails


# ─── VISTA PÚBLICA: el cliente solicita cotización ───────────────────────────

def solicitar_cotizacion(request, tatuador_id=None):
    """
    Si viene de un perfil de artista (/nueva/<id>/) el campo tatuador
    se oculta y se pre-llena automáticamente.
    """
    tatuador_inicial = None
    tatuador_obj     = None

    if tatuador_id:
        tatuador_obj     = get_object_or_404(User, pk=tatuador_id, perfil__rol='tatuador')
        tatuador_inicial = tatuador_obj

    if request.method == 'POST':
        form = CotizacionForm(request.POST, request.FILES,
                               tatuador_inicial=tatuador_inicial)
        if form.is_valid():
            cotizacion = form.save()
            # Save uploaded reference images (up to 6)
            archivos = request.FILES.getlist('referencias')
            for i, archivo in enumerate(archivos[:6]):
                ReferenciaImagen.objects.create(cotizacion=cotizacion, imagen=archivo, orden=i)
            emails.correo_cotizacion_pedida(cotizacion)
            return redirect('galeria')
    else:
        form = CotizacionForm(tatuador_inicial=tatuador_inicial)

    return render(request, 'cotizaciones/formulario.html', {
        'form': form,
        'tatuador_obj': tatuador_obj,
    })


# ─── VISTA DE RECEPCIÓN (solo tatuadores logueados) ──────────────────────────

@login_required
def recepcion_tatuador(request):
    """El tatuador ve únicamente sus propias cotizaciones activas."""
    pendientes = Cotizacion.objects.filter(
        tatuador=request.user,
        estado='pendiente',
    ).order_by('fecha_creacion')

    anticipo_subido = Cotizacion.objects.filter(
        tatuador=request.user,
        estado='anticipo_subido',
    ).order_by('fecha_creacion')

    historial = Cotizacion.objects.filter(
        tatuador=request.user,
        estado__in=['confirmada', 'cancelada', 'abierta', 'cotizada'],
    ).order_by('-fecha_creacion')[:10]

    return render(request, 'cotizaciones/recepcion.html', {
        'pendientes':      pendientes,
        'anticipo_subido': anticipo_subido,
        'historial':       historial,
    })


# ─── COTIZAR: tatuador asigna precio ─────────────────────────────────────────

@login_required
def aceptar_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)

    # Verificar que le pertenece al tatuador logueado
    if cotizacion.tatuador != request.user:
        return HttpResponseForbidden("No tienes permiso para esta cotización.")

    if request.method == 'POST':
        cotizacion.monto_total     = request.POST.get('monto_total')
        cotizacion.monto_anticipo  = request.POST.get('monto_anticipo')
        cotizacion.estado          = 'cotizada'
        cotizacion.save()
        emails.correo_cotizacion_enviada(cotizacion)
        return redirect('recepcion_tatuador')

    return render(request, 'cotizaciones/aceptar.html', {'cotizacion': cotizacion})


# ─── MAGIC LINK: panel privado del cliente ───────────────────────────────────

def estado_magico_cliente(request, token):
    cotizacion = get_object_or_404(Cotizacion, token_acceso=token)

    if request.method == 'POST':
        form = ComprobanteForm(request.POST, request.FILES, instance=cotizacion)
        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.estado = 'anticipo_subido'
            cotizacion.save()
            emails.correo_anticipo_subido(cotizacion)
            return redirect('estado_magico', token=token)
    else:
        form = ComprobanteForm(instance=cotizacion)

    return render(request, 'cotizaciones/estado_magico.html', {
        'form': form,
        'cotizacion': cotizacion,
    })


# ─── CANCELAR por el cliente (desde magic link) ──────────────────────────────

def cancelar_por_cliente(request, token):
    cotizacion = get_object_or_404(Cotizacion, token_acceso=token)

    # Solo se puede cancelar si la cita no está ya confirmada o cancelada
    if cotizacion.estado in ('confirmada', 'cancelada'):
        return redirect('estado_magico', token=token)

    if request.method == 'POST':
        form = CancelacionForm(request.POST)
        if form.is_valid():
            cotizacion.estado           = 'cancelada'
            cotizacion.cancelada_por    = 'cliente'
            cotizacion.notas_cancelacion = form.cleaned_data.get('notas', '')
            cotizacion.save()
            emails.correo_cancelacion_cliente(cotizacion)
            return redirect('estado_magico', token=token)
    else:
        form = CancelacionForm()

    return render(request, 'cotizaciones/cancelar.html', {
        'form': form,
        'cotizacion': cotizacion,
        'cancelador': 'cliente',
    })


# ─── DEJAR FECHA ABIERTA (desde magic link) ───────────────────────────────────

def dejar_abierta(request, token):
    cotizacion = get_object_or_404(Cotizacion, token_acceso=token)

    if cotizacion.estado in ('confirmada', 'cancelada'):
        return redirect('estado_magico', token=token)

    cotizacion.estado = 'abierta'
    cotizacion.save()
    emails.correo_fecha_abierta(cotizacion)
    return redirect('estado_magico', token=token)


# ─── CANCELAR por el tatuador (desde recepción) ──────────────────────────────

@login_required
def cancelar_por_tatuador(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)

    if cotizacion.tatuador != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CancelacionForm(request.POST)
        if form.is_valid():
            cotizacion.estado            = 'cancelada'
            cotizacion.cancelada_por     = 'tatuador'
            cotizacion.notas_cancelacion = form.cleaned_data.get('notas', '')
            cotizacion.save()
            emails.correo_cancelacion_tatuador(cotizacion)
            return redirect('recepcion_tatuador')
    else:
        form = CancelacionForm()

    return render(request, 'cotizaciones/cancelar.html', {
        'form': form,
        'cotizacion': cotizacion,
        'cancelador': 'tatuador',
    })


# ─── DETALLE DE COTIZACIÓN (solo tatuador dueño) ─────────────────────────────

@login_required
def detalle_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)

    if cotizacion.tatuador != request.user:
        return HttpResponseForbidden("No tienes permiso para ver esta cotización.")

    return render(request, 'cotizaciones/detalle.html', {
        'cotizacion': cotizacion,
    })


# ─── NOTIFICACIONES ──────────────────────────────────────────────────────────

@login_required
def marcar_notificaciones_leidas(request):
    from usuarios.models import Notificacion
    Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
    return redirect(request.META.get('HTTP_REFERER', 'recepcion_tatuador'))
