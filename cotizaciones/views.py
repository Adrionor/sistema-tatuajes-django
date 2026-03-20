from django.shortcuts import render, redirect, get_object_or_404
from .models import Cotizacion
from .forms import CotizacionForm, ComprobanteForm
from . import emails

def solicitar_cotizacion(request):
    if request.method == 'POST':
        form = CotizacionForm(request.POST, request.FILES)
        if form.is_valid():
            # Como ya no hay que asignarle un "Usuario" al cliente, simplemente guardamos el formulario
            cotizacion = form.save() 
            emails.correo_cotizacion_pedida(cotizacion)
            return redirect('galeria') 
    else:
        form = CotizacionForm()
    return render(request, 'cotizaciones/formulario.html', {'form': form})

def recepcion_tatuador(request):
    cotizaciones_pendientes = Cotizacion.objects.filter(estado__in=['pendiente', 'pagada'])
    return render(request, 'cotizaciones/recepcion.html', {'cotizaciones': cotizaciones_pendientes})

def aceptar_cotizacion(request, cotizacion_id):
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
    if request.method == 'POST':
        cotizacion.monto_total = request.POST.get('monto_total')
        cotizacion.monto_anticipo = request.POST.get('monto_anticipo')
        cotizacion.estado = 'aceptada' 
        cotizacion.save()
        
        # Envia el correo con el Magic Link
        emails.correo_cotizacion_aceptada(cotizacion)
        return redirect('recepcion_tatuador')
    return render(request, 'cotizaciones/aceptar.html', {'cotizacion': cotizacion})

# ¡NUEVA VISTA DEL MAGIC LINK!
def estado_magico_cliente(request, token):
    # Busca la cotización usando el UUID único. Si alguien inventa un token, dará error 404 (No encontrado)
    cotizacion = get_object_or_404(Cotizacion, token_acceso=token)
    
    if request.method == 'POST':
        form = ComprobanteForm(request.POST, request.FILES, instance=cotizacion)
        if form.is_valid():
            cotizacion = form.save(commit=False)
            cotizacion.estado = 'pagada' 
            cotizacion.save()
            emails.correo_comprobante_subido(cotizacion)
            return redirect('galeria') # Lo regresamos a la galería tras pagar
    else:
        form = ComprobanteForm(instance=cotizacion)
        
    return render(request, 'cotizaciones/estado_magico.html', {'form': form, 'cotizacion': cotizacion})