"""
Módulo centralizado de correos y notificaciones del sistema.

Cada evento del flujo dispara:
  1. Un correo al destinatario correspondiente.
  2. Una notificación interna (si el destinatario tiene cuenta de usuario).
"""
from django.core.mail import send_mail
from django.conf import settings

BASE_URL = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')


# ─── helpers ──────────────────────────────────────────────────────────────────

def _notificar(usuario, mensaje, url=''):
    """Crea una notificación interna para un usuario con cuenta."""
    from usuarios.models import Notificacion
    Notificacion.objects.create(usuario=usuario, mensaje=mensaje, url=url)


def _enlace_cliente(cotizacion):
    return f"{BASE_URL}/cotizar/estado/{cotizacion.token_acceso}/"


def _mail(asunto, cuerpo, destinatarios):
    """Envía un correo y absorbe errores para no romper el flujo."""
    try:
        send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL, destinatarios)
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")


# ─── PASO 1: Cliente envía solicitud ──────────────────────────────────────────

def correo_cotizacion_pedida(cotizacion):
    """Al tatuador: nueva solicitud de cotización."""
    nombre   = cotizacion.tatuador.get_full_name() or cotizacion.tatuador.username
    asunto   = f"🖊 Nueva solicitud de {cotizacion.nombre_cliente}"
    cuerpo   = (
        f"Hola {nombre},\n\n"
        f"El cliente {cotizacion.nombre_cliente} quiere un tatuaje de estilo "
        f"{cotizacion.estilo}{' para el día ' + cotizacion.fecha_solicitada.strftime('%d/%m/%Y') if cotizacion.fecha_solicitada else ' (fecha por definir)'}.\n\n"
        f"Zona: {cotizacion.zona_cuerpo} | Tamaño: {cotizacion.tamano}\n\n"
        f"Revisa tu panel de recepción para cotizar el trabajo:\n"
        f"{BASE_URL}/cotizar/recepcion/"
    )
    _mail(asunto, cuerpo, [cotizacion.tatuador.email])

    # Notificación interna al tatuador
    _notificar(
        cotizacion.tatuador,
        f"Nueva solicitud de {cotizacion.nombre_cliente} ({cotizacion.estilo})",
        url='/cotizar/recepcion/',
    )


# ─── PASO 2: Tatuador cotiza ───────────────────────────────────────────────────

def correo_cotizacion_enviada(cotizacion):
    """Al cliente: le llega el precio y su magic link para pagar."""
    tatuador_nombre = cotizacion.tatuador.get_full_name() or cotizacion.tatuador.username
    enlace          = _enlace_cliente(cotizacion)
    asunto  = "💰 Tu cotización de tatuaje está lista"
    cuerpo  = (
        f"Hola {cotizacion.nombre_cliente},\n\n"
        f"{tatuador_nombre} revisó tu idea. Aquí están los detalles:\n\n"
        f"  • Estilo: {cotizacion.estilo}\n"
        f"  • Fecha solicitada: {cotizacion.fecha_solicitada.strftime('%d/%m/%Y') if cotizacion.fecha_solicitada else 'Por definir'}\n"
        f"  • Precio total estimado: ${cotizacion.monto_total}\n"
        f"  • Anticipo para reservar la fecha: ${cotizacion.monto_anticipo}\n\n"
        f"Para aceptar y subir tu comprobante de pago, entra a tu enlace personal:\n"
        f"{enlace}\n\n"
        f"Este enlace es único y privado para ti."
    )
    _mail(asunto, cuerpo, [cotizacion.email_cliente])


# ─── PASO 3: Cliente sube comprobante ─────────────────────────────────────────

