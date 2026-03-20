from django.contrib import admin
from django.utils.html import format_html
from .models import Cotizacion, Mensaje


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display  = ('nombre_cliente', 'tatuador', 'estilo', 'zona_cuerpo',
                     'fecha_solicitada', 'estado_badge', 'magic_link')
    list_filter   = ('estado', 'tatuador', 'estilo')
    search_fields = ('nombre_cliente', 'email_cliente', 'tatuador__username')
    readonly_fields = ('token_acceso', 'fecha_creacion')
    list_select_related = ('tatuador',)

    def estado_badge(self, obj):
        colors = {
            'pendiente': '#999',
            'aceptada':  '#c9a84c',
            'pagada':    '#2ecc71',
        }
        color = colors.get(obj.estado, '#999')
        return format_html(
            '<span style="background:{};color:#0d0d0d;padding:2px 8px;'
            'border-radius:99px;font-size:11px;font-weight:700;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'

    def magic_link(self, obj):
        url = f'/cotizar/estado/{obj.token_acceso}/'
        return format_html('<a href="{}" target="_blank">Ver enlace cliente</a>', url)
    magic_link.short_description = 'Enlace cliente'


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display   = ('cotizacion', 'autor', 'texto_preview', 'fecha_creacion')
    list_filter    = ('autor',)
    search_fields  = ('cotizacion__nombre_cliente', 'texto')
    readonly_fields = ('fecha_creacion',)

    def texto_preview(self, obj):
        return obj.texto[:80] + '…' if len(obj.texto) > 80 else obj.texto
    texto_preview.short_description = 'Mensaje'
