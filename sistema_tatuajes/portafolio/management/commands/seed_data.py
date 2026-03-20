"""
Comando de Django para poblar la base de datos con datos de demostración.
Uso: python manage.py seed_data
"""
import io
import os
import random
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from usuarios.models import Perfil
from portafolio.models import Trabajo
from cotizaciones.models import Cotizacion
from citas.models import Cita


ESTILOS = ['Realismo', 'Americano Tradicional', 'Neo Tradicional', 'Japonés', 'Blackwork', 'Acuarela', 'Minimalista']

PALETTES = [
    [(15, 15, 15), (201, 168, 76)],   # negro/dorado
    [(20, 10, 30), (180, 60, 200)],   # morado oscuro
    [(10, 25, 15), (46, 180, 90)],    # verde oscuro
    [(25, 10, 10), (220, 60, 60)],    # rojo oscuro
    [(10, 20, 30), (60, 130, 220)],   # azul oscuro
]


def _make_demo_image(label: str, size=(800, 800)) -> bytes:
    """Genera una imagen de placeholder con el nombre del estilo."""
    palette = random.choice(PALETTES)
    bg_color, accent_color = palette

    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)

    # Patrón de líneas de fondo
    for i in range(0, size[0], 40):
        draw.line([(i, 0), (0, i)], fill=tuple(max(0, c - 8) for c in bg_color), width=1)

    # Rectángulo de acento
    margin = 60
    draw.rectangle([margin, margin, size[0] - margin, size[1] - margin],
                   outline=accent_color, width=3)

    # Símbolo central
    cx, cy = size[0] // 2, size[1] // 2
    r = 80
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=accent_color, width=3)
    draw.line([cx - r + 20, cy, cx + r - 20, cy], fill=accent_color, width=2)
    draw.line([cx, cy - r + 20, cx, cy + r - 20], fill=accent_color, width=2)

    # Texto con el estilo (texto grande)
    try:
        font = ImageFont.truetype("arial.ttf", 48)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        font = ImageFont.load_default()
        font_small = font

    # Sombra del texto
    text = label.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx, ty = (size[0] - tw) // 2, size[1] - margin - th - 20

    draw.text((tx + 2, ty + 2), text, fill=(0, 0, 0), font=font)
    draw.text((tx, ty), text, fill=accent_color, font=font)

    # Subtexto "DEMO"
    demo_text = "DEMO — INK STUDIO"
    dbbox = draw.textbbox((0, 0), demo_text, font=font_small)
    dw = dbbox[2] - dbbox[0]
    draw.text(((size[0] - dw) // 2, margin + 20), demo_text,
              fill=tuple(min(255, c + 40) for c in accent_color), font=font_small)

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return buf.getvalue()


TATUADORES = [
    {
        'username': 'carlos_ink',
        'first_name': 'Carlos',
        'last_name': 'Mendoza',
        'email': 'carlos@inkstudio.com',
        'password': 'tatuador123',
        'trabajos': [
            ('Realismo', 'Retrato hiperrealista en escala de grises. Sesión de 6 horas.'),
            ('Realismo', 'Rosa con gotas de agua. Detalle fotográfico en color.'),
            ('Blackwork', 'Mandala geométrico en antebrazo. 4 horas de trabajo.'),
            ('Blackwork', 'Diseño tribal moderno en hombro completo.'),
            ('Americano Tradicional', 'Águila clásica con bandera. Colores sólidos y contornos gruesos.'),
        ]
    },
    {
        'username': 'sofia_art',
        'first_name': 'Sofía',
        'last_name': 'Ramírez',
        'email': 'sofia@inkstudio.com',
        'password': 'tatuadora123',
        'trabajos': [
            ('Acuarela', 'Mariposas en acuarela, colores vibrantes sin contorno.'),
            ('Acuarela', 'Galaxia abstracta en antebrazo. Técnica splash.'),
            ('Neo Tradicional', 'Zorro en estilo neo tradicional con flores japonesas.'),
            ('Minimalista', 'Constelación de Orión ultra fina en costilla.'),
            ('Japonés', 'Carpa koi en armonía con oleaje japonés tradicional.'),
            ('Japonés', 'Oni mask con peonías. Media manga completa.'),
        ]
    },
    {
        'username': 'miguel_dark',
        'first_name': 'Miguel',
        'last_name': 'Torres',
        'email': 'miguel@inkstudio.com',
        'password': 'tatuador123',
        'trabajos': [
            ('Blackwork', 'Sleeve completo en blackwork geométrico. Trabajo de 3 sesiones.'),
            ('Realismo', 'León realista en muslo. Detalle de pelaje en escala de grises.'),
            ('Neo Tradicional', 'Calavera neo tradicional con rosas y serpiente.'),
            ('Americano Tradicional', 'Ancla y marinero clásico. Old school auténtico.'),
        ]
    },
]


class Command(BaseCommand):
    help = 'Puebla la base de datos con tatuadores y trabajos de demostración.'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true',
                            help='Elimina los datos demo anteriores antes de crear nuevos.')

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️  Eliminando datos demo...')
            User.objects.filter(username__in=[t['username'] for t in TATUADORES]).delete()
            self.stdout.write(self.style.WARNING('Datos demo eliminados.'))

        # Crear / verificar superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@inkstudio.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('✔ Superuser creado: admin / admin123'))
        else:
            admin = User.objects.get(username='admin')
            self.stdout.write(self.style.WARNING('ℹ  Superuser "admin" ya existe, se omite.'))

        # Asegurarse de que admin tenga perfil
        Perfil.objects.get_or_create(usuario=admin)

        # Crear tatuadores
        for data in TATUADORES:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name':  data['last_name'],
                    'email':      data['email'],
                }
            )

            if created:
                user.set_password(data['password'])
                user.save()

            # Asignar rol tatuador
            perfil, _ = Perfil.objects.get_or_create(usuario=user)
            perfil.rol = 'tatuador'
            perfil.save()

            # Crear trabajos si el usuario es nuevo o no tiene trabajos
            if created or not user.trabajos_portafolio.exists():
                for estilo, descripcion in data['trabajos']:
                    img_bytes = _make_demo_image(estilo)
                    trabajo = Trabajo(
                        tatuador=user,
                        estilo=estilo,
                        descripcion=descripcion,
                    )
                    filename = f"demo_{user.username}_{estilo.lower().replace(' ', '_')}.jpg"
                    trabajo.imagen.save(filename, ContentFile(img_bytes), save=True)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✔ Tatuador "{user.get_full_name()}" con {len(data["trabajos"])} trabajos.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'ℹ  Tatuador "{user.get_full_name()}" ya existe con trabajos, se omite.'
                    )
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('  ¡Datos de demo cargados exitosamente!'))

        # ── Crear citas de demostración para cada tatuador ──────────────────
        self._seed_citas()

        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('  🌐 Galería:      http://127.0.0.1:8000/portafolio/')
        self.stdout.write('  📝 Cotizar:      http://127.0.0.1:8000/cotizar/')
        self.stdout.write('  🔧 Admin:        http://127.0.0.1:8000/admin/')
        self.stdout.write('  👤 Admin login:  admin / admin123')
        self.stdout.write('')

    def _seed_citas(self):
        """Crea cotizaciones confirmadas + citas de prueba para los próximos meses."""
        CLIENTES_DEMO = [
            {'nombre': 'Ana García',     'email': 'ana@demo.com',     'tel': '5551234567'},
            {'nombre': 'Luis Herrera',   'email': 'luis@demo.com',    'tel': '5559876543'},
            {'nombre': 'María López',    'email': 'maria@demo.com',   'tel': '5555551234'},
            {'nombre': 'Pedro Sánchez',  'email': 'pedro@demo.com',   'tel': '5554443322'},
            {'nombre': 'Valeria Ruiz',   'email': 'vale@demo.com',    'tel': '5557778899'},
            {'nombre': 'Diego Morales',  'email': 'diego@demo.com',   'tel': '5556665544'},
        ]
        ZONAS   = ['Brazo', 'Antebrazo', 'Espalda', 'Pierna', 'Cuello', 'Tobillo']
        TAMANOS = ['Pequeño (5-10cm)', 'Mediano (10-20cm)', 'Grande (20-30cm)']
        hoy = timezone.now()

        # Días de citas para cada tatuador: algunos en los próximos 7 días, otros más adelante
        offsets_por_tatuador = {
            'carlos_ink':  [3, 5, 7, 14, 21, 35],
            'sofia_art':   [2, 8, 15, 25, 40],
            'miguel_dark': [4, 6, 10, 18, 30],
        }

        for data in TATUADORES:
            username = data['username']
            try:
                tatuador = User.objects.get(username=username)
            except User.DoesNotExist:
                continue

            offsets = offsets_por_tatuador.get(username, [5, 12, 20])
            clientes = random.sample(CLIENTES_DEMO, min(len(offsets), len(CLIENTES_DEMO)))

            creadas = 0
            for i, dias in enumerate(offsets):
                cliente = clientes[i % len(clientes)]
                estilo  = random.choice(data['trabajos'])[0]
                zona    = random.choice(ZONAS)
                tamano  = random.choice(TAMANOS)
                hora    = random.choice([10, 11, 12, 14, 15, 16])
                duracion = random.choice([2, 3, 4])

                fecha_inicio = (hoy + timedelta(days=dias)).replace(
                    hour=hora, minute=0, second=0, microsecond=0)
                fecha_fin    = fecha_inicio + timedelta(hours=duracion)

                # Saltar si ya existe una cita ese día/hora para este tatuador
                if Cita.objects.filter(
                    tatuador=tatuador,
                    fecha_hora_inicio__date=fecha_inicio.date(),
                ).exists():
                    continue

                # Crear cotización confirmada
                cotizacion = Cotizacion.objects.create(
                    tatuador          = tatuador,
                    nombre_cliente    = cliente['nombre'],
                    email_cliente     = cliente['email'],
                    telefono_cliente  = cliente['tel'],
                    estilo            = estilo,
                    zona_cuerpo       = zona,
                    tamano            = tamano,
                    fecha_solicitada  = fecha_inicio.date(),
                    monto_total       = random.choice([2500, 3000, 3500, 4000, 5000]),
                    monto_anticipo    = random.choice([500, 800, 1000]),
                    estado            = 'confirmada',
                )

                Cita.objects.create(
                    cotizacion        = cotizacion,
                    tatuador          = tatuador,
                    fecha_hora_inicio = fecha_inicio,
                    fecha_hora_fin    = fecha_fin,
                    estado            = 'programada',
                )
                creadas += 1

            if creadas:
                self.stdout.write(
                    self.style.SUCCESS(f'  📅 {creadas} cita(s) demo para {tatuador.get_full_name()}')
                )

