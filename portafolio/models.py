from django.db import models
from django.contrib.auth.models import User

class Trabajo(models.Model):
    tatuador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trabajos_portafolio')
    imagen = models.ImageField(upload_to='portafolio/')
    descripcion = models.TextField(blank=True, null=True)
    estilo = models.CharField(max_length=50) # Ej: Realismo, Americano Tradicional

    def __str__(self):
        return f"Trabajo de {self.tatuador.username} - {self.estilo}"