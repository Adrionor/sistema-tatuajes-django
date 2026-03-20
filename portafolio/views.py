from django.shortcuts import render
from .models import Trabajo

def galeria_portafolio(request):
    # Obtenemos todos los trabajos guardados en la base de datos
    trabajos = Trabajo.objects.all()
    
    # Se los enviamos a un archivo HTML llamado 'galeria.html'
    return render(request, 'portafolio/galeria.html', {'trabajos': trabajos})