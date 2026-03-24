from django import forms
from .models import Cotizacion
from django.contrib.auth.models import User


class CotizacionForm(forms.ModelForm):
    """
    Formulario de solicitud de cotización para el cliente.
    Si se pasa `tatuador_inicial` al constructor, el campo tatuador
    se oculta y se pre-llena automáticamente.
    """
    tatuador = forms.ModelChoiceField(
        queryset=User.objects.none(),
        empty_label="Escoge a tu artista favorito",
    )

    # Declarado explícitamente para forzar el formato YYYY-MM-DD
    # (el input nativo HTML5 siempre envía ese formato, pero el locale 'es'
    # espera DD/MM/YYYY, lo que provoca que la validación rechace el valor)
    fecha_solicitada = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
        label='Fecha preferida',
    )

    notas_cliente = forms.CharField(
        label='Cuéntanos tu idea',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Describe tu idea libremente: colores, referencias, significado, tamaño, zona exacta, cualquier detalle que quieras que tu artista sepa…',
        }),
    )

    class Meta:
        model  = Cotizacion
        fields = [
            'nombre_cliente', 'email_cliente', 'telefono_cliente',
            'tatuador', 'fecha_solicitada',
            'estilo', 'zona_cuerpo', 'tamano',
            'notas_cliente',
        ]

    def __init__(self, *args, tatuador_inicial=None, studio=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar artistas por estudio
        qs = User.objects.filter(perfil__rol__in=['tatuador', 'propietario'], is_active=True)
        if studio:
            qs = qs.filter(perfil__estudio=studio)
        self.fields['tatuador'].queryset = qs.order_by('first_name')
        if tatuador_inicial:
            self.fields['tatuador'].initial  = tatuador_inicial
            self.fields['tatuador'].widget   = forms.HiddenInput()
            self.fields['tatuador'].required = True
        # Orden y labels amigables
        self.fields['nombre_cliente'].label   = 'Tu nombre completo'
        self.fields['email_cliente'].label    = 'Correo electrónico'
        self.fields['telefono_cliente'].label = 'Teléfono / WhatsApp'
        self.fields['fecha_solicitada'].label = 'Fecha preferida'
        self.fields['estilo'].label           = 'Estilo de tatuaje'
        self.fields['zona_cuerpo'].label      = 'Zona del cuerpo'
        self.fields['tamano'].label           = 'Tamaño aproximado'
        self.fields['notas_cliente'].label      = 'Cuéntanos tu idea'

    def clean_fecha_solicitada(self):
        from django.utils import timezone
        fecha = self.cleaned_data.get('fecha_solicitada')
        if fecha and fecha < timezone.now().date():
            raise forms.ValidationError("No puedes solicitar una fecha pasada.")
        return fecha


class ComprobanteForm(forms.ModelForm):
    class Meta:
        model  = Cotizacion
        fields = ['comprobante_anticipo']
        widgets = {
            'comprobante_anticipo': forms.FileInput(),
        }


class CancelacionForm(forms.Form):
    notas = forms.CharField(
        label='Motivo de cancelación (opcional)',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