def correo_anticipo_subido(cotizacion):
    """Al tatuador: el cliente subió su comprobante, a verificar."""
    nombre  = cotizacion.tatuador.get_full_name() or cotizacion.tatuador.username
    asunto  = f"💳 {cotizacion.nombre_cliente} subió su comprobante de anticipo"
    cuerpo  = (
        f"Hola {nombre},\n\n"
        f"{cotizacion.nombre_cliente} subió el comprobante de anticipo (${cotizacion.monto_anticipo}) "
        f"para su tatuaje de {cotizacion.estilo}.\n\n"
        f"Por favor verifica el depósito en tu banco y, si todo está correcto, "
        f"confirma la cita y define el horario desde tu panel:\n"
        f"{BASE_URL}/cotizar/recepcion/"
    )
    _mail(asunto, cuerpo, [cotizacion.tatuador.email])

    _notificar(
        cotizacion.tatuador,
        f"{cotizacion.nombre_cliente} subió comprobante de anticipo — verifica y agenda.",
        url='/cotizar/recepcion/',
    )

    # Al cliente: confirmación de que su comprobante fue recibido
    enlace = _enlace_cliente(cotizacion)
    asunto_c = "✅ Comprobante recibido — estamos revisando tu pago"
    cuerpo_c = (
        f"Hola {cotizacion.nombre_cliente},\n\n"
        f"Recibimos tu comprobante de anticipo. El artista verificará el depósito "
        f"y te confirmará la fecha y hora exacta de tu cita.\n\n"
        f"Puedes revisar el estado de tu tatuaje en cualquier momento aquí:\n"
        f"{enlace}"
    )
    _mail(asunto_c, cuerpo_c, [cotizacion.email_cliente])


# ─── PASO 4: Tatuador confirma la cita ────────────────────────────────────────

def correo_cita_confirmada(cita):
    """A ambos: la cita está 100% confirmada con fecha y hora exacta."""
    cotizacion     = cita.cotizacion
    tatuador_nombre = cita.tatuador.get_full_name() or cita.tatuador.username
    fecha_hora     = cita.fecha_hora_inicio.strftime('%d/%m/%Y a las %H:%M')

    # Al cliente
    enlace  = _enlace_cliente(cotizacion)
    asunto  = "🎉 ¡Tu cita está confirmada!"
    cuerpo  = (
        f"Hola {cotizacion.nombre_cliente},\n\n"
        f"¡Todo listo! Tu cita con {tatuador_nombre} fue confirmada:\n\n"
        f"  📅 Fecha y hora: {fecha_hora}\n"
        f"  🎨 Estilo: {cotizacion.estilo}\n"
        f"  📍 Zona: {cotizacion.zona_cuerpo}\n\n"
        f"Recibirás recordatorios 7 días y 1 día antes de tu cita.\n\n"
        f"Revisa los detalles aquí:\n{enlace}"
    )
    _mail(asunto, cuerpo, [cotizacion.email_cliente])

    # Al tatuador
    asunto_t = f"✅ Cita confirmada con {cotizacion.nombre_cliente}"
    cuerpo_t = (
        f"Hola {tatuador_nombre},\n\n"
        f"Confirmaste la cita con {cotizacion.nombre_cliente}:\n\n"
        f"  📅 {fecha_hora}\n"
        f"  🎨 {cotizacion.estilo} — {cotizacion.zona_cuerpo}\n"
    )
    _mail(asunto_t, cuerpo_t, [cita.tatuador.email])

    _notificar(
        cita.tatuador,
        f"Cita confirmada con {cotizacion.nombre_cliente} el {fecha_hora}.",
        url='/cotizar/recepcion/',
    )


# ─── CANCELACIÓN: cliente cancela ─────────────────────────────────────────────

def correo_cancelacion_cliente(cotizacion):
    """Al tatuador: el cliente canceló su solicitud."""
    nombre  = cotizacion.tatuador.get_full_name() or cotizacion.tatuador.username
    asunto  = f"❌ {cotizacion.nombre_cliente} canceló su solicitud"
    cuerpo  = (
        f"Hola {nombre},\n\n"
        f"{cotizacion.nombre_cliente} canceló su solicitud de "
        f"{cotizacion.estilo} para el {cotizacion.fecha_solicitada.strftime('%d/%m/%Y')}.\n\n"
        f"Motivo: {cotizacion.notas_cancelacion or 'No especificado'}"
    )
    _mail(asunto, cuerpo, [cotizacion.tatuador.email])

    _notificar(
        cotizacion.tatuador,
        f"{cotizacion.nombre_cliente} canceló su solicitud de {cotizacion.estilo}.",
        url='/cotizar/recepcion/',
    )

    # Al cliente: confirmación de cancelación
    enlace  = _enlace_cliente(cotizacion)
    asunto_c = "Cancelación de tu solicitud de tatuaje"
    cuerpo_c = (
        f"Hola {cotizacion.nombre_cliente},\n\n"
        f"Tu solicitud de tatuaje ({cotizacion.estilo}) fue cancelada correctamente.\n\n"
        f"Si cambias de opinión, puedes hacer una nueva solicitud en:\n"
        f"{BASE_URL}/cotizar/nueva/"
    )
    _mail(asunto_c, cuerpo_c, [cotizacion.email_cliente])


