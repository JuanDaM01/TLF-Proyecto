import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.regex_engine import RegexEngine
from text_scanner.scanner import TextScanner
from patterns.definitions import PATTERNS


class TestRunner:
    """Runner de pruebas sin dependencias externas."""
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


def test_motor_basico():
    runner = TestRunner("Motor Regex — Operaciones Básicas")

    e = RegexEngine(r'abc')
    runner.assert_match(e, 'abc',  True,  "Literal exacto")
    runner.assert_match(e, 'ab',   False, "Literal incompleto")
    runner.assert_match(e, 'abcd', False, "Literal con extra")
    runner.assert_match(e, '',     False, "Vacío vs literal")

    e = RegexEngine(r'a*')
    runner.assert_match(e, '',     True,  "Kleene: cadena vacía")
    runner.assert_match(e, 'a',    True,  "Kleene: uno")
    runner.assert_match(e, 'aaa',  True,  "Kleene: varios")

    e = RegexEngine(r'a+')
    runner.assert_match(e, '',     False, "Plus: vacío rechazado")
    runner.assert_match(e, 'a',    True,  "Plus: uno aceptado")
    runner.assert_match(e, 'aaaa', True,  "Plus: varios aceptados")

    e = RegexEngine(r'colou?r')
    runner.assert_match(e, 'color',  True,  "Question: sin 'u'")
    runner.assert_match(e, 'colour', True,  "Question: con 'u'")
    runner.assert_match(e, 'colouur',False, "Question: dos 'u' rechazado")

    e = RegexEngine(r'gato|perro')
    runner.assert_match(e, 'gato',  True,  "Alt: primera opción")
    runner.assert_match(e, 'perro', True,  "Alt: segunda opción")
    runner.assert_match(e, 'conejo',False, "Alt: ninguna opción")

    e = RegexEngine(r'a.c')
    runner.assert_match(e, 'abc', True,  "Dot: cualquier char")
    runner.assert_match(e, 'a1c', True,  "Dot: dígito")
    runner.assert_match(e, 'ac',  False, "Dot: falta char medio")

    e = RegexEngine(r'[0-9]+')
    runner.assert_match(e, '123',  True,  "Clase [0-9]+")
    runner.assert_match(e, '0',    True,  "Clase [0-9]+: un dígito")
    runner.assert_match(e, 'abc',  False, "Clase [0-9]+: letras rechazadas")

    e = RegexEngine(r'[a-zA-Z]+')
    runner.assert_match(e, 'Hola',  True,  "Clase letras mixtas")
    runner.assert_match(e, 'h3lo',  False, "Clase letras: dígito rechazado")

    e = RegexEngine(r'[^0-9]+')
    runner.assert_match(e, 'abc',  True,  "Negado [^0-9]+: letras")
    runner.assert_match(e, '123',  False, "Negado [^0-9]+: dígitos rechazados")

    e = RegexEngine(r'\d+')
    runner.assert_match(e, '999',  True,  r"Escape \d+: dígitos")
    runner.assert_match(e, 'abc',  False, r"Escape \d+: letras rechazadas")

    e = RegexEngine(r'\w+')
    runner.assert_match(e, 'user_123', True,  r"Escape \w+: alfanumérico")
    runner.assert_match(e, 'hola!',   False, r"Escape \w+: especial rechazado")

    runner.report()
    return runner.passed, runner.failed


def test_emails():
    runner = TestRunner("Correos Electrónicos")
    e      = RegexEngine(PATTERNS['email']['pattern'])

    validos = [
        'usuario@ejemplo.com',
        'nombre.apellido@empresa.co',
        'admin@sub.empresa.edu',
        'test.123@mail.net',
        'a@b.co',
    ]
    for email in validos:
        runner.assert_match(e, email, True, f"VÁLIDO: email")

    invalidos = [
        '@sinusuario.com',
        'sin_arroba.com',
        'usuario@',
        'usuario@dominio',
        'juan+perez@empresa.com',
        'dos@@arrobas.com',
        '',
        'espacio en@medio.com',
    ]
    for email in invalidos:
        runner.assert_match(e, email, False, f"INVÁLIDO: email")

    texto = "Para soporte: ayuda@empresa.com, ventas@tienda.co.uk y spam@fake"
    runner.assert_search_count(e, texto, 2, "Emails en texto")

    runner.report()
    return runner.passed, runner.failed


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
        '2001234567',
        '',
        'abc',
        '+58 3201234567',
    ]
    for tel in invalidos:
        runner.assert_match(e, tel, False, f"INVÁLIDO: teléfono")

    runner.report()
    return runner.passed, runner.failed


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
        '32/01/2023',
        '15/13/2023',
        '15-6-23',
        '2023/06/15',
        '',
        '00/00/0000',
    ]
    for f in invalidos:
        runner.assert_match(e, f, False, f"INVÁLIDO: fecha")

    runner.report()
    return runner.passed, runner.failed


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
        'www.google.com',
        'http:/dominio.com',
        '://sin-esquema.com',
        '',
        'htp://typo.com',
    ]
    for url in invalidos:
        runner.assert_match(e, url, False, f"INVÁLIDO: URL")

    runner.report()
    return runner.passed, runner.failed


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


