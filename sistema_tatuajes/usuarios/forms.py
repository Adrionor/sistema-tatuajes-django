from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil, ConfiguracionEstudio, Anuncio


# ─── Crear tatuador ──────────────────────────────────────────────────────────

class CrearTatuadorForm(UserCreationForm):
    first_name   = forms.CharField(label='Nombre', max_length=30)
    last_name    = forms.CharField(label='Apellido', max_length=30, required=False)
    email        = forms.EmailField(label='Correo electrónico', required=False)

    class Meta:
        model  = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


class PerfilTatuadorForm(forms.ModelForm):
    """Datos de perfil al crear o editar un tatuador."""
    class Meta:
        model  = Perfil
        fields = ('rol', 'telefono', 'especialidad', 'bio', 'instagram',
                  'foto_perfil', 'es_colaboracion', 'fecha_inicio_colab',
                  'fecha_fin_colab')
        widgets = {
            'bio':               forms.Textarea(attrs={'rows': 3}),
            'fecha_inicio_colab': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_colab':    forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['es_colaboracion'].widget.attrs['class'] = 'form-check-input'
        # Solo permitir propietario/tatuador en este formulario
        self.fields['rol'].choices = [
            ('propietario', 'Propietario'),
            ('tatuador',    'Tatuador'),
        ]


# ─── Editar usuario existente ────────────────────────────────────────────────

class EditarUsuarioForm(forms.ModelForm):
    """Edición de los datos User del admin."""
    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email', 'is_active')
        labels = {
            'is_active': '¿Cuenta activa?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'is_active':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'


# ─── Configuración del estudio ────────────────────────────────────────────────

class ConfiguracionEstudioForm(forms.ModelForm):
    class Meta:
        model  = ConfiguracionEstudio
        fields = ('nombre', 'slogan', 'direccion', 'telefono', 'whatsapp',
                  'instagram', 'facebook', 'email_contacto', 'descripcion',
                  'imagen_hero', 'moneda', 'porcentaje_anticipo',
                  'skin', 'idioma')
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


# ─── Anuncios ─────────────────────────────────────────────────────────────────────────────

class AnuncioForm(forms.ModelForm):
    class Meta:
        model  = Anuncio
        fields = ('titulo', 'tipo', 'descripcion', 'imagen',
                  'tatuador_asociado', 'fecha_evento', 'activo', 'orden')
        widgets = {
            'descripcion':  forms.Textarea(attrs={'rows': 3}),
            'fecha_evento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('activo',):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'
        # Solo artistas para el FK
        self.fields['tatuador_asociado'].queryset = (
            User.objects
            .filter(perfil__rol__in=('tatuador', 'propietario'), is_active=True)
            .order_by('first_name')
        )
        self.fields['tatuador_asociado'].empty_label = '— Sin artista asociado —'
