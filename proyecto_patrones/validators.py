from core.engine_manager import EngineManager


def validar_nombre(texto: str) -> tuple[bool, str]:
    texto = texto.strip()
    if not texto:
        return False, 'El nombre no puede estar vacío'
    try:
        eng = EngineManager.get_custom(
            r'[A-Za-zÁÉÍÓÚáéíóúÑñ]+( [A-Za-zÁÉÍÓÚáéíóúÑñ]+)+',
            key='nombre',
        )
        if eng.match(texto):
            return True, ''
        return False, 'Ingrese nombre y apellido (solo letras, Ej: María García López)'
    except ValueError as exc:
        return False, str(exc)


def validar_email(texto: str) -> tuple[bool, str]:
    texto = texto.strip()
    if not texto:
        return False, 'El correo no puede estar vacío'
    try:
        if EngineManager.get('email').match(texto):
            return True, ''
        return False, 'Formato inválido. Ej: usuario@dominio.com'
    except (KeyError, ValueError) as exc:
        return False, str(exc)


def validar_telefono(texto: str) -> tuple[bool, str]:
    texto = texto.strip()
    if not texto:
        return False, 'El teléfono no puede estar vacío'
    try:
        if EngineManager.get('telefono_co').match(texto):
            return True, ''
        return False, 'Formato inválido. Ej: 3001234567 o +57 310 555 9999'
    except (KeyError, ValueError) as exc:
        return False, str(exc)


def validar_fecha(texto: str) -> tuple[bool, str]:
    texto = texto.strip()
    if not texto:
        return False, 'La fecha no puede estar vacía'
    try:
        if EngineManager.get('fecha').match(texto):
            return True, ''
        return False, 'Formato inválido. Use DD/MM/AAAA (Ej: 25/12/1990)'
    except (KeyError, ValueError) as exc:
        return False, str(exc)


def validar_cedula(texto: str) -> tuple[bool, str]:
    texto = texto.strip()
    if not texto:
        return False, 'La cédula no puede estar vacía'
    try:
        if EngineManager.get('cedula_co').match(texto):
            return True, ''
        return False, 'Debe tener entre 6 y 10 dígitos, sin separadores'
    except (KeyError, ValueError) as exc:
        return False, str(exc)


def validar_url(texto: str) -> tuple[bool, str]:
    texto = texto.strip()
    if not texto:
        return True, ''
    try:
        if EngineManager.get('url').match(texto):
            return True, ''
        return False, 'URL inválida. Debe iniciar con http://, https:// o ftp://'
    except (KeyError, ValueError) as exc:
        return False, str(exc)


def validar_usuario(texto: str) -> tuple[bool, str]:
    texto = texto.strip()
    if not texto:
        return False, 'El usuario no puede estar vacío'
    if len(texto) < 4:
        return False, 'Mínimo 4 caracteres'
    if len(texto) > 20:
        return False, 'Máximo 20 caracteres'
    try:
        if EngineManager.get_custom(r'[a-zA-Z][a-zA-Z0-9_]+', key='usuario').match(texto):
            return True, ''
        return False, 'Solo letras, dígitos y _, debe iniciar con letra'
    except ValueError as exc:
        return False, str(exc)


def validar_contrasena(texto: str) -> tuple[bool, str]:
    """Validación compuesta (no regex única): reglas acumulativas de seguridad."""
    if not texto:
        return False, 'La contraseña no puede estar vacía'
    if len(texto) < 8:
        return False, 'Mínimo 8 caracteres'
    faltantes = []
    if not any(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in texto):
        faltantes.append('mayúscula')
    if not any(c in 'abcdefghijklmnopqrstuvwxyz' for c in texto):
        faltantes.append('minúscula')
    if not any(c in '0123456789' for c in texto):
        faltantes.append('dígito')
    if not any(c in '@#$%^&*()_+!' for c in texto):
        faltantes.append('especial (@#$%^&*)')
    if faltantes:
        return False, f"Falta: {', '.join(faltantes)}"
    return True, ''


FORM_FIELDS = (
    ('nombre', 'Nombre Completo', validar_nombre),
    ('usuario', 'Nombre de Usuario', validar_usuario),
    ('email', 'Correo Electrónico', validar_email),
    ('password', 'Contraseña', validar_contrasena),
    ('telefono', 'Teléfono Colombiano', validar_telefono),
    ('cedula', 'Cédula de Ciudadanía', validar_cedula),
    ('fecha_nac', 'Fecha de Nacimiento', validar_fecha),
    ('sitio_web', 'Sitio Web (opcional)', validar_url),
)