# ─── CANCELACIÓN: tatuador cancela ────────────────────────────────────────────

def correo_cancelacion_tatuador(cotizacion):
    """Al cliente: el tatuador canceló la cita."""
    tatuador_nombre = cotizacion.tatuador.get_full_name() or cotizacion.tatuador.username
    asunto  = "Aviso importante sobre tu cita de tatuaje"
    cuerpo  = (
        f"Hola {cotizacion.nombre_cliente},\n\n"
        f"Lamentablemente, {tatuador_nombre} tuvo que cancelar tu cita de "
        f"{cotizacion.estilo} del {cotizacion.fecha_solicitada.strftime('%d/%m/%Y')}.\n\n"
        f"Motivo: {cotizacion.notas_cancelacion or 'No especificado'}\n\n"
        f"Por favor contáctanos para reprogramar o solicitar un reembolso.\n"
        f"Disculpa los inconvenientes."
    )
    _mail(asunto, cuerpo, [cotizacion.email_cliente])

    _notificar(
        cotizacion.tatuador,
        f"Cancelaste la cita de {cotizacion.nombre_cliente}.",
        url='/cotizar/recepcion/',
    )


# ─── FECHA ABIERTA ────────────────────────────────────────────────────────────

def correo_fecha_abierta(cotizacion):
    """Al tatuador: el cliente quiere mantener la solicitud abierta sin fecha fija."""
    nombre  = cotizacion.tatuador.get_full_name() or cotizacion.tatuador.username
    asunto  = f"📆 {cotizacion.nombre_cliente} quiere dejar su fecha abierta"
    cuerpo  = (
        f"Hola {nombre},\n\n"
        f"{cotizacion.nombre_cliente} desea mantener su solicitud de {cotizacion.estilo} "
        f"sin fecha fija por ahora.\n"
        f"Su cotización quedará marcada como 'Abierta' hasta que acuerden una fecha.\n\n"
        f"Revisa tu panel:\n{BASE_URL}/cotizar/recepcion/"
    )
    _mail(asunto, cuerpo, [cotizacion.tatuador.email])

    _notificar(
        cotizacion.tatuador,
        f"{cotizacion.nombre_cliente} dejó su fecha abierta ({cotizacion.estilo}).",
        url='/cotizar/recepcion/',
    )


# ─── RECORDATORIOS ────────────────────────────────────────────────────────────

def correo_recordatorio(cita, dias_antes):
    """Recordatorio enviado automáticamente 7 días y 1 día antes de la cita."""
    cotizacion      = cita.cotizacion
    tatuador_nombre = cita.tatuador.get_full_name() or cita.tatuador.username
    fecha_hora      = cita.fecha_hora_inicio.strftime('%d/%m/%Y a las %H:%M')
    label           = "1 semana" if dias_antes == 7 else "mañana"

    # Al cliente
    enlace   = _enlace_cliente(cotizacion)
    asunto_c = f"🔔 Recordatorio: tu tatuaje es {label}"
    cuerpo_c = (
        f"Hola {cotizacion.nombre_cliente},\n\n"
        f"Te recordamos que tu cita de tatuaje ({cotizacion.estilo}) con "
        f"{tatuador_nombre} es {label}:\n\n"
        f"  📅 {fecha_hora}\n"
        f"  📍 Zona: {cotizacion.zona_cuerpo}\n\n"
        f"Recuerda llegar descansado/a, hidratado/a y con la zona a tatuar limpia 😊\n\n"
        f"Revisa los detalles: {enlace}"
    )
    _mail(asunto_c, cuerpo_c, [cotizacion.email_cliente])

    # Al tatuador
    asunto_t = f"🔔 Recordatorio: cita con {cotizacion.nombre_cliente} es {label}"
    cuerpo_t = (
        f"Hola {tatuador_nombre},\n\n"
        f"Tu cita con {cotizacion.nombre_cliente} ({cotizacion.estilo}) es {label}:\n\n"
        f"  📅 {fecha_hora}\n"
        f"  📍 Zona: {cotizacion.zona_cuerpo} | Tamaño: {cotizacion.tamano}\n"
    )
    _mail(asunto_t, cuerpo_t, [cita.tatuador.email])

    _notificar(
        cita.tatuador,
        f"Recordatorio: cita con {cotizacion.nombre_cliente} es {label} — {fecha_hora}.",
        url='/cotizar/recepcion/',
    )
