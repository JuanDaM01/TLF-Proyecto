# =============================================================================
# tests/test_cases.py
# Suite completa de casos de prueba
# Cubre todos los patrones con entradas válidas e inválidas.
# NO usa unittest ni pytest para mantener la independencia de librerías.
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.regex_engine import RegexEngine
from text_scanner.scanner import TextScanner
from patterns.definitions import PATTERNS


# ===========================================================================
# FRAMEWORK MÍNIMO DE PRUEBAS
# ===========================================================================

class TestRunner:
    """
    Framework de pruebas minimalista sin dependencias externas.
    Ejecuta casos y reporta resultados con estadísticas.
    """
    def __init__(self, name):
        self.name    = name
        self.passed  = 0
        self.failed  = 0
        self.results = []

    def assert_true(self, condition, description, details=""):
        status = "[PASS]" if condition else "[FAIL]"
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        self.results.append((status, description, details))

    def assert_match(self, engine, text, expected, label=""):
        result = engine.match(text)
        desc   = f"{label} | match('{text}') == {expected}"
        detail = f"  -> Motor retorno: {result}"
        self.assert_true(result == expected, desc, detail)

    def assert_search_count(self, engine, text, expected_count, label=""):
        matches = engine.search(text)
        desc    = f"{label} | search en texto -> {expected_count} coincidencias"
        detail  = f"  -> Motor encontro: {len(matches)}: {[m['value'] for m in matches]}"
        self.assert_true(len(matches) == expected_count, desc, detail)

    def report(self):
        total = self.passed + self.failed
        print(f"\n{'='*65}")
        print(f"  SUITE: {self.name}")
        print(f"  Total: {total} | Pasaron: {self.passed} | Fallaron: {self.failed}")
        print(f"{'='*65}")
        for status, desc, detail in self.results:
            print(f"  {status}: {desc}")
            if "FAIL" in status and detail:
                print(f"          {detail}")
        print(f"{'='*65}")
        return self.failed == 0


# ===========================================================================
# SUITE 1: MOTOR REGEX — OPERACIONES BÁSICAS
# ===========================================================================

def test_motor_basico():
    runner = TestRunner("Motor Regex — Operaciones Básicas")

    # --- Caracteres literales ---
    e = RegexEngine(r'abc')
    runner.assert_match(e, 'abc',  True,  "Literal exacto")
    runner.assert_match(e, 'ab',   False, "Literal incompleto")
    runner.assert_match(e, 'abcd', False, "Literal con extra")
    runner.assert_match(e, '',     False, "Vacío vs literal")

    # --- Cuantificador * (cero o más) ---
    e = RegexEngine(r'a*')
    runner.assert_match(e, '',     True,  "Kleene: cadena vacía")
    runner.assert_match(e, 'a',    True,  "Kleene: uno")
    runner.assert_match(e, 'aaa',  True,  "Kleene: varios")

    # --- Cuantificador + (uno o más) ---
    e = RegexEngine(r'a+')
    runner.assert_match(e, '',     False, "Plus: vacío rechazado")
    runner.assert_match(e, 'a',    True,  "Plus: uno aceptado")
    runner.assert_match(e, 'aaaa', True,  "Plus: varios aceptados")

    # --- Cuantificador ? (cero o uno) ---
    e = RegexEngine(r'colou?r')
    runner.assert_match(e, 'color',  True,  "Question: sin 'u'")
    runner.assert_match(e, 'colour', True,  "Question: con 'u'")
    runner.assert_match(e, 'colouur',False, "Question: dos 'u' rechazado")

    # --- Alternación | ---
    e = RegexEngine(r'gato|perro')
    runner.assert_match(e, 'gato',  True,  "Alt: primera opción")
    runner.assert_match(e, 'perro', True,  "Alt: segunda opción")
    runner.assert_match(e, 'conejo',False, "Alt: ninguna opción")

    # --- Metacarácter . ---
    e = RegexEngine(r'a.c')
    runner.assert_match(e, 'abc', True,  "Dot: cualquier char")
    runner.assert_match(e, 'a1c', True,  "Dot: dígito")
    runner.assert_match(e, 'ac',  False, "Dot: falta char medio")

    # --- Clases de caracteres ---
    e = RegexEngine(r'[0-9]+')
    runner.assert_match(e, '123',  True,  "Clase [0-9]+")
    runner.assert_match(e, '0',    True,  "Clase [0-9]+: un dígito")
    runner.assert_match(e, 'abc',  False, "Clase [0-9]+: letras rechazadas")

    e = RegexEngine(r'[a-zA-Z]+')
    runner.assert_match(e, 'Hola',  True,  "Clase letras mixtas")
    runner.assert_match(e, 'h3lo',  False, "Clase letras: dígito rechazado")

    # --- Clases negadas ---
    e = RegexEngine(r'[^0-9]+')
    runner.assert_match(e, 'abc',  True,  "Negado [^0-9]+: letras")
    runner.assert_match(e, '123',  False, "Negado [^0-9]+: dígitos rechazados")

    # --- Escape \d ---
    e = RegexEngine(r'\d+')
    runner.assert_match(e, '999',  True,  r"Escape \d+: dígitos")
    runner.assert_match(e, 'abc',  False, r"Escape \d+: letras rechazadas")

    # --- Escape \w ---
    e = RegexEngine(r'\w+')
    runner.assert_match(e, 'user_123', True,  r"Escape \w+: alfanumérico")
    runner.assert_match(e, 'hola!',   False, r"Escape \w+: especial rechazado")

    runner.report()
    return runner.passed, runner.failed


