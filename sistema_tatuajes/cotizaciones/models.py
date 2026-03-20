import uuid
from django.db import models
from django.contrib.auth.models import User


class Cotizacion(models.Model):
    ESTADOS = (
        ('pendiente',       'Pendiente de revisión'),
        ('cotizada',        'Cotizada — Esperando anticipo'),
        ('anticipo_subido', 'Anticipo subido — Verificar depósito'),
        ('confirmada',      'Cita confirmada'),
        ('cancelada',       'Cancelada'),
        ('abierta',         'Fecha abierta — Por agendar'),
    )

    CANCELADA_POR = (
        ('cliente',  'Cliente'),
        ('tatuador', 'Tatuador'),
    )

    # Datos del cliente (sin necesidad de cuenta)
    nombre_cliente   = models.CharField(max_length=100)
    email_cliente    = models.EmailField()
    telefono_cliente = models.CharField(max_length=20)

    # Magic Link de acceso privado
    token_acceso = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    tatuador = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cotizaciones_recibidas'
    )

    # Detalles del tatuaje
    estilo          = models.CharField(max_length=50)
    zona_cuerpo     = models.CharField(max_length=100)
    tamano          = models.CharField(max_length=50)
    imagen_referencia = models.ImageField(upload_to='referencias/')

    # El cliente elige solo la fecha; el tatuador define la hora al confirmar
    fecha_solicitada = models.DateField(null=True, blank=True)

    # Proceso de pago
    estado          = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    monto_total     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_anticipo  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    comprobante_anticipo = models.ImageField(upload_to='comprobantes/', null=True, blank=True)

    # Notas libres del cliente al solicitar
    notas_cliente       = models.TextField(blank=True, help_text='Descripción libre: ideas, referencias, detalles especiales, etc.')

    # Cancelación
    cancelada_por       = models.CharField(max_length=10, choices=CANCELADA_POR, blank=True)
    notas_cancelacion   = models.TextField(blank=True)

    fecha_creacion  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_cliente} → {self.tatuador.username} ({self.fecha_solicitada or 'fecha abierta'})"


class Mensaje(models.Model):
    AUTOR_CHOICES = (
        ('tatuador', 'Tatuador'),
        ('cliente',  'Cliente'),
    )

    cotizacion     = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='mensajes')
    autor          = models.CharField(max_length=10, choices=AUTOR_CHOICES)
    texto          = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_creacion']

    def __str__(self):
        return f"[{self.autor}] {self.cotizacion.nombre_cliente} — {self.fecha_creacion:%d/%m/%Y %H:%M}"
