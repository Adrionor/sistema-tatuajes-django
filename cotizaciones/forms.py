from django import forms
from .models import Cotizacion
from django.contrib.auth.models import User

class CotizacionForm(forms.ModelForm):
    tatuador = forms.ModelChoiceField(
        queryset=User.objects.filter(perfil__rol='tatuador'),
        empty_label="Escoge a tu tatuador favorito"
    )

    class Meta:
        model = Cotizacion
        # Añadimos los datos personales y la fecha solicitada
        fields = ['nombre_cliente', 'email_cliente', 'telefono_cliente', 'tatuador', 'fecha_solicitada', 'estilo', 'zona_cuerpo', 'tamano', 'imagen_referencia']
        
        # Esto le dice a Django que muestre un calendario bonito en el navegador para elegir fecha y hora
        widgets = {
            'fecha_solicitada': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ComprobanteForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['comprobante_anticipo']