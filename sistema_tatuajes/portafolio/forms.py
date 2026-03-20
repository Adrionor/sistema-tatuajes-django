from django import forms
from .models import Trabajo
from usuarios.models import Perfil


class TrabajoForm(forms.ModelForm):
    class Meta:
        model  = Trabajo
        fields = ['imagen', 'titulo', 'estilo', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3,
                'placeholder': 'Describe brevemente este trabajo (técnica, tiempo, inspiración...)'}),
            'titulo': forms.TextInput(attrs={'placeholder': 'Ej: Manga floral, Retrato realista...'}),
            'estilo': forms.TextInput(attrs={'placeholder': 'Ej: Realismo, Blackwork, Neo-tradicional...'}),
        }
        labels = {
            'imagen':      'Foto del tatuaje',
            'titulo':      'Título (opcional)',
            'estilo':      'Estilo',
            'descripcion': 'Descripción (opcional)',
        }


class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(label='Nombre', max_length=150, required=False)
    last_name  = forms.CharField(label='Apellido', max_length=150, required=False)
    email      = forms.EmailField(label='Correo electrónico', required=False)

    class Meta:
        model  = Perfil
        fields = ['foto_perfil', 'bio', 'especialidad', 'instagram', 'telefono']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4,
                'placeholder': 'Cuéntale a los clientes quién eres, tu historia, tu filosofía de trabajo...'}),
            'especialidad': forms.TextInput(attrs={
                'placeholder': 'Ej: Realismo en color, Blackwork, Japonés...'}),
            'instagram': forms.TextInput(attrs={'placeholder': '@tu_usuario'}),
            'telefono':  forms.TextInput(attrs={'placeholder': '+52 55 1234 5678'}),
        }
        labels = {
            'foto_perfil':  'Foto de perfil',
            'bio':          'Sobre mí',
            'especialidad': 'Especialidad(es)',
            'instagram':    'Instagram',
            'telefono':     'Teléfono / WhatsApp',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial  = user.last_name
            self.fields['email'].initial      = user.email
        # Put name/email first
        ordered = ['first_name', 'last_name', 'email',
                   'foto_perfil', 'especialidad', 'bio', 'instagram', 'telefono']
        self.fields = {k: self.fields[k] for k in ordered if k in self.fields}
