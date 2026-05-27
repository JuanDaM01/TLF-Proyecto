PATTERNS = {

    'email': {
        'name': 'Correo Electrónico',
        'pattern': (
            r'[a-zA-Z0-9._\-]+'
            r'@'
            r'[a-zA-Z0-9.\-]+'
            r'\.'
            r'[a-zA-Z][a-zA-Z][a-zA-Z]?[a-zA-Z]?[a-zA-Z]?[a-zA-Z]?'
        ),
        'description': 'Dirección de correo electrónico simplificada (no permite + en la parte local)',
        'valid_ex':   ['usuario@ejemplo.com', 'nombre.apellido@empresa.co',
                    'admin@sub.dominio.edu'],
        'invalid_ex': ['@sinusuario.com', 'sin_arroba.com',
                    'usuario@', 'usuario@dominio'],
    },

    'telefono_co': {
        'name': 'Teléfono Colombiano',
        'pattern': (
            r'(\+57|57)?'
            r'[ \-]?'
            r'(3[0-9][0-9]'
            r'[ \-]?[0-9][0-9][0-9]'
            r'[ \-]?[0-9][0-9][0-9][0-9]'
            r'|60[0-9]'
            r'[ \-]?[0-9][0-9][0-9][0-9][0-9][0-9][0-9])'
        ),
        'description': 'Número telefónico colombiano (celular o fijo con/sin prefijo +57)',
        'valid_ex':   ['3001234567', '300 123 4567', '+57 310 555 9999',
                        '601-5551234', '57 3201234567'],
        'invalid_ex': ['123456', '12345678901', '200-1234567'],
    },

    'fecha': {
        'name': 'Fecha',
        'pattern': (
            r'([0-2][0-9]|3[01])'
            r'[/\-\.]'
            r'(0[1-9]|1[0-2])'
            r'[/\-\.]'
            r'(19|20)[0-9][0-9]'
        ),
        'description': 'Fecha en formato DD/MM/AAAA, DD-MM-AAAA o DD.MM.AAAA',
        'valid_ex':   ['15/06/2023', '01-12-1999', '31.01.2000', '29/02/2000'],
        'invalid_ex': ['32/01/2023', '00/13/2023', '15-6-23'],
    },

    'fecha_iso': {
        'name': 'Fecha ISO 8601',
        'pattern': (
            r'(19|20)[0-9][0-9]'
            r'\-'
            r'(0[1-9]|1[0-2])'
            r'\-'
            r'([0-2][0-9]|3[01])'
        ),
        'description': 'Fecha en formato estándar ISO 8601: AAAA-MM-DD',
        'valid_ex':   ['2023-06-15', '1999-12-31', '2000-01-01'],
        'invalid_ex': ['23-06-15', '2023-13-01', '2023-00-10'],
    },

    'url': {
        'name': 'URL / Dirección Web',
        'pattern': (
            r'(https?|ftp)'
            r'://'
            r'([a-zA-Z0-9\-]+\.)*'
            r'[a-zA-Z0-9\-]+'
            r'\.[a-zA-Z][a-zA-Z][a-zA-Z]?[a-zA-Z]?[a-zA-Z]?[a-zA-Z]?'
            r'(/[a-zA-Z0-9._/\-?=&#%]*)?'
        ),
        'description': 'URL completa con esquema http, https o ftp',
        'valid_ex':   ['https://www.google.com', 'http://ejemplo.co/ruta',
                        'https://sub.dominio.org/page?id=1&ref=main',
                        'ftp://archivos.servidor.net'],
        'invalid_ex': ['www.google.com', 'ftp:/dominio.com', '://sin-esquema.com'],
    },

    'placa_co': {
        'name': 'Placa Vehicular Colombiana',
        'pattern': (
            r'[A-Z][A-Z][A-Z]'
            r'[\-]?'
            r'([0-9][0-9][0-9]'
            r'|[0-9][0-9][A-Z])'
        ),
        'description': 'Placa colombiana de vehículo (carro o moto)',
        'valid_ex':   ['ABC123', 'XYZ-456', 'DEF78G', 'AAA-000'],
        'invalid_ex': ['AB123', 'ABCD123', '123ABC', 'abc123'],
    },

    'cedula_co': {
        'name': 'Cédula de Ciudadanía',
        'pattern': (
            r'[1-9]'
            r'[0-9][0-9][0-9][0-9][0-9][0-9]'
            r'([0-9]([0-9]([0-9])?)?)?'
        ),
        'description': 'Cédula de ciudadanía colombiana: 7 a 10 dígitos',
        'valid_ex':   ['1234567', '12345678', '1234567890'],
        'invalid_ex': ['123456', '12345678901', '01234567'],
    },

    'codigo_postal': {
        'name': 'Código Postal',
        'pattern': r'[0-9][0-9][0-9][0-9][0-9][0-9]',
        'description': 'Código postal colombiano: exactamente 6 dígitos',
        'valid_ex':   ['110111', '050001', '760020'],
        'invalid_ex': ['11011', '1100111', 'AB1234'],
    },

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

    'hora': {
        'name': 'Hora',
        'pattern': (
            r'(2[0-3]|[01]?[0-9])'
            r':'
            r'[0-5][0-9]'
            r'(:[0-5][0-9])?'
            r'( ?(AM|PM|am|pm))?'
        ),
        'description': 'Hora en formato HH:MM o HH:MM:SS con AM/PM opcional',
        'valid_ex':   ['08:30', '23:59:59', '12:00 PM', '00:00:01'],
        'invalid_ex': ['25:00', '08:60', '12:61:00'],
    },

    'hashtag': {
        'name': 'Hashtag',
        'pattern': r'#[a-zA-Z][a-zA-Z0-9_]+',
        'description': 'Hashtag de redes sociales: # seguido de letras y dígitos',
        'valid_ex':   ['#Python', '#IA2024', '#hola_mundo'],
        'invalid_ex': ['#', '#123inicio', '# con espacio'],
    },

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
