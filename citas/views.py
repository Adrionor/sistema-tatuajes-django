from django.shortcuts import render, redirect
from cotizaciones.models import Cotizacion
from .models import Cita
from cotizaciones import emails
from . import services
from django.http import JsonResponse
from .models import Cita

def confirmar_y_agendar(request, cotizacion_id):
    # Traemos la cotización que ya fue pagada
    cotizacion = Cotizacion.objects.get(id=cotizacion_id)
    
    if request.method == 'POST':
        # Obtenemos la fecha y hora que el tatuador elija en el formulario HTML
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        
# 1. Creamos la Cita oficial en la base de datos local
        nueva_cita = Cita.objects.create(
            cotizacion=cotizacion,
            tatuador=cotizacion.tatuador,
            cliente=cotizacion.cliente,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin
        )
        
        # 2. Enviamos el correo local (el que hicimos en el paso anterior)
        emails.correo_cita_agendada(nueva_cita)
        
        # 3. ¡NUEVO! Conectamos con Google Calendar
        # Nota: Asegúrate de que los usuarios (tatuador y cliente) tengan un email registrado en tu base de datos
        google_id = services.crear_evento_google_calendar(nueva_cita)
        
        if google_id:
            nueva_cita.google_calendar_id = google_id
            nueva_cita.save()
            
        return redirect('recepcion_tatuador')
    
        
    return render(request, 'citas/agendar.html', {'cotizacion': cotizacion})

# Función que devuelve las fechas ocupadas de un tatuador en formato JSON
def obtener_fechas_ocupadas(request, tatuador_id):
    # Buscamos todas las citas confirmadas de ese tatuador
    citas = Cita.objects.filter(tatuador_id=tatuador_id)
    
    fechas_bloqueadas = []
    for cita in citas:
        # Extraemos solo la fecha (sin la hora) para bloquear el día completo en el calendario
        # Si prefieres bloquear por horas es más complejo, bloquearemos el día por ahora para simplificar
        fecha_texto = cita.fecha_hora_inicio.strftime('%Y-%m-%d')
        fechas_bloqueadas.append(fecha_texto)
        
    return JsonResponse(fechas_bloqueadas, safe=False)