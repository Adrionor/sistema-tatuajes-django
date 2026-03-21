from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
import calendar
from datetime import date, timedelta
from cotizaciones.models import Cotizacion
from cotizaciones import emails
from .models import Cita, BloqueoAgenda
from . import services


@login_required
def agenda_tatuador(request):
    """Vista de agenda mensual + lista de próximas citas."""
    hoy = timezone.now().date()

    # Mes a mostrar (parámetros GET: ?anio=2026&mes=4)
    try:
        anio = int(request.GET.get('anio', hoy.year))
        mes  = int(request.GET.get('mes',  hoy.month))
        if mes < 1:  anio -= 1; mes = 12
        if mes > 12: anio += 1; mes = 1
    except (ValueError, TypeError):
        anio, mes = hoy.year, hoy.month

    # Navegación prev/next
    if mes == 1:
        prev_mes, prev_anio = 12, anio - 1
    else:
        prev_mes, prev_anio = mes - 1, anio
    if mes == 12:
        next_mes, next_anio = 1, anio + 1
    else:
        next_mes, next_anio = mes + 1, anio

    # Citas del mes visible
    primer_dia = date(anio, mes, 1)
    ultimo_dia = date(anio, mes, calendar.monthrange(anio, mes)[1])

    citas_mes = Cita.objects.filter(
        tatuador=request.user,
        fecha_hora_inicio__date__gte=primer_dia,
        fecha_hora_inicio__date__lte=ultimo_dia,
    ).select_related('cotizacion').order_by('fecha_hora_inicio')

    # Indexar citas por día para el grid
    citas_por_dia = {}
    for cita in citas_mes:
        d = cita.fecha_hora_inicio.date().day
        citas_por_dia.setdefault(d, []).append(cita)

    # Bloqueos que se solapan con el mes visible
    bloqueos_mes = BloqueoAgenda.objects.filter(
        tatuador=request.user,
        fecha_inicio__lte=ultimo_dia,
        fecha_fin__gte=primer_dia,
    )
    # Conjunto de días bloqueados en el mes para el grid
    dias_bloqueados = set()
    for b in bloqueos_mes:
        d_ini = max(b.fecha_inicio, primer_dia)
        d_fin = min(b.fecha_fin,   ultimo_dia)
        cur   = d_ini
        while cur <= d_fin:
            dias_bloqueados.add(cur.day)
            cur += timedelta(days=1)

    # Construir el grid del calendario
    cal = calendar.monthcalendar(anio, mes)  # lista de semanas (0 = fuera del mes)

    # Próximas citas (siguiente 60 días)
    proximas = Cita.objects.filter(
        tatuador=request.user,
        estado='programada',
        fecha_hora_inicio__date__gte=hoy,
        fecha_hora_inicio__date__lte=hoy + timedelta(days=60),
    ).select_related('cotizacion').order_by('fecha_hora_inicio')

    # Próximos bloqueos / viajes (siguiente 90 días)
    proximos_bloqueos = BloqueoAgenda.objects.filter(
        tatuador=request.user,
        fecha_fin__gte=hoy,
    ).order_by('fecha_inicio')[:10]

    return render(request, 'citas/agenda.html', {
        'hoy':             hoy,
        'anio':            anio,
        'mes':             mes,
        'mes_nombre':      ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][mes],
        'cal':             cal,
        'citas_por_dia':   citas_por_dia,
        'dias_bloqueados': dias_bloqueados,
        'proximas':        proximas,
        'proximos_bloqueos': proximos_bloqueos,
        'prev_mes':        prev_mes,
        'prev_anio':       prev_anio,
        'next_mes':        next_mes,
        'next_anio':       next_anio,
    })


