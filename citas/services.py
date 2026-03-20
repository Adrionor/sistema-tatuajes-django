import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Necesitaremos un archivo de credenciales de Google (te explicaré esto en el siguiente paso)
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
SERVICE_ACCOUNT_FILE = 'credentials.json' 

def crear_evento_google_calendar(cita):
    try:
        # Autenticación con Google
        creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)

        # Formatear las fechas para Google (formato ISO 8601)
        # Aseguramos que tengan el formato correcto de string
        inicio = cita.fecha_hora_inicio.isoformat()
        fin = cita.fecha_hora_fin.isoformat()

        # Crear el cuerpo del evento
        evento = {
            'summary': f'Cita de Tatuaje: {cita.cotizacion.estilo}',
            'description': f'Tatuaje en {cita.cotizacion.zona_cuerpo} (Tamaño: {cita.cotizacion.tamano}).',
            'start': {
                'dateTime': inicio,
                'timeZone': 'America/Mexico_City', # Puedes cambiar la zona horaria si lo necesitas
            },
            'end': {
                'dateTime': fin,
                'timeZone': 'America/Mexico_City',
            },
            # Agregamos al tatuador y al cliente como invitados para que se vincule a sus calendarios
            'attendees': [
                {'email': cita.tatuador.email},
                {'email': cita.cliente.email},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60}, # Recordatorio 1 día antes
                    {'method': 'popup', 'minutes': 60},      # Notificación 1 hora antes
                ],
            },
        }

        # Insertar el evento en el calendario y enviar actualizaciones (correos) a los invitados
        # Usamos un ID de calendario genérico por ahora, luego lo configuraremos
        evento_creado = service.events().insert(
            calendarId='primary', 
            body=evento, 
            sendUpdates='all' # Esto hace que Google les mande el correo de invitación
        ).execute()

        # Devolvemos el ID del evento de Google por si queremos cancelarlo o modificarlo después
        return evento_creado.get('id')
        
    except Exception as e:
        print(f"Error al conectar con Google Calendar: {e}")
        return None