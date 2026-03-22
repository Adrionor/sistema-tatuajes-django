import os
import re
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


def _seo_upload_path(instance, filename):
    """
    Genera un nombre de archivo SEO-friendly en el momento de la subida.
    Formato: <estudio>-<artista>-<estilo>-<titulo>.<ext>
    Ejemplo: ink-studio-juan-realismo-manga-floral.jpg
    """
    ext = os.path.splitext(filename)[1].lower() or '.jpg'

    # Nombre del estudio
    try:
        from usuarios.models import ConfiguracionEstudio
        studio_slug = slugify(ConfiguracionEstudio.get_config().nombre)[:20]
    except Exception:
        studio_slug = 'estudio'

    # Nombre del artista
    artist_name = (instance.tatuador.get_full_name() or instance.tatuador.username)
    artist_slug = slugify(artist_name)[:15]

    # Estilo
    style_slug = slugify(instance.estilo or 'tatuaje')[:20]

    # Título o descripción (lo más descriptivo disponible)
    detail = instance.titulo or (instance.descripcion or '')[:60]
    detail_slug = slugify(detail)[:30] if detail else 'tatuaje'

    seo_name = f"{studio_slug}-{artist_slug}-{style_slug}-{detail_slug}{ext}"
    # Eliminar guiones dobles que puedan quedar
    seo_name = re.sub(r'-{2,}', '-', seo_name).strip('-')
    return f"portafolio/{seo_name}"


class Trabajo(models.Model):
    tatuador     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trabajos_portafolio')
    imagen       = models.ImageField(upload_to=_seo_upload_path)
    titulo       = models.CharField(max_length=100, blank=True, help_text='Título opcional (ej: "Manga floral")')
    descripcion  = models.TextField(blank=True, null=True)
    estilo       = models.CharField(max_length=50)
    alt_text     = models.CharField(
        max_length=200, blank=True,
        help_text='Texto alternativo SEO de la imagen. Se genera automáticamente si se deja vacío.',
        verbose_name='Alt text (SEO)',
    )
    fecha_subida = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"Trabajo de {self.tatuador.username} - {self.estilo}"

    # ── Generación automática de alt_text ────────────────────────────────────
    def generar_alt_text(self):
        """Construye un alt text descriptivo y rico en keywords para SEO."""
        try:
            from usuarios.models import ConfiguracionEstudio
            studio = ConfiguracionEstudio.get_config().nombre
        except Exception:
            studio = 'el estudio'

        artist = self.tatuador.get_full_name() or self.tatuador.username
        parts = [f"Tatuaje de {self.estilo}", f"por {artist}", f"en {studio}"]

        if self.titulo:
            parts.append(f"— {self.titulo}")
        elif self.descripcion:
            snippet = self.descripcion[:80].rstrip()
            parts.append(f"— {snippet}")

        return ' '.join(parts)

    def save(self, *args, **kwargs):
        # Auto-generar alt_text la primera vez o si está vacío
        if not self.alt_text:
            self.alt_text = self.generar_alt_text()
        super().save(*args, **kwargs)