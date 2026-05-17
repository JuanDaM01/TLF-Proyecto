# =============================================================================
# ui/services.py — Lógica de presentación desacoplada de la vista
# =============================================================================

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from patterns.definitions import PATTERNS


def export_text_report(content: str, path: str) -> None:
    header = (
        '=' * 72 + '\n'
        'LUMEN — REPORTE DE ANÁLISIS DE PATRONES\n'
        f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        '=' * 72 + '\n\n'
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(header + content)


def export_catalog_json(path: str) -> None:
    payload: dict[str, Any] = {
        'generated_at': datetime.now().isoformat(),
        'engine': 'RegexEngine (motor propio TLF)',
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
        '# Catálogo de Patrones — Lumen TLF\n',
        f'*Exportado: {datetime.now().strftime("%Y-%m-%d %H:%M")}*\n',
    ]
    for key, info in PATTERNS.items():
        lines.append(f'\n## {info["name"]} (`{key}`)\n')
        lines.append(f'{info["description"]}\n')
        lines.append(f'```regex\n{info["pattern"]}\n```\n')
        lines.append('**Válidos:** ' + ' · '.join(info['valid_ex'][:4]) + '\n')
        lines.append('**Inválidos:** ' + ' · '.join(info['invalid_ex'][:4]) + '\n')
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)


HELP_DOCUMENTATION = """
LUMEN — GUÍA RÁPIDA

▸ Escáner de Textos
  · Seleccione patrones con los checkboxes o use "Seleccionar todos"
  · Pegue texto o cargue un archivo .txt
  · Pulse "Analizar Texto" para detectar coincidencias
  · Exporte el reporte cuando termine el análisis

▸ Validador Interactivo
  · Complete el formulario; cada campo se valida en tiempo real
  · El botón Enviar se habilita cuando todos los obligatorios son válidos

▸ Catálogo de Patrones
  · Consulte las expresiones regulares del motor propio
  · Exporte el catálogo en JSON o Markdown
  · Use la búsqueda para filtrar por nombre

Motor: Lexer → Parser → NFA (Thompson) → DFA → Match
Proyecto: Teoría de Lenguajes Formales (TLF)
""".strip()