# ===========================================================================
# SUITE 2: CORREOS ELECTRÓNICOS
# ===========================================================================

def test_emails():
    runner = TestRunner("Correos Electrónicos")
    e      = RegexEngine(PATTERNS['email']['pattern'])

    # Válidos
    validos = [
        'usuario@ejemplo.com',
        'nombre.apellido@empresa.co',
        'contacto+info@dominio.org',
        'admin@sub.empresa.edu',
        'test.123@mail.net',
        'a@b.co',
    ]
    for email in validos:
        runner.assert_match(e, email, True, f"VÁLIDO: email")

    # Inválidos
    invalidos = [
        '@sinusuario.com',
        'sin_arroba.com',
        'usuario@',
        'usuario@dominio',
        'dos@@arrobas.com',
        '',
        'espacio en@medio.com',
    ]
    for email in invalidos:
        runner.assert_match(e, email, False, f"INVÁLIDO: email")

    # Búsqueda en texto
    texto = "Para soporte: ayuda@empresa.com, ventas@tienda.co.uk y spam@fake"
    runner.assert_search_count(e, texto, 2, "Emails en texto")

    runner.report()
    return runner.passed, runner.failed


# ===========================================================================
# SUITE 3: TELÉFONOS COLOMBIANOS
# ===========================================================================

def test_telefonos():
    runner = TestRunner("Teléfonos Colombianos")
    e      = RegexEngine(PATTERNS['telefono_co']['pattern'])

    validos = [
        '3001234567',
        '3201234567',
        '+573201234567',
        '573001234567',
    ]
    for tel in validos:
        runner.assert_match(e, tel, True, f"VÁLIDO: teléfono")

    invalidos = [
        '12345',
        '2001234567',   # No empieza en 3 ni tiene indicativo fijo válido
        '',
        'abc',
    ]
    for tel in invalidos:
        runner.assert_match(e, tel, False, f"INVÁLIDO: teléfono")

    runner.report()
    return runner.passed, runner.failed


# ===========================================================================
# SUITE 4: FECHAS
# ===========================================================================

