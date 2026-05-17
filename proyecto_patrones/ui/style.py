# =============================================================================
# ui/style.py
# Estilos centralizados para la interfaz Lumen Academic Analytics
# Basado en la estética Glassmorphism y el Diseño Institucional
# =============================================================================

COLORS = {
    'bg_dark':     '#0b1420',   # Fondo principal (surface)
    'bg_panel':    '#141c29',   # Panel secundario (surface-container-low)
    'bg_input':    '#060e1b',   # Fondo de campos de entrada (surface-container-lowest)
    'accent':      '#00695c',   # Verde institucional (primary)
    'accent_2':    '#56d6a0',   # Éxito / Validación positiva
    'danger':      '#f87171',   # Error / Validación negativa
    'text_main':   '#e6eef8',   # Texto principal (on-surface)
    'text_muted':  '#9fb0c8',   # Texto secundario (on-surface-variant)
    'border':      '#323948',   # Bordes translúcidos (surface-bright)
    'glass_bg':    '#172031',   # Fondo para efecto glass sin transparencia
    'glass_border':'#2a3a52'
}

TYPO = {
    'title':     ('Inter', 18, 'bold'),
    'header':    ('Inter', 14, 'bold'),
    'label':     ('Inter', 10),
    'label_bold':('Inter', 10, 'bold'),
    'mono':      ('JetBrains Mono', 9),
}

SPACING = {
    'pad_small': 8,
    'pad_mid':   16,
    'pad_large': 24,
    'rounding':  12,
}
