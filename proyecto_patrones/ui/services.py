from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from patterns.definitions import PATTERNS

def export_text_report(content: str, path: str) -> None:
    header = (
        '=' * 72 + '\n'
        'REPORTE DE ANALISIS DE PATRONES\n'
        f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        '=' * 72 + '\n\n'
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(header + content)

def export_catalog_json(path: str) -> None:
    payload: dict[str, Any] = {
        'generated_at': datetime.now().isoformat(),
        'patterns': {
            key: {
                'name': info['name'],
                'pattern': info['pattern'],
                'description': info['description'],
                'valid_examples': info['valid_ex'],
                'invalid_examples': info['invalid_ex'],
            }
            for key, info in PATTERNS.items()
        },
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def export_catalog_markdown(path: str) -> None:
    lines = [
        '# Catalogo de patrones\n',
        f'*Exportado: {datetime.now().strftime("%Y-%m-%d %H:%M")}*\n',
    ]
    for key, info in PATTERNS.items():
        lines.append(f'\n## {info["name"]} (`{key}`)\n')
        lines.append(f'{info["description"]}\n')
        lines.append(f'```\n{info["pattern"]}\n```\n')
        lines.append('**Validos:** ' + ' · '.join(info['valid_ex'][:4]) + '\n')
        lines.append('**Invalidos:** ' + ' · '.join(info['invalid_ex'][:4]) + '\n')
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

HELP_DOCUMENTATION = """
AYUDA

Escáner de textos
  1. Marque los patrones a detectar (Seleccionar todos / Ninguno).
  2. Pegue texto o cargue un archivo .txt.
  3. Pulse Analizar y revise los resultados.
  4. Opcional: Exportar reporte.

Validador interactivo
  Complete el formulario. Cada campo se valida al escribir.
  Enviar se habilita cuando los 7 campos obligatorios son correctos.

Catálogo de patrones
  Consulte las expresiones regulares y ejemplos.
  Use la búsqueda para filtrar por nombre.
  Exportar guarda el catálogo en JSON o Markdown.
""".strip()