def test_fechas():
    runner = TestRunner("Fechas DD/MM/AAAA")
    e      = RegexEngine(PATTERNS['fecha']['pattern'])

    validos = [
        '15/06/2023', '01-12-1999', '31.01.2000',
        '29/02/2000', '01/01/1900', '31/12/2099'
    ]
    for f in validos:
        runner.assert_match(e, f, True, f"VÁLIDO: fecha")

    invalidos = [
        '32/01/2023',   # día 32 inválido
        '15/13/2023',   # mes 13 inválido
        '15-6-23',      # año de 2 dígitos
        '2023/06/15',   # formato ISO en lugar de DD/MM/AAAA
        '',
        '00/00/0000',
    ]
    for f in invalidos:
        runner.assert_match(e, f, False, f"INVÁLIDO: fecha")

    runner.report()
    return runner.passed, runner.failed


# ===========================================================================
# SUITE 5: URLs
# ===========================================================================

def test_urls():
    runner = TestRunner("URLs")
    e      = RegexEngine(PATTERNS['url']['pattern'])

    validos = [
        'https://www.google.com',
        'http://ejemplo.co',
        'ftp://archivos.servidor.net',
        'https://api.servicio.org/v2/users?id=1',
    ]
    for url in validos:
        runner.assert_match(e, url, True, f"VÁLIDO: URL")

    invalidos = [
        'www.google.com',       # sin esquema
        'http:/dominio.com',    # falta segunda barra
        '://sin-esquema.com',
        '',
        'htp://typo.com',       # esquema incorrecto
    ]
    for url in invalidos:
        runner.assert_match(e, url, False, f"INVÁLIDO: URL")

    runner.report()
    return runner.passed, runner.failed


# ===========================================================================
# SUITE 6: PLACAS VEHICULARES
# ===========================================================================

def test_placas():
    runner = TestRunner("Placas Vehiculares Colombianas")
    e      = RegexEngine(PATTERNS['placa_co']['pattern'])

    validos   = ['ABC123', 'XYZ-456', 'DEF78G', 'AAA-000']
    invalidos = ['AB123', 'ABCD123', '123ABC', 'abc123', 'AB-1234']

    for p in validos:
        runner.assert_match(e, p, True,  f"VÁLIDO: placa")
    for p in invalidos:
        runner.assert_match(e, p, False, f"INVÁLIDO: placa")

    runner.report()
    return runner.passed, runner.failed


# ===========================================================================
# SUITE 7: IPv4
# ===========================================================================

def test_ipv4():
    runner = TestRunner("Direcciones IPv4")
    e      = RegexEngine(PATTERNS['ipv4']['pattern'])

    validos   = ['192.168.1.1', '10.0.0.1', '255.255.255.0',
                 '0.0.0.0', '127.0.0.1', '172.16.254.1']
    invalidos = ['256.1.1.1', '192.168.1',
                 '192.168.1.1.1', '999.0.0.1', '1.2.3']

    for ip in validos:
        runner.assert_match(e, ip, True,  "VÁLIDO: IPv4")
    for ip in invalidos:
        runner.assert_match(e, ip, False, "INVÁLIDO: IPv4")

    runner.report()
    return runner.passed, runner.failed


# ===========================================================================
# SUITE 8: ESCÁNER DE TEXTO MIXTO
# ===========================================================================

def test_scanner_texto_mixto():
    runner = TestRunner("Escáner — Texto Mixto con Múltiples Patrones")

    texto = """
    Estimado cliente,
    
    Le contactamos desde soporte@empresa.com para informarle sobre su pedido.
    También puede llamarnos al 3201234567 o al fijo 601-5551234.
    
    Su fecha de registro fue el 15/08/2023 y su cédula registrada: 1098765432.
    
    Visite nuestra página en https://www.empresa.com/soporte para más info.
    El servidor de pagos está en 192.168.10.50.
    
    Placa de la moto de reparto: GHI45J
    Etiqueta en redes: #ServicioExcelente
    
    Atentamente,
    El equipo de soporte.
    """

    scanner = TextScanner()
    results = scanner.scan(texto)

    # Verificar que se encontraron los patrones esperados
    runner.assert_true('email'        in results, "Detectó: correo electrónico")
    runner.assert_true('telefono_co'  in results, "Detectó: teléfono")
    runner.assert_true('fecha'        in results, "Detectó: fecha")
    runner.assert_true('cedula_co'    in results, "Detectó: cédula")
    runner.assert_true('url'          in results, "Detectó: URL")
    runner.assert_true('ipv4'         in results, "Detectó: IPv4")
    runner.assert_true('placa_co'     in results, "Detectó: placa")
    runner.assert_true('hashtag'      in results, "Detectó: hashtag")

    # Verificar conteos específicos
    if 'email' in results:
        runner.assert_true(
            len(results['email']) >= 1,
            f"Encontró al menos 1 email (encontró {len(results['email'])})"
        )

    runner.report()
    return runner.passed, runner.failed


