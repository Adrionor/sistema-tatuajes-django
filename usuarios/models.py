from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    ROLES = (
        ('tatuador', 'Tatuador'),
        ('cliente', 'Cliente'),
    )
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=15, choices=ROLES, default='cliente')
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"