from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    ROLES = (
        ('propietario', 'Propietario'),
        ('tatuador',    'Tatuador'),
        ('cliente',     'Cliente'),
    )
    usuario      = models.OneToOneField(User, on_delete=models.CASCADE)
    rol          = models.CharField(max_length=15, choices=ROLES, default='cliente')
    telefono     = models.CharField(max_length=20, blank=True)
    bio          = models.TextField(blank=True, help_text='Presentación que verán los clientes en tu perfil')
    especialidad = models.CharField(max_length=120, blank=True, help_text='Ej: Realismo, Blackwork, Neo-tradicional')
    instagram    = models.CharField(max_length=60, blank=True, help_text='Solo el @usuario, sin URL')
    foto_perfil  = models.ImageField(upload_to='perfiles/', null=True, blank=True)

    # ── Colaboraciones temporales ────────────────────────────
    es_colaboracion        = models.BooleanField(default=False,
        help_text='Marcar si es un artista invitado / colaboración temporal')
    fecha_inicio_colab     = models.DateField(null=True, blank=True,
        help_text='Inicio de la colaboración (opcional)')
    fecha_fin_colab        = models.DateField(null=True, blank=True,
        help_text='Fin de la colaboración (opcional)')

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"

    @property
    def es_tatuador_activo(self):
        """True si es tatuador o propietario y la cuenta está activa."""
        return self.rol in ('tatuador', 'propietario') and self.usuario.is_active


# ─── Configuración global del estudio ────────────────────────────────────────

class ConfiguracionEstudio(models.Model):
    nombre          = models.CharField(max_length=120, default='Mi Estudio de Tatuajes')
    slogan          = models.CharField(max_length=200, blank=True)
    direccion       = models.CharField(max_length=250, blank=True)
    telefono        = models.CharField(max_length=20, blank=True)
    whatsapp        = models.CharField(max_length=20, blank=True,
        help_text='Número completo con código de país, sin espacios ni +')
    instagram       = models.CharField(max_length=60, blank=True, help_text='Solo el @usuario')
    facebook        = models.CharField(max_length=120, blank=True, help_text='URL completa o solo el usuario')
    email_contacto  = models.EmailField(blank=True)
    descripcion     = models.TextField(blank=True, help_text='Descripción breve para la página de inicio')
    moneda          = models.CharField(max_length=10, default='MXN')
    porcentaje_anticipo = models.PositiveSmallIntegerField(default=30,
        help_text='% de anticipo requerido para confirmar cita')

    class Meta:
        verbose_name = 'Configuración del Estudio'

    def __str__(self):
        return self.nombre

    @classmethod
    def get_config(cls):
        """Devuelve siempre el único registro de configuración (lo crea si no existe)."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Notificacion(models.Model):
    """
    Notificación interna del sistema para usuarios con cuenta (tatuadores).
    Los clientes reciben sus notificaciones exclusivamente por correo.
    """
    usuario    = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='notificaciones')
    mensaje    = models.TextField()
    url        = models.CharField(max_length=300, blank=True)
    leida      = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{'✓' if self.leida else '●'}] {self.usuario.username}: {self.mensaje[:60]}"
