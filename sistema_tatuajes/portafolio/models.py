from django.db import models
from django.contrib.auth.models import User

class Trabajo(models.Model):
    tatuador     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trabajos_portafolio')
    imagen       = models.ImageField(upload_to='portafolio/')
    titulo       = models.CharField(max_length=100, blank=True, help_text='Título opcional (ej: "Manga floral")')
    descripcion  = models.TextField(blank=True, null=True)
    estilo       = models.CharField(max_length=50)
    fecha_subida = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"Trabajo de {self.tatuador.username} - {self.estilo}"