from django.db import models
from django.contrib.auth.models import User
from cotizaciones.models import Cotizacion


class Cita(models.Model):
    ESTADOS = (
        ('programada',  'Programada'),
        ('completada',  'Completada'),
        ('cancelada',   'Cancelada'),
    )

    cotizacion       = models.OneToOneField(Cotizacion, on_delete=models.CASCADE)
    tatuador         = models.ForeignKey(User, on_delete=models.CASCADE,
                                         related_name='citas_tatuador')

    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin    = models.DateTimeField()

    estado = models.CharField(max_length=15, choices=ESTADOS, default='programada')

    # Banderas para no enviar recordatorios duplicados
    recordatorio_semana_enviado = models.BooleanField(default=False)
    recordatorio_dia_enviado    = models.BooleanField(default=False)

    google_calendar_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return (
            f"Cita: {self.tatuador.username} con "
            f"{self.cotizacion.nombre_cliente} — "
            f"{self.fecha_hora_inicio.strftime('%d/%m/%Y %H:%M')}"
        )
