import uuid
from django.db import models
from django.contrib.auth.models import User

class Cotizacion(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente de revisión'),
        ('aceptada', 'Aceptada - Esperando anticipo'),
        ('pagada', 'Anticipo Recibido - Lista para agendar'),
    )
    
    # Datos del cliente (Sin necesidad de cuenta)
    nombre_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField()
    telefono_cliente = models.CharField(max_length=20)
    
    # Este será nuestro "Magic Link" secreto para este cliente
    token_acceso = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    tatuador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cotizaciones_recibidas')
    
    # Detalles del tatuaje
    estilo = models.CharField(max_length=50)
    zona_cuerpo = models.CharField(max_length=100)
    tamano = models.CharField(max_length=50) 
    imagen_referencia = models.ImageField(upload_to='referencias/')
    
    # ¡NUEVO! El cliente elige su fecha ideal desde el principio
    fecha_solicitada = models.DateTimeField()
    
    # Proceso de pago
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_anticipo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    comprobante_anticipo = models.ImageField(upload_to='comprobantes/', null=True, blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_cliente} -> {self.tatuador.username} ({self.fecha_solicitada.date()})"