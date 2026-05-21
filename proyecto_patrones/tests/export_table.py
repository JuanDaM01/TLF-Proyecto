from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.regex_engine import RegexEngine
from patterns.definitions import PATTERNS
from validators import FORM_FIELDS, validar_contrasena, validar_email


def _run_pattern_case(pattern_key: str, text: str, expect_match: bool) -> str:
    try:
        eng = RegexEngine(PATTERNS[pattern_key]['pattern'])
        got = eng.match(text)
        return 'EXITOSO' if got == expect_match else 'FALLIDO'
    except Exception as exc:
        return f'ERROR ({exc})'


def _run_validator(fn, text: str, expect_ok: bool) -> str:
    try:
        ok, _ = fn(text)
        return 'EXITOSO' if ok == expect_ok else 'FALLIDO'
    except Exception as exc:
        return f'ERROR ({exc})'


def write_markdown_table(path: str) -> None:
    rows: list[str] = []

    rows.append('# Tabla de casos de prueba\n')
    rows.append('Proyecto: Busqueda y validacion de patrones — TLF\n')
    rows.append('| Modulo | Caso | Entrada | Resultado esperado | Resultado |')
    rows.append('|--------|------|---------|-------------------|-----------|')

    for key, info in PATTERNS.items():
        for ex in info['valid_ex'][:2]:
            res = _run_pattern_case(key, ex, True)
            rows.append(f'| Escanner ({info["name"]}) | Valido | `{ex}` | Aceptar | {res} |')
        for ex in info['invalid_ex'][:2]:
            res = _run_pattern_case(key, ex, False)
            rows.append(f'| Escanner ({info["name"]}) | Invalido | `{ex}` | Rechazar | {res} |')

    val_samples = [
        ('validar_email', validar_email, 'user@test.com', True),
        ('validar_email', validar_email, 'mal-correo', False),
        ('validar_contrasena', validar_contrasena, 'Segura1!', True),
        ('validar_contrasena', validar_contrasena, 'corta', False),
    ]
    for name, fn, text, exp in val_samples:
        res = _run_validator(fn, text, exp)
        rows.append(f'| Formulario | {name} | `{text}` | {"Valido" if exp else "Invalido"} | {res} |')

    for key, label, fn in FORM_FIELDS:
        if fn:
            rows.append(f'| Formulario | Campo {label} | (ver suite tests) | Regla definida | PENDIENTE/manual |')

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rows) + '\n')
