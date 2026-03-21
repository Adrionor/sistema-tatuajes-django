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


class BloqueoAgenda(models.Model):
    """
    Periodo bloqueado manualmente por el tatuador.
    Puede ser vacaciones, un viaje a trabajar a otro estado/país, un evento, etc.
    Las fechas dentro de este rango NO aparecerán disponibles en el formulario de cotización.
    """
    TIPOS = (
        ('vacaciones',          'Vacaciones'),
        ('evento',              'Evento / Convención'),
        ('viaje_nacional',      'Viaje a otro estado'),
        ('viaje_internacional', 'Viaje internacional'),
        ('otro',                'Otro'),
    )

    tatuador     = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bloqueos_agenda'
    )
    tipo         = models.CharField(max_length=25, choices=TIPOS, default='otro')
    fecha_inicio = models.DateField()
    fecha_fin    = models.DateField()
    descripcion  = models.TextField(blank=True, help_text='Descripción opcional para el cliente')
    ciudad       = models.CharField(max_length=100, blank=True,
                                    help_text='Ciudad donde trabajará (solo para viajes)')
    pais         = models.CharField(max_length=80, blank=True, default='México',
                                    help_text='País (solo para viajes)')
    publico      = models.BooleanField(
        default=True,
        help_text='Si está activo, los clientes pueden ver este periodo en tu perfil público'
    )

    class Meta:
        ordering = ['fecha_inicio']

    def __str__(self):
        return (
            f"{self.tatuador.username}: {self.get_tipo_display()} "
            f"{self.fecha_inicio} – {self.fecha_fin}"
        )

    @property
    def es_viaje(self):
        return self.tipo in ('viaje_nacional', 'viaje_internacional')
