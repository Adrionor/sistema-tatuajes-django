from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from .models import Perfil, ConfiguracionEstudio
from .forms import CrearTatuadorForm, PerfilTatuadorForm, EditarUsuarioForm, ConfiguracionEstudioForm
from cotizaciones.models import Cotizacion
from citas.models import Cita


# ─── Decorador propietario ────────────────────────────────────────────────────

def propietario_required(view_func):
    """Solo el propietario (o superuser) puede acceder."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            es_prop = request.user.perfil.rol == 'propietario'
        except Perfil.DoesNotExist:
            es_prop = False
        if es_prop or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Acceso restringido al propietario del estudio.')
        return redirect('recepcion_tatuador')
    return wrapper


# ─── Dashboard ────────────────────────────────────────────────────────────────

@propietario_required
def panel_dashboard(request):
    hoy = timezone.localdate()

    total_tatuadores  = User.objects.filter(perfil__rol='tatuador', is_active=True).count()
    colaboraciones    = User.objects.filter(
        perfil__rol='tatuador', perfil__es_colaboracion=True, is_active=True
    ).count()
    citas_hoy         = Cita.objects.filter(
        fecha_hora_inicio__date=hoy, estado='programada'
    ).count()
    pendientes        = Cotizacion.objects.filter(estado='pendiente').count()
    anticipo_subido   = Cotizacion.objects.filter(estado='anticipo_subido').count()
    confirmadas_total = Cotizacion.objects.filter(estado='confirmada').count()

    ultimas_cotizaciones = (
        Cotizacion.objects
        .select_related('tatuador')
        .order_by('-fecha_creacion')[:8]
    )

    proximas_citas = (
        Cita.objects
        .select_related('tatuador', 'cotizacion')
        .filter(estado='programada', fecha_hora_inicio__gte=timezone.now())
        .order_by('fecha_hora_inicio')[:6]
    )

    return render(request, 'panel/dashboard.html', {
        'total_tatuadores':     total_tatuadores,
        'colaboraciones':       colaboraciones,
        'citas_hoy':            citas_hoy,
        'pendientes':           pendientes,
        'anticipo_subido':      anticipo_subido,
        'confirmadas_total':    confirmadas_total,
        'ultimas_cotizaciones': ultimas_cotizaciones,
        'proximas_citas':       proximas_citas,
    })


# ─── Gestión de tatuadores ────────────────────────────────────────────────────

@propietario_required
def panel_tatuadores(request):
    filtro = request.GET.get('filtro', 'todos')

    qs = User.objects.filter(
        Q(perfil__rol='tatuador') | Q(perfil__rol='propietario')
    ).select_related('perfil').order_by('first_name', 'username')

    if filtro == 'colaboracion':
        qs = qs.filter(perfil__es_colaboracion=True)
    elif filtro == 'permanente':
        qs = qs.filter(perfil__es_colaboracion=False, is_active=True)
    elif filtro == 'inactivo':
        qs = qs.filter(is_active=False)
    else:  # todos
        qs = qs.filter(is_active=True)

    tatuadores = []
    for u in qs:
        tatuadores.append({
            'user':          u,
            'perfil':        u.perfil,
            'n_cotizaciones': Cotizacion.objects.filter(tatuador=u).count(),
            'n_trabajos':     u.trabajos_portafolio.count(),
        })

    return render(request, 'panel/tatuadores.html', {
        'tatuadores': tatuadores,
        'filtro':     filtro,
    })


@propietario_required
def panel_crear_tatuador(request):
    if request.method == 'POST':
        user_form   = CrearTatuadorForm(request.POST)
        perfil_form = PerfilTatuadorForm(request.POST, request.FILES)

        if user_form.is_valid() and perfil_form.is_valid():
            user = user_form.save(commit=False)
            user.first_name = user_form.cleaned_data['first_name']
            user.last_name  = user_form.cleaned_data.get('last_name', '')
            user.email      = user_form.cleaned_data.get('email', '')
            user.save()

            perfil, _ = Perfil.objects.get_or_create(usuario=user)
            pf = perfil_form.save(commit=False)
            pf.pk      = perfil.pk
            pf.usuario = user
            pf.save()

            messages.success(request, f'Tatuador @{user.username} creado correctamente.')
            return redirect('panel_tatuadores')
    else:
        user_form   = CrearTatuadorForm()
        perfil_form = PerfilTatuadorForm(initial={'rol': 'tatuador'})

    return render(request, 'panel/crear_tatuador.html', {
        'user_form':   user_form,
        'perfil_form': perfil_form,
    })


@propietario_required
def panel_editar_usuario(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    perfil, _ = Perfil.objects.get_or_create(usuario=usuario)

    if request.method == 'POST':
        user_form   = EditarUsuarioForm(request.POST, instance=usuario)
        perfil_form = PerfilTatuadorForm(request.POST, request.FILES, instance=perfil)

        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, f'Usuario @{usuario.username} actualizado.')
            return redirect('panel_tatuadores')
    else:
        user_form   = EditarUsuarioForm(instance=usuario)
        perfil_form = PerfilTatuadorForm(instance=perfil)

    return render(request, 'panel/editar_usuario.html', {
        'usuario':     usuario,
        'user_form':   user_form,
        'perfil_form': perfil_form,
    })


@propietario_required
def panel_toggle_activo(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    if usuario == request.user:
        messages.warning(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('panel_tatuadores')
    usuario.is_active = not usuario.is_active
    usuario.save()
    estado = 'activado' if usuario.is_active else 'desactivado'
    messages.success(request, f'Usuario @{usuario.username} {estado}.')
    return redirect('panel_tatuadores')


@propietario_required
def panel_eliminar_tatuador(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    if usuario == request.user:
        messages.warning(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('panel_tatuadores')
    if request.method == 'POST':
        nombre = usuario.username
        usuario.delete()
        messages.success(request, f'La cuenta @{nombre} fue eliminada.')
    return redirect('panel_tatuadores')


# ─── Clientes ─────────────────────────────────────────────────────────────────

@propietario_required
def panel_clientes(request):
    busqueda = request.GET.get('q', '').strip()

    clientes = (
        Cotizacion.objects
        .values('nombre_cliente', 'email_cliente', 'telefono_cliente')
        .annotate(total=Count('id'))
        .order_by('nombre_cliente')
    )

    if busqueda:
        clientes = clientes.filter(
            Q(nombre_cliente__icontains=busqueda) |
            Q(email_cliente__icontains=busqueda)
        )

    resultado = []
    for c in clientes:
        ultima = (
            Cotizacion.objects
            .filter(email_cliente=c['email_cliente'])
            .order_by('-fecha_creacion')
            .first()
        )
        resultado.append({**c, 'ultima': ultima})

    return render(request, 'panel/clientes.html', {
        'clientes': resultado,
        'busqueda': busqueda,
    })


# ─── Cotizaciones (vista global del propietario) ──────────────────────────────

@propietario_required
def panel_cotizaciones(request):
    estado   = request.GET.get('estado', '')
    artista  = request.GET.get('artista', '')
    busqueda = request.GET.get('q', '').strip()

    qs = Cotizacion.objects.select_related('tatuador').order_by('-fecha_creacion')

    if estado:
        qs = qs.filter(estado=estado)
    if artista:
        qs = qs.filter(tatuador__username=artista)
    if busqueda:
        qs = qs.filter(
            Q(nombre_cliente__icontains=busqueda) |
            Q(email_cliente__icontains=busqueda)
        )

    tatuadores = User.objects.filter(
        Q(perfil__rol='tatuador') | Q(perfil__rol='propietario')
    ).order_by('first_name')

    ESTADO_LABELS = {
        'pendiente':       'Pendiente',
        'cotizada':        'Cotizada',
        'anticipo_subido': 'Anticipo subido',
        'confirmada':      'Confirmada',
        'abierta':         'Fecha abierta',
        'cancelada':       'Cancelada',
    }

    return render(request, 'panel/cotizaciones.html', {
        'cotizaciones':  qs[:100],
        'estado':        estado,
        'artista':       artista,
        'busqueda':      busqueda,
        'tatuadores':    tatuadores,
        'ESTADO_LABELS': ESTADO_LABELS,
    })


# ─── Configuración del estudio ────────────────────────────────────────────────

@propietario_required
def panel_configuracion(request):
    config = ConfiguracionEstudio.get_config()

    if request.method == 'POST':
        form = ConfiguracionEstudioForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada correctamente.')
            return redirect('panel_configuracion')
    else:
        form = ConfiguracionEstudioForm(instance=config)

    return render(request, 'panel/configuracion.html', {
        'form':   form,
        'config': config,
    })
