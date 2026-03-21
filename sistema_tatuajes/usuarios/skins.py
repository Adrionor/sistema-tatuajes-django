"""
Definición de los skins (temas visuales) disponibles para cada estudio.
Cada skin es un diccionario de variables CSS y fuentes de Google Fonts.
El panel del propietario permite elegir el skin activo.
"""

SKINS = {

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # NOIR — tema oscuro dorado (el diseño original)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    'noir': {
        'label':       'Noir — Oro y Negro',
        'description': 'Elegancia oscura con acentos dorados. El clásico del tatuaje.',
        'preview_bg':  '#0d0d0d',
        'preview_accent': '#c9a84c',
        'fonts_url': (
            'https://fonts.googleapis.com/css2?'
            'family=Bebas+Neue&family=Raleway:wght@300;400;500;600;700&display=swap'
        ),
        'vars': {
            '--bg':           '#0d0d0d',
            '--bg-card':      '#181818',
            '--bg-muted':     '#222222',
            '--border':       '#2e2e2e',
            '--text':         '#e8e8e8',
            '--text-muted':   '#999999',
            '--gold':         '#c9a84c',
            '--gold-dim':     '#a0823a',
            '--red':          '#e63030',
            '--green':        '#2ecc71',
            '--font-head':    "'Bebas Neue', sans-serif",
            '--font-body':    "'Raleway', sans-serif",
        },
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CRIMSON — rojo sangre y negro. Intenso, agresivo.
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    'crimson': {
        'label':       'Crimson — Rojo y Negro',
        'description': 'Energía de tinta roja. Para estudios con personalidad fuerte.',
        'preview_bg':  '#0e0808',
        'preview_accent': '#c0392b',
        'fonts_url': (
            'https://fonts.googleapis.com/css2?'
            'family=Anton&family=Inter:wght@300;400;500;600;700&display=swap'
        ),
        'vars': {
            '--bg':           '#0e0808',
            '--bg-card':      '#1a0f0f',
            '--bg-muted':     '#251515',
            '--border':       '#3d1c1c',
            '--text':         '#f0e0e0',
            '--text-muted':   '#9e7070',
            '--gold':         '#c0392b',
            '--gold-dim':     '#922b21',
            '--red':          '#ff4444',
            '--green':        '#2ecc71',
            '--font-head':    "'Anton', sans-serif",
            '--font-body':    "'Inter', sans-serif",
        },
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FROST — blanco y plata. Limpio, moderno, minimalista.
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    'frost': {
        'label':       'Frost — Blanco Minimalista',
        'description': 'Limpio y sofisticado. Perfecto para estudios de fine-line.',
        'preview_bg':  '#f7f7f7',
        'preview_accent': '#1a1a1a',
        'fonts_url': (
            'https://fonts.googleapis.com/css2?'
            'family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap'
        ),
        'vars': {
            '--bg':           '#f7f7f7',
            '--bg-card':      '#ffffff',
            '--bg-muted':     '#eeeeee',
            '--border':       '#d0d0d0',
            '--text':         '#1a1a1a',
            '--text-muted':   '#666666',
            '--gold':         '#1a1a1a',
            '--gold-dim':     '#444444',
            '--red':          '#c0392b',
            '--green':        '#27ae60',
            '--font-head':    "'Playfair Display', serif",
            '--font-body':    "'DM Sans', sans-serif",
            '--navbar-bg':    '#ffffff',
        },
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AMETHYST — morado y negro. Místico, mágico, neo-tradicional.
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    'amethyst': {
        'label':       'Amethyst — Morado y Negro',
        'description': 'Vibraciones místicas. Ideal para tatuajes neo-tradicionales y darkwork.',
        'preview_bg':  '#0b0810',
        'preview_accent': '#9b59b6',
        'fonts_url': (
            'https://fonts.googleapis.com/css2?'
            'family=Cinzel:wght@700;900&family=Nunito:wght@300;400;500;600;700&display=swap'
        ),
        'vars': {
            '--bg':           '#0b0810',
            '--bg-card':      '#130f1c',
            '--bg-muted':     '#1c1630',
            '--border':       '#2d2050',
            '--text':         '#e8e0f0',
            '--text-muted':   '#8870aa',
            '--gold':         '#9b59b6',
            '--gold-dim':     '#7d3c98',
            '--red':          '#e74c3c',
            '--green':        '#2ecc71',
            '--font-head':    "'Cinzel', serif",
            '--font-body':    "'Nunito', sans-serif",
        },
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # OBSIDIAN — verde neón y negro. Cyberpunk / neo-ink.
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    'obsidian': {
        'label':       'Obsidian — Verde Neón',
        'description': 'Cyberpunk industrial. Para los estudios más audaces y modernos.',
        'preview_bg':  '#060c08',
        'preview_accent': '#00e676',
        'fonts_url': (
            'https://fonts.googleapis.com/css2?'
            'family=Orbitron:wght@700;900&family=Share+Tech+Mono&display=swap'
        ),
        'vars': {
            '--bg':           '#060c08',
            '--bg-card':      '#0d1a10',
            '--bg-muted':     '#142218',
            '--border':       '#1a3a20',
            '--text':         '#ccffcc',
            '--text-muted':   '#558855',
            '--gold':         '#00e676',
            '--gold-dim':     '#00c853',
            '--red':          '#ff1744',
            '--green':        '#00e676',
            '--font-head':    "'Orbitron', sans-serif",
            '--font-body':    "'Share Tech Mono', monospace",
        },
    },
}


def get_skin(skin_key):
    """Devuelve el skin por su clave, con fallback a 'noir'."""
    return SKINS.get(skin_key, SKINS['noir'])


def skin_choices():
    """Opciones para el campo choices de Django."""
    return [(key, skin['label']) for key, skin in SKINS.items()]


def render_skin_css(skin_key):
    """Genera el bloque CSS de variables para inyectar en base.html."""
    skin = get_skin(skin_key)
    lines = [':root {']
    for prop, value in skin['vars'].items():
        lines.append(f'    {prop}: {value};')
    # Forzar la fuente del body en el elemento html
    lines.append('}')
    return '\n'.join(lines)
