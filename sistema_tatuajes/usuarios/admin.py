from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name = 'Perfil (Rol)'
    fields = ('rol', 'telefono')


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'first_name', 'last_name', 'email', 'rol_display', 'is_staff')

    def rol_display(self, obj):
        try:
            return obj.perfil.get_rol_display()
        except Perfil.DoesNotExist:
            return '—'
    rol_display.short_description = 'Rol'


# Re-registrar User con el nuevo admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
