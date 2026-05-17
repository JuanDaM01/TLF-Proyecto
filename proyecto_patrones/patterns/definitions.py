# =============================================================================
# patterns/definitions.py
# Definición de todos los patrones del dominio con su expresión regular,
# descripción y ejemplos válidos/inválidos.
#
# IMPORTANTE: Todas las expresiones regulares están escritas para el motor
# propio (RegexEngine), no para la librería 're' de Python.
# =============================================================================

# Cada patrón es un diccionario con:
#   name        : Nombre legible del patrón
#   pattern     : Expresión regular para el motor propio
#   description : Descripción técnica de lo que detecta
#   valid_ex    : Lista de ejemplos válidos (para documentación y pruebas)
#   invalid_ex  : Lista de ejemplos inválidos


PATTERNS = {

    # -------------------------------------------------------------------------
    # CORREO ELECTRÓNICO
    # Formato: usuario@dominio.tld
    # Reglas:
    #   - Usuario: letras, dígitos, puntos, guiones, +, _
    #   - Dominio: letras, dígitos, guiones, puntos
    #   - TLD: 2 a 6 letras (com, org, edu, co, info, museum)
    # -------------------------------------------------------------------------
    'email': {
        'name': 'Correo Electrónico',
        'pattern': (
            r'[a-zA-Z0-9._+\-]+'       # usuario
            r'@'                        # arroba
            r'[a-zA-Z0-9.\-]+'         # dominio
            r'\.'                       # punto obligatorio antes del TLD
            r'[a-zA-Z][a-zA-Z][a-zA-Z]?[a-zA-Z]?[a-zA-Z]?[a-zA-Z]?'  # TLD 2-6 letras
        ),
        'description': 'Dirección de correo electrónico estándar (RFC 5322 simplificado)',
        'valid_ex':   ['usuario@ejemplo.com', 'nombre.apellido@empresa.co',
                       'contacto+info@dominio.org', 'admin@sub.dominio.edu'],
        'invalid_ex': ['@sinusuario.com', 'sin_arroba.com',
                       'usuario@', 'usuario@dominio'],
    },

    # -------------------------------------------------------------------------
    # NÚMERO TELEFÓNICO COLOMBIANO
    # Formatos soportados:
    #   - Fijo Bogotá:  601-XXXXXXX  (7 dígitos)
    #   - Fijo otro:    60X-XXXXXXX
    #   - Celular:      3XX XXXXXXX o 3XXXXXXXXX (10 dígitos, inicia en 3)
    #   - Con prefijo:  +57 3XX... o 57 3XX...
    # -------------------------------------------------------------------------
    'telefono_co': {
        'name': 'Teléfono Colombiano',
        'pattern': (
            r'(\+57|57)?'              # prefijo internacional opcional
            r'[ \-]?'                  # separador opcional
            r'(3[0-9][0-9]'           # celular: 3XX
            r'[ \-]?[0-9][0-9][0-9]'  # XXX
            r'[ \-]?[0-9][0-9][0-9][0-9]'  # XXXX
            r'|60[0-9]'               # o: indicativo fijo (601 o 60X)
            r'[ \-]?[0-9][0-9][0-9][0-9][0-9][0-9][0-9])'  # XXXXXXX
        ),
        'description': 'Número telefónico colombiano (celular o fijo con/sin prefijo +57)',
        'valid_ex':   ['3001234567', '300 123 4567', '+57 310 555 9999',
                       '601-5551234', '57 3201234567'],
        'invalid_ex': ['123456', '12345678901', '200-1234567'],
    },

    # -------------------------------------------------------------------------
    # FECHAS
    # Formatos soportados:
    #   DD/MM/AAAA, DD-MM-AAAA, DD.MM.AAAA
    #   AAAA/MM/DD, AAAA-MM-DD
    #   DD de MES de AAAA (texto)
    # -------------------------------------------------------------------------
    'fecha': {
        'name': 'Fecha',
        'pattern': (
            r'([0-2][0-9]|3[01])'      # día: 01-31
            r'[/\-\.]'                  # separador
            r'(0[1-9]|1[0-2])'         # mes: 01-12
            r'[/\-\.]'                  # separador
            r'(19|20)[0-9][0-9]'       # año: 1900-2099
        ),
        'description': 'Fecha en formato DD/MM/AAAA, DD-MM-AAAA o DD.MM.AAAA',
        'valid_ex':   ['15/06/2023', '01-12-1999', '31.01.2000', '29/02/2000'],
        'invalid_ex': ['32/01/2023', '00/13/2023', '15-6-23'],
    },

    # -------------------------------------------------------------------------
    # FECHAS ISO 8601
    # Formato: AAAA-MM-DD
    # -------------------------------------------------------------------------
    'fecha_iso': {
        'name': 'Fecha ISO 8601',
        'pattern': (
            r'(19|20)[0-9][0-9]'       # año
            r'\-'
            r'(0[1-9]|1[0-2])'         # mes
            r'\-'
            r'([0-2][0-9]|3[01])'      # día
        ),
        'description': 'Fecha en formato estándar ISO 8601: AAAA-MM-DD',
        'valid_ex':   ['2023-06-15', '1999-12-31', '2000-01-01'],
        'invalid_ex': ['23-06-15', '2023-13-01', '2023-00-10'],
    },

    # -------------------------------------------------------------------------
    # DIRECCIÓN URL
    # Esquemas: http, https, ftp
    # -------------------------------------------------------------------------
    'url': {
        'name': 'URL / Dirección Web',
        'pattern': (
            r'(https?|ftp)'             # esquema
            r'://'                      # separador
            r'([a-zA-Z0-9\-]+\.)*'     # subdominios opcionales
            r'[a-zA-Z0-9\-]+'          # dominio principal
            r'\.[a-zA-Z][a-zA-Z][a-zA-Z]?[a-zA-Z]?[a-zA-Z]?[a-zA-Z]?'  # TLD
            r'(/[a-zA-Z0-9._/\-?=&#%]*)?'  # ruta y query opcionales
        ),
        'description': 'URL completa con esquema http, https o ftp',
        'valid_ex':   ['https://www.google.com', 'http://ejemplo.co/ruta',
                       'https://sub.dominio.org/page?id=1&ref=main',
                       'ftp://archivos.servidor.net'],
        'invalid_ex': ['www.google.com', 'ftp:/dominio.com', '://sin-esquema.com'],
    },

    # -------------------------------------------------------------------------
    # PLACA VEHICULAR COLOMBIANA
    # Formato actual: 3 letras + 3 dígitos  (ABC-123 o ABC123)
    # Formato moto:   3 letras + 2 dígitos + 1 letra  (ABC12D)
    # -------------------------------------------------------------------------
    'placa_co': {
        'name': 'Placa Vehicular Colombiana',
        'pattern': (
            r'[A-Z][A-Z][A-Z]'          # 3 letras mayúsculas
            r'[\-]?'                    # guion opcional
            r'([0-9][0-9][0-9]'        # 3 dígitos (carro)
            r'|[0-9][0-9][A-Z])'       # o 2 dígitos + letra (moto)
        ),
        'description': 'Placa colombiana de vehículo (carro o moto)',
        'valid_ex':   ['ABC123', 'XYZ-456', 'DEF78G', 'AAA-000'],
        'invalid_ex': ['AB123', 'ABCD123', '123ABC', 'abc123'],
    },

    # -------------------------------------------------------------------------
    # CÉDULA DE CIUDADANÍA COLOMBIANA
    # 6 a 10 dígitos (sin puntos ni separadores)
    # -------------------------------------------------------------------------
    'cedula_co': {
        'name': 'Cédula de Ciudadanía',
        'pattern': r'[1-9][0-9][0-9][0-9][0-9][0-9]([0-9][0-9][0-9][0-9])?',
        'description': 'Cédula de ciudadanía colombiana: 6 a 10 dígitos',
        'valid_ex':   ['123456', '1234567890', '987654321'],
        'invalid_ex': ['12345', '12345678901', '01234567'],
    },

    # -------------------------------------------------------------------------
    # CÓDIGO POSTAL COLOMBIANO
    # 6 dígitos exactos
    # -------------------------------------------------------------------------
    'codigo_postal': {
        'name': 'Código Postal',
        'pattern': r'[0-9][0-9][0-9][0-9][0-9][0-9]',
        'description': 'Código postal colombiano: exactamente 6 dígitos',
        'valid_ex':   ['110111', '050001', '760020'],
        'invalid_ex': ['11011', '1100111', 'AB1234'],
    },

    # -------------------------------------------------------------------------
    # DIRECCIÓN IP v4
    # Formato: 0-255 . 0-255 . 0-255 . 0-255
    # -------------------------------------------------------------------------
    'ipv4': {
        'name': 'Dirección IPv4',
        'pattern': (
            r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])'
            r'\.'
            r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])'
            r'\.'
            r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])'
            r'\.'
            r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])'
        ),
        'description': 'Dirección de red IPv4 (0.0.0.0 a 255.255.255.255)',
        'valid_ex':   ['192.168.1.1', '10.0.0.1', '255.255.255.0', '0.0.0.0'],
        'invalid_ex': ['256.1.1.1', '192.168.1', '192.168.1.1.1'],
    },

    # -------------------------------------------------------------------------
    # HORA
    # Formatos: HH:MM  HH:MM:SS  con AM/PM opcional
    # -------------------------------------------------------------------------
    'hora': {
        'name': 'Hora',
        'pattern': (
            r'(2[0-3]|[01]?[0-9])'    # hora: 0-23
            r':'
            r'[0-5][0-9]'             # minutos: 00-59
            r'(:[0-5][0-9])?'         # segundos opcionales
            r'( ?(AM|PM|am|pm))?'     # AM/PM opcional
        ),
        'description': 'Hora en formato HH:MM o HH:MM:SS con AM/PM opcional',
        'valid_ex':   ['08:30', '23:59:59', '12:00 PM', '00:00:01'],
        'invalid_ex': ['25:00', '08:60', '12:61:00'],
    },

    # -------------------------------------------------------------------------
    # HASHTAG (Redes Sociales)
    # -------------------------------------------------------------------------
    'hashtag': {
        'name': 'Hashtag',
        'pattern': r'#[a-zA-Z][a-zA-Z0-9_]+',
        'description': 'Hashtag de redes sociales: # seguido de letras y dígitos',
        'valid_ex':   ['#Python', '#IA2024', '#hola_mundo'],
        'invalid_ex': ['#', '#123inicio', '# con espacio'],
    },

    # -------------------------------------------------------------------------
    # TARJETA DE CRÉDITO (formato genérico 16 dígitos)
    # Grupos: XXXX-XXXX-XXXX-XXXX o XXXXXXXXXXXXXXXX
    # -------------------------------------------------------------------------
    'tarjeta_credito': {
        'name': 'Número de Tarjeta de Crédito',
        'pattern': (
            r'[0-9][0-9][0-9][0-9]'
            r'[\- ]?'
            r'[0-9][0-9][0-9][0-9]'
            r'[\- ]?'
            r'[0-9][0-9][0-9][0-9]'
            r'[\- ]?'
            r'[0-9][0-9][0-9][0-9]'
        ),
        'description': 'Número de tarjeta de crédito: 16 dígitos en grupos de 4',
        'valid_ex':   ['4111111111111111', '4111-1111-1111-1111', '4111 1111 1111 1111'],
        'invalid_ex': ['411111111111111', '4111-111-1111-1111', 'abcd1234efgh5678'],
    },
}