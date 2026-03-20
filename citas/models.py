from django.db import models
from django.contrib.auth.models import User
from cotizaciones.models import Cotizacion

class Cita(models.Model):
    cotizacion = models.OneToOneField(Cotizacion, on_delete=models.CASCADE)
    tatuador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citas_tatuador')
    
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()
    
    google_calendar_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Cita: {self.tatuador.username} con {self.cotizacion.nombre_cliente}"