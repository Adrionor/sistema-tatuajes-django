from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from .models import Perfil, ConfiguracionEstudio, Anuncio, ImagenHero
from .forms import CrearTatuadorForm, PerfilTatuadorForm, EditarUsuarioForm, ConfiguracionEstudioForm, AnuncioForm, SuperadminEstudioForm, SuperadminPropietarioForm
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
    hoy    = timezone.localdate()
    studio = request.studio

    total_tatuadores  = User.objects.filter(
        perfil__rol='tatuador', perfil__estudio=studio, is_active=True
    ).count()
    colaboraciones    = User.objects.filter(
        perfil__rol='tatuador', perfil__estudio=studio,
        perfil__es_colaboracion=True, is_active=True
    ).count()
    citas_hoy         = Cita.objects.filter(
        tatuador__perfil__estudio=studio,
        fecha_hora_inicio__date=hoy, estado='programada'
    ).count()
    pendientes        = Cotizacion.objects.filter(
        tatuador__perfil__estudio=studio, estado='pendiente'
    ).count()
    anticipo_subido   = Cotizacion.objects.filter(
        tatuador__perfil__estudio=studio, estado='anticipo_subido'
    ).count()
    confirmadas_total = Cotizacion.objects.filter(
        tatuador__perfil__estudio=studio, estado='confirmada'
    ).count()

    ultimas_cotizaciones = (
        Cotizacion.objects
        .filter(tatuador__perfil__estudio=studio)
        .select_related('tatuador')
        .order_by('-fecha_creacion')[:8]
    )

    proximas_citas = (
        Cita.objects
        .select_related('tatuador', 'cotizacion')
        .filter(
            tatuador__perfil__estudio=studio,
            estado='programada', fecha_hora_inicio__gte=timezone.now()
        )
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
    studio = request.studio

    qs = User.objects.filter(
        Q(perfil__rol='tatuador') | Q(perfil__rol='propietario'),
        perfil__estudio=studio,
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
            pf.estudio = request.studio   # asignar al estudio actual
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
    # Solo permite editar usuarios que pertenezcan al mismo estudio
    usuario = get_object_or_404(User, pk=user_id, perfil__estudio=request.studio)
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
    usuario = get_object_or_404(User, pk=user_id, perfil__estudio=request.studio)
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
    usuario = get_object_or_404(User, pk=user_id, perfil__estudio=request.studio)
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
    studio   = request.studio

    clientes = (
        Cotizacion.objects
        .filter(tatuador__perfil__estudio=studio)
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
            .filter(
                tatuador__perfil__estudio=studio,
                email_cliente=c['email_cliente'],
            )
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
    studio   = request.studio

    qs = (
        Cotizacion.objects
        .filter(tatuador__perfil__estudio=studio)
        .select_related('tatuador')
        .order_by('-fecha_creacion')
    )

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
        Q(perfil__rol='tatuador') | Q(perfil__rol='propietario'),
        perfil__estudio=studio,
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
    config = request.studio

    if request.method == 'POST':
        form = ConfiguracionEstudioForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada correctamente.')
            return redirect('panel_configuracion')
    else:
        form = ConfiguracionEstudioForm(instance=config)

    imagenes_hero = ImagenHero.objects.filter(configuracion=config).order_by('orden', 'pk')
    return render(request, 'panel/configuracion.html', {
        'form':          form,
        'config':        config,
        'imagenes_hero': imagenes_hero,
    })


# ─── Redirección post-login ──────────────────────────────────────────────────────

def post_login_redirect(request):
    """
    Redirige al usuario al subdominio correcto de su estudio después de iniciar sesión.
    - Superusuario  → panel_dashboard (puede estar en cualquier subdominio)
    - Propietario / tatuador → subdominio de su estudio si está mal ubicado, o recepción
    """
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_superuser:
        return redirect('panel_dashboard')

    try:
        user_estudio = request.user.perfil.estudio
    except (Perfil.DoesNotExist, AttributeError):
        return redirect('recepcion_tatuador')

    # Si el estudio del usuario ya coincide con el tenant actual, listo
    if not user_estudio or user_estudio == request.studio:
        return redirect('recepcion_tatuador')

    # Intentar redirigir al subdominio correcto del estudio
    if user_estudio.subdominio:
        host = request.get_host().lower().split(':')[0]
        parts = host.split('.')

        # Local (localhost / 127.0.0.1): no hay subdomnios reales → ir directo
        if host in ('localhost', '127.0.0.1'):
            return redirect('recepcion_tatuador')

        # Producción: construir URL con el subdominio correcto
        if len(parts) >= 2:
            base = '.'.join(parts[1:]) if len(parts) > 2 else host
            scheme = 'https' if request.is_secure() else 'http'
            return redirect(f'{scheme}://{user_estudio.subdominio}.{base}/cotizar/recepcion/')

    return redirect('recepcion_tatuador')


# ─── Landing page ──────────────────────────────────────────────────────────────────

def landing(request):
    config   = request.studio
    anuncios = Anuncio.objects.filter(activo=True, estudio=config).select_related('tatuador_asociado')

    # Por cada anuncio con tatuador asociado, pre-cargar sus trabajos
    anuncios_data = []
    for anuncio in anuncios:
        trabajos = []
        if anuncio.tatuador_asociado:
            trabajos = list(
                anuncio.tatuador_asociado.trabajos_portafolio.all()[:6]
            )
        anuncios_data.append({
            'anuncio':  anuncio,
            'trabajos': trabajos,
        })

    imagenes_hero = list(
        ImagenHero.objects.filter(configuracion=config, activo=True).order_by('orden', 'pk')
    )

    layout = config.plantilla_layout or 'clasico'
    return render(request, f'landing_{layout}.html', {
        'config':        config,
        'anuncios_data': anuncios_data,
        'imagenes_hero': imagenes_hero,
    })


# ─── Imágenes Hero del carrusel ─────────────────────────────────────────

@propietario_required
def panel_subir_imagen_hero(request):
    if request.method == 'POST':
        config = request.studio
        for imagen in request.FILES.getlist('imagenes'):
            ImagenHero.objects.create(configuracion=config, imagen=imagen)
        messages.success(request, 'Imágenes añadidas al carrusel.')
    return redirect('panel_configuracion')


@propietario_required
def panel_eliminar_imagen_hero(request, imagen_id):
    img = get_object_or_404(ImagenHero, pk=imagen_id)
    img.imagen.delete(save=False)
    img.delete()
    messages.success(request, 'Imagen eliminada.')
    return redirect('panel_configuracion')


# ─── Panel de anuncios ─────────────────────────────────────────────────────────────────

@propietario_required
def panel_anuncios(request):
    anuncios = Anuncio.objects.filter(estudio=request.studio).select_related('tatuador_asociado').order_by('orden', '-created_at')
    return render(request, 'panel/anuncios.html', {'anuncios': anuncios})


@propietario_required
def panel_crear_anuncio(request):
    if request.method == 'POST':
        form = AnuncioForm(request.POST, request.FILES, studio=request.studio)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.estudio = request.studio
            anuncio.save()
            messages.success(request, 'Anuncio creado correctamente.')
            return redirect('panel_anuncios')
    else:
        form = AnuncioForm(studio=request.studio)
    return render(request, 'panel/crear_anuncio.html', {'form': form, 'editando': False})


@propietario_required
def panel_editar_anuncio(request, anuncio_id):
    anuncio = get_object_or_404(Anuncio, pk=anuncio_id, estudio=request.studio)
    if request.method == 'POST':
        form = AnuncioForm(request.POST, request.FILES, instance=anuncio, studio=request.studio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anuncio actualizado.')
            return redirect('panel_anuncios')
    else:
        form = AnuncioForm(instance=anuncio, studio=request.studio)
    return render(request, 'panel/crear_anuncio.html', {'form': form, 'editando': True, 'anuncio': anuncio})


@propietario_required
def panel_eliminar_anuncio(request, anuncio_id):
    anuncio = get_object_or_404(Anuncio, pk=anuncio_id, estudio=request.studio)
    if request.method == 'POST':
        anuncio.delete()
        messages.success(request, 'Anuncio eliminado.')
    return redirect('panel_anuncios')


# ─── Superadmin: gestión de estudios ─────────────────────────────────────────

def superadmin_required(view_func):
    """Solo superusuarios pueden acceder."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Acceso restringido a superadministradores.')
        return redirect('panel_dashboard')
    return wrapper


@superadmin_required
def superadmin_estudios(request):
    estudios = ConfiguracionEstudio.objects.annotate(
        num_miembros=Count('miembros')
    ).order_by('nombre')
    return render(request, 'panel/superadmin_estudios.html', {'estudios': estudios})


@superadmin_required
def superadmin_crear_estudio(request):
    estudio_form = SuperadminEstudioForm()
    prop_form    = SuperadminPropietarioForm()

    if request.method == 'POST':
        estudio_form = SuperadminEstudioForm(request.POST)
        prop_form    = SuperadminPropietarioForm(request.POST)
        if estudio_form.is_valid() and prop_form.is_valid():
            estudio = estudio_form.save()
            d = prop_form.cleaned_data
            user = User.objects.create_user(
                username=d['username'], password=d['password'],
                first_name=d['first_name'], last_name=d.get('last_name', ''),
                email=d.get('email', ''),
            )
            # get_or_create garantiza que el Perfil exista aunque no haya señal
            perfil, _ = Perfil.objects.get_or_create(usuario=user)
            perfil.rol    = 'propietario'
            perfil.estudio = estudio
            perfil.save()
            messages.success(request, f'Estudio "{estudio.nombre}" creado correctamente.')
            return redirect('superadmin_estudios')

    return render(request, 'panel/superadmin_estudio_form.html', {
        'estudio_form': estudio_form,
        'prop_form':    prop_form,
        'editando':     False,
    })


@superadmin_required
def superadmin_editar_estudio(request, estudio_id):
    estudio = get_object_or_404(ConfiguracionEstudio, pk=estudio_id)
    if request.method == 'POST':
        form = SuperadminEstudioForm(request.POST, instance=estudio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estudio actualizado.')
            return redirect('superadmin_estudios')
    else:
        form = SuperadminEstudioForm(instance=estudio)
    return render(request, 'panel/superadmin_estudio_form.html', {
        'estudio_form': form,
        'prop_form':    None,
        'editando':     True,
        'estudio':      estudio,
    })


@superadmin_required
def superadmin_eliminar_estudio(request, estudio_id):
    estudio = get_object_or_404(ConfiguracionEstudio, pk=estudio_id)
    if request.method == 'POST':
        nombre = estudio.nombre
        estudio.delete()
        messages.success(request, f'Estudio "{nombre}" eliminado.')
    return redirect('superadmin_estudios')