def test_fecha_iso():
    runner = TestRunner("Fecha ISO 8601")
    e = RegexEngine(PATTERNS['fecha_iso']['pattern'])

    validos = ['2023-06-15', '1999-12-31', '2000-01-01']
    invalidos = ['23-06-15', '2023-13-01', '2023-00-10', '20230615', '']

    for f in validos:
        runner.assert_match(e, f, True, "VÁLIDO: fecha_iso")
    for f in invalidos:
        runner.assert_match(e, f, False, "INVÁLIDO: fecha_iso")

    runner.report()
    return runner.passed, runner.failed


def test_codigo_postal():
    runner = TestRunner("Código Postal")
    e = RegexEngine(PATTERNS['codigo_postal']['pattern'])

    validos = ['110111', '050001', '760020']
    invalidos = ['11011', '1100111', 'AB1234', '', '12345a']

    for c in validos:
        runner.assert_match(e, c, True, "VÁLIDO: codigo_postal")
    for c in invalidos:
        runner.assert_match(e, c, False, "INVÁLIDO: codigo_postal")

    runner.report()
    return runner.passed, runner.failed


def test_tarjeta_credito():
    runner = TestRunner("Tarjeta de Crédito")
    e = RegexEngine(PATTERNS['tarjeta_credito']['pattern'])

    validos = ['4111111111111111', '4111-1111-1111-1111', '4111 1111 1111 1111']
    invalidos = ['411111111111111', '4111-111-1111-1111', 'abcd1234efgh5678', '', '4111 1111 1111']

    for t in validos:
        runner.assert_match(e, t, True, "VÁLIDO: tarjeta_credito")
    for t in invalidos:
        runner.assert_match(e, t, False, "INVÁLIDO: tarjeta_credito")

    runner.report()
    return runner.passed, runner.failed


def test_scanner_texto_mixto():
    runner = TestRunner("Escáner — Texto Mixto con Múltiples Patrones")

    texto = """
    Estimado cliente,

    Le contactamos desde soporte@empresa.com para informarle sobre su pedido.
    Tambien puede llamarnos al 3201234567 o al fijo 601-5551234.

    Su fecha de registro fue el 15/08/2023 y su cedula registrada: 1098765432.

    Visite nuestra pegina en https://www.empresa.com/soporte para mas info.
    El servidor de pagos esta en 192.168.10.50.

    Placa de la moto de reparto: GHI45J
    Etiqueta en redes: #Envio

    Atentamente,
    El equipo de soporte.
    """

    scanner = TextScanner()
    results = scanner.scan(texto)

    runner.assert_true('email'        in results, "Detectó: correo electrónico")
    runner.assert_true('telefono_co'  in results, "Detectó: teléfono")
    runner.assert_true('fecha'        in results, "Detectó: fecha")
    runner.assert_true('cedula_co'    in results, "Detectó: cédula")
    runner.assert_true('url'          in results, "Detectó: URL")
    runner.assert_true('ipv4'         in results, "Detectó: IPv4")
    runner.assert_true('placa_co'     in results, "Detectó: placa")
    runner.assert_true('hashtag'      in results, "Detectó: hashtag")

    if 'email' in results:
        runner.assert_true(
            len(results['email']) >= 1,
            f"Encontró al menos 1 email (encontró {len(results['email'])})"
        )

    runner.report()
    return runner.passed, runner.failed


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
        (validar_email, 'juan+perez@empresa.com', False),
        (validar_email, 'no-email', False),
        (validar_telefono, '3001234567', True),
        (validar_telefono, '123', False),
        (validar_telefono, '+57 3201234567', True),
        (validar_telefono, '+58 3201234567', False),
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
    """Ejecuta todas las suites y muestra resumen."""
    print("\n" + "=" * 65)
    print("  EJECUCION COMPLETA DE CASOS DE PRUEBA")
    print("  Sistema de Patrones — Teoria de Lenguajes Formales")
    print("=" * 65)

    suites = [
        ("Motor Basico",         test_motor_basico),
        ("Correos",              test_emails),
        ("Telefonos",            test_telefonos),
        ("Fechas",               test_fechas),
        ("Fecha ISO",            test_fecha_iso),
        ("URLs",                 test_urls),
        ("Placas",               test_placas),
        ("IPv4",                 test_ipv4),
        ("Codigo Postal",        test_codigo_postal),
        ("Tarjeta Credito",      test_tarjeta_credito),
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
