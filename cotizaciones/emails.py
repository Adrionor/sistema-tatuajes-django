from django.core.mail import send_mail
from django.conf import settings

def correo_cotizacion_pedida(cotizacion):
    asunto = f"Nueva solicitud de tatuaje de {cotizacion.nombre_cliente}"
    mensaje = f"Hola {cotizacion.tatuador.username},\n\nEl cliente {cotizacion.nombre_cliente} ha solicitado una cotización para un tatuaje estilo {cotizacion.estilo} el día {cotizacion.fecha_solicitada.strftime('%d/%m/%Y')}.\nPor favor revisa tu panel de recepción."
    send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [cotizacion.tatuador.email])

def correo_cotizacion_aceptada(cotizacion):
    asunto = "¡Tu cotización de tatuaje ha sido respondida!"
    # ¡AQUÍ ESTÁ LA MAGIA! Creamos el enlace único usando su token secreto
    enlace_magico = f"http://127.0.0.1:8000/cotizar/estado/{cotizacion.token_acceso}/"
    
    mensaje = f"Hola {cotizacion.nombre_cliente},\n\nEl artista {cotizacion.tatuador.username} ha revisado tu idea. El costo total estimado es de ${cotizacion.monto_total}.\nPara agendar, requerimos un anticipo de ${cotizacion.monto_anticipo}.\n\nPara aceptar el precio y subir tu comprobante de pago, haz clic en tu enlace seguro y personal:\n{enlace_magico}"
    
    send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [cotizacion.email_cliente])

def correo_comprobante_subido(cotizacion):
    asunto = f"Comprobante de anticipo recibido - {cotizacion.nombre_cliente}"
    mensaje = f"Hola {cotizacion.tatuador.username},\n\nEl cliente {cotizacion.nombre_cliente} ha subido su comprobante de pago.\nPor favor revisa tu panel para confirmar de recibido y agendar la cita."
    send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [cotizacion.tatuador.email])

def correo_cita_agendada(cita):
    asunto = "¡Tu cita de tatuaje está 100% confirmada!"
    mensaje = f"Hola {cita.cotizacion.nombre_cliente},\n\n¡Excelentes noticias! Hemos confirmado tu pago. Tu cita con {cita.tatuador.username} ha sido agendada para el {cita.fecha_hora_inicio.strftime('%d/%m/%Y a las %H:%M')}.\n\n¡Te esperamos!"
    send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [cita.cotizacion.email_cliente])