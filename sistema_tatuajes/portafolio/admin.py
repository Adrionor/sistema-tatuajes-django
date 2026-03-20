from django.contrib import admin
from django.utils.html import format_html
from .models import Trabajo


@admin.register(Trabajo)
class TrabajoAdmin(admin.ModelAdmin):
    list_display  = ('tatuador', 'estilo', 'thumbnail', 'descripcion_corta')
    list_filter   = ('tatuador', 'estilo')
    search_fields = ('tatuador__username', 'tatuador__first_name', 'estilo')
    list_select_related = ('tatuador',)

    def thumbnail(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="height:60px;border-radius:4px;" />', obj.imagen.url)
        return '—'
    thumbnail.short_description = 'Vista previa'

    def descripcion_corta(self, obj):
        if obj.descripcion:
            return obj.descripcion[:60] + ('...' if len(obj.descripcion) > 60 else '')
        return '—'
    descripcion_corta.short_description = 'Descripción'
