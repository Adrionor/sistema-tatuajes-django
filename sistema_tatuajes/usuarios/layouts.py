# usuarios/layouts.py
# Metadata for the 5 client-facing layout templates.
# Each entry provides display info for the panel selector.

LAYOUTS = {
    'clasico': {
        'label':       'Clásico',
        'description': 'Hero centrado, cuadrícula de tarjetas con fotos',
        # preview_* are used to render a tiny visual preview in the panel
        'preview': [
            {'w': '100%', 'h': '28px', 'bg': '#111', 'br': '4px 4px 0 0'},  # hero bar
            {'w': '48%',  'h': '18px', 'bg': '#222', 'br': '3px'},
            {'w': '48%',  'h': '18px', 'bg': '#222', 'br': '3px'},
            {'w': '48%',  'h': '18px', 'bg': '#222', 'br': '3px'},
            {'w': '48%',  'h': '18px', 'bg': '#222', 'br': '3px'},
        ],
        'icon': '⊞',
    },
    'revista': {
        'label':       'Revista',
        'description': 'Editorial dividido, filas horizontales, tipografía prominente',
        'preview': [
            {'w': '55%', 'h': '50px', 'bg': '#111', 'br': '3px'},
            {'w': '42%', 'h': '50px', 'bg': '#1a1a1a', 'br': '3px'},
            {'w': '100%', 'h': '14px', 'bg': '#222', 'br': '2px'},
            {'w': '100%', 'h': '14px', 'bg': '#1a1a1a', 'br': '2px'},
        ],
        'icon': '📰',
    },
    'minimal': {
        'label':       'Minimal',
        'description': 'Solo tipografía, sin distracciones visuales',
        'preview': [
            {'w': '70%', 'h': '18px', 'bg': '#333', 'br': '2px'},
            {'w': '45%', 'h': '10px', 'bg': '#222', 'br': '2px'},
            {'w': '100%', 'h': '1px',  'bg': '#2a2a2a', 'br': '0'},
            {'w': '80%', 'h': '10px', 'bg': '#1e1e1e', 'br': '2px'},
            {'w': '65%', 'h': '10px', 'bg': '#1e1e1e', 'br': '2px'},
        ],
        'icon': '○',
    },
    'impacto': {
        'label':       'Impacto',
        'description': 'Pantalla completa, visual cinematográfico, sin bordes',
        'preview': [
            {'w': '100%', 'h': '44px', 'bg': 'linear-gradient(135deg,#0a0a0a,#1a0f00)', 'br': '3px 3px 0 0'},
            {'w': '100%', 'h': '16px', 'bg': '#0d0d0d', 'br': '0'},
            {'w': '100%', 'h': '16px', 'bg': '#111', 'br': '0 0 3px 3px'},
        ],
        'icon': '▓',
    },
    'mosaico': {
        'label':       'Mosaico',
        'description': 'Collage de imágenes al estilo Pinterest',
        'preview': [
            {'w': '32%', 'h': '28px', 'bg': '#1a1a1a', 'br': '2px'},
            {'w': '32%', 'h': '28px', 'bg': '#222',    'br': '2px'},
            {'w': '32%', 'h': '28px', 'bg': '#141414', 'br': '2px'},
            {'w': '32%', 'h': '20px', 'bg': '#222',    'br': '2px'},
            {'w': '32%', 'h': '20px', 'bg': '#1a1a1a', 'br': '2px'},
            {'w': '32%', 'h': '20px', 'bg': '#111',    'br': '2px'},
        ],
        'icon': '⊟',
    },
}

LAYOUT_CHOICES = [(k, v['label']) for k, v in LAYOUTS.items()]