# ===========================================================================
# EJECUCIÓN DE TODAS LAS SUITES
# ===========================================================================

def test_validadores_formulario():
    """Etapa B: validación de entradas en sistema interactivo."""
    from validators import (
        validar_cedula, validar_contrasena, validar_email,
        validar_fecha, validar_nombre, validar_telefono, validar_url, validar_usuario,
    )
    runner = TestRunner("Validador — Formulario Interactivo")

    casos = [
        (validar_nombre, 'María García', True),
        (validar_nombre, 'Solo', False),
        (validar_email, 'a@b.co', True),
        (validar_email, 'no-email', False),
        (validar_telefono, '3001234567', True),
        (validar_telefono, '123', False),
        (validar_fecha, '25/12/1990', True),
        (validar_fecha, '32/13/1990', False),
        (validar_cedula, '1234567890', True),
        (validar_cedula, '123', False),
        (validar_usuario, 'user_1', True),
        (validar_usuario, '1user', False),
        (validar_contrasena, 'Segura1!', True),
        (validar_contrasena, 'corta', False),
        (validar_url, '', True),
        (validar_url, 'https://ok.com', True),
        (validar_url, 'sin-esquema.com', False),
    ]
    for fn, texto, esperado in casos:
        ok, _ = fn(texto)
        runner.assert_true(ok == esperado, f"{fn.__name__}('{texto}') -> {esperado}")

    runner.report()
    return runner.passed, runner.failed


def run_all_tests():
    """Ejecuta todas las suites de pruebas y muestra un resumen global."""
    print("\n" + "=" * 65)
    print("  EJECUCION COMPLETA DE CASOS DE PRUEBA")
    print("  Sistema de Patrones — Teoria de Lenguajes Formales")
    print("=" * 65)

    suites = [
        ("Motor Basico",         test_motor_basico),
        ("Correos",              test_emails),
        ("Telefonos",            test_telefonos),
        ("Fechas",               test_fechas),
        ("URLs",                 test_urls),
        ("Placas",               test_placas),
        ("IPv4",                 test_ipv4),
        ("Escaner Mixto",        test_scanner_texto_mixto),
        ("Validador Formulario", test_validadores_formulario),
    ]

    total_pass = 0
    total_fail = 0

    for nombre, func in suites:
        try:
            p, f = func()
            total_pass += p
            total_fail += f
        except Exception as ex:
            print(f"\n[ERROR] en suite '{nombre}': {ex}")
            import traceback; traceback.print_exc()
            total_fail += 1

    total = total_pass + total_fail
    print("\n" + "=" * 65)
    print("  RESUMEN GLOBAL")
    print("=" * 65)
    print(f"  Total de pruebas: {total}")
    print(f"  Aprobadas:        {total_pass}")
    print(f"  Fallidas:         {total_fail}")
    pct = (total_pass / total * 100) if total > 0 else 0
    print(f"  Tasa de exito:    {pct:.1f}%")
    print("=" * 65)

    if total_fail == 0:
        print("\n  TODAS LAS PRUEBAS PASARON.")
    else:
        print(f"\n  {total_fail} prueba(s) requieren atencion.")
    print()
    return total_fail == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if run_all_tests() else 1)