@login_required
def confirmar_y_agendar(request, cotizacion_id):
    """
    El tatuador verificó el depósito y ahora define el horario exacto.
    Crea la Cita oficial y marca la cotización como confirmada.
    """
    cotizacion = get_object_or_404(
        Cotizacion, id=cotizacion_id, estado='anticipo_subido'
    )

    if cotizacion.tatuador != request.user:
        return HttpResponseForbidden("No tienes permiso para esta cotización.")

    if request.method == 'POST':
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone as tz

        fecha_inicio_str = request.POST.get('fecha_inicio')
        fecha_fin_str    = request.POST.get('fecha_fin')

        # parse_datetime handles "YYYY-MM-DDTHH:MM" sent by datetime-local inputs
        fecha_inicio = parse_datetime(fecha_inicio_str)
        fecha_fin    = parse_datetime(fecha_fin_str)

        # Make timezone-aware if the parsed value is naive
        if fecha_inicio and tz.is_naive(fecha_inicio):
            fecha_inicio = tz.make_aware(fecha_inicio)
        if fecha_fin and tz.is_naive(fecha_fin):
            fecha_fin = tz.make_aware(fecha_fin)

        if not fecha_inicio:
            return render(request, 'citas/agendar.html', {
                'cotizacion': cotizacion,
                'error': 'La fecha de inicio no es válida.',
            })

        # Crear la cita
        nueva_cita = Cita.objects.create(
            cotizacion        = cotizacion,
            tatuador          = cotizacion.tatuador,
            fecha_hora_inicio = fecha_inicio,
            fecha_hora_fin    = fecha_fin,
        )

        # Marcar la cotización como confirmada
        cotizacion.estado = 'confirmada'
        cotizacion.save()

        # Enviar correos de confirmación a ambas partes
        emails.correo_cita_confirmada(nueva_cita)

        # Intentar sincronizar con Google Calendar (opcional)
        google_id = services.crear_evento_google_calendar(nueva_cita)
        if google_id:
            nueva_cita.google_calendar_id = google_id
            nueva_cita.save()

        return redirect('recepcion_tatuador')

    return render(request, 'citas/agendar.html', {'cotizacion': cotizacion})


@login_required
def cancelar_cita(request, cita_id):
    """El tatuador cancela una cita ya confirmada."""
    cita       = get_object_or_404(Cita, id=cita_id)
    cotizacion = cita.cotizacion

    if cita.tatuador != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        cita.estado                  = 'cancelada'
        cita.save()
        cotizacion.estado            = 'cancelada'
        cotizacion.cancelada_por     = 'tatuador'
        cotizacion.notas_cancelacion = motivo
        cotizacion.save()
        emails.correo_cancelacion_tatuador(cotizacion)
        return redirect('recepcion_tatuador')

    return render(request, 'citas/cancelar_cita.html', {'cita': cita})


def api_periodos_bloqueados(request, tatuador_id):
    """
    API: devuelve los rangos de fechas bloqueadas de un tatuador.
    Formato: [{"from": "2026-04-01", "to": "2026-04-07"}, ...]
    Flatpickr acepta este formato en su opción `disable`.
    Los días con citas ya agendadas NO se bloquean — el tatuador puede
    atender a varias personas en el mismo día en diferentes horarios.
    """
    bloqueos = BloqueoAgenda.objects.filter(tatuador_id=tatuador_id)
    rangos = [
        {'from': b.fecha_inicio.strftime('%Y-%m-%d'),
         'to':   b.fecha_fin.strftime('%Y-%m-%d')}
        for b in bloqueos
    ]
    return JsonResponse(rangos, safe=False)


# ─── Gestión de bloqueos ──────────────────────────────────────────────────────

@login_required
def gestionar_bloqueos(request):
    """Lista de periodos bloqueados del tatuador, con botón para crear/eliminar."""
    bloqueos = BloqueoAgenda.objects.filter(
        tatuador=request.user
    ).order_by('fecha_inicio')
    return render(request, 'citas/bloqueos.html', {'bloqueos': bloqueos})


@login_required
def crear_bloqueo(request):
    """Crear un nuevo periodo de bloqueo."""
    if request.method == 'POST':
        from django.utils.dateparse import parse_date
        tipo         = request.POST.get('tipo', 'otro')
        fecha_inicio = parse_date(request.POST.get('fecha_inicio', ''))
        fecha_fin    = parse_date(request.POST.get('fecha_fin', ''))
        descripcion  = request.POST.get('descripcion', '').strip()
        ciudad       = request.POST.get('ciudad', '').strip()
        pais         = request.POST.get('pais', 'México').strip() or 'México'
        publico      = request.POST.get('publico') == 'on'

        if not fecha_inicio or not fecha_fin:
            from django.contrib import messages
            messages.error(request, 'Las fechas son obligatorias.')
            return redirect('gestionar_bloqueos')

        if fecha_fin < fecha_inicio:
            from django.contrib import messages
            messages.error(request, 'La fecha de fin no puede ser anterior a la de inicio.')
            return redirect('gestionar_bloqueos')

        BloqueoAgenda.objects.create(
            tatuador=request.user,
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            descripcion=descripcion,
            ciudad=ciudad,
            pais=pais,
            publico=publico,
        )
        from django.contrib import messages
        messages.success(request, 'Periodo bloqueado correctamente.')
    return redirect('gestionar_bloqueos')


@login_required
def eliminar_bloqueo(request, bloqueo_id):
    """Elimina un bloqueo propio."""
    bloqueo = get_object_or_404(BloqueoAgenda, pk=bloqueo_id, tatuador=request.user)
    if request.method == 'POST':
        bloqueo.delete()
        from django.contrib import messages
        messages.success(request, 'Bloqueo eliminado.')
    return redirect('gestionar_bloqueos')
