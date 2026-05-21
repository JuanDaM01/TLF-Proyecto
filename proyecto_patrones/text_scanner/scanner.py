import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.regex_engine import RegexEngine
from patterns.definitions import PATTERNS


class ScanResult:
    """Coincidencia: patron, valor, posicion y contexto."""

    def __init__(self, pattern_name, value, start, end, context=""):
        self.pattern_name = pattern_name
        self.value = value
        self.start = start
        self.end = end
        self.context = context

    def __repr__(self):
        return (f"ScanResult(pattern='{self.pattern_name}', "
                f"value='{self.value}', pos={self.start}:{self.end})")


class TextScanner:
    """Aplica patrones de PATTERNS sobre texto y genera reporte."""

    CONTEXT_WINDOW = 20

    def __init__(self, selected_patterns=None):
        """Compila motores una vez; selected_patterns limita las claves."""
        self._engines = {}
        keys = selected_patterns or list(PATTERNS.keys())

        for key in keys:
            if key in PATTERNS:
                try:
                    self._engines[key] = RegexEngine(PATTERNS[key]['pattern'])
                except Exception as e:
                    print(f"[ADVERTENCIA] No se pudo compilar patrón '{key}': {e}")

    def _extract_context(self, text, start, end):
        """Fragmento de texto alrededor del match."""
        ctx_start = max(0, start - self.CONTEXT_WINDOW)
        ctx_end = min(len(text), end + self.CONTEXT_WINDOW)

        prefix = "..." if ctx_start > 0 else ""
        suffix = "..." if ctx_end < len(text) else ""
        snippet = text[ctx_start:ctx_end]

        return f"{prefix}{snippet}{suffix}"

    def scan(self, text: str) -> dict:
        """Devuelve { clave_patron: [ScanResult, ...] }."""
        if not text or not text.strip():
            return {}

        results = {}

        for key, engine in self._engines.items():
            matches = engine.search(text)
            if matches:
                results[key] = []
                for m in matches:
                    context = self._extract_context(text, m['start'], m['end'])
                    results[key].append(ScanResult(
                        pattern_name=PATTERNS[key]['name'],
                        value=m['value'],
                        start=m['start'],
                        end=m['end'],
                        context=context
                    ))

        return results

    def generate_report(self, results: dict) -> str:
        """Reporte de texto con todas las coincidencias."""
        if not results:
            return "No se encontraron coincidencias en el texto analizado.\n"

        lines = []
        lines.append("=" * 65)
        lines.append("  REPORTE DE ANÁLISIS DE PATRONES")
        lines.append("=" * 65)

        total = sum(len(v) for v in results.values())
        lines.append(f"  Total de coincidencias: {total}")
        lines.append("=" * 65)

        for key, matches in results.items():
            pattern_info = PATTERNS.get(key, {})
            name = pattern_info.get('name', key)
            desc = pattern_info.get('description', '')

            lines.append(f"\n{name.upper()} ({len(matches)} encontrado(s))")
            lines.append(f"   Descripción: {desc}")
            lines.append("   " + "-" * 55)

            for i, match in enumerate(matches, 1):
                lines.append(f"   [{i}] Valor   : '{match.value}'")
                lines.append(f"       Posición: {match.start} -> {match.end}")
                lines.append(f"       Contexto: {match.context}")
                lines.append("")

        lines.append("=" * 65)
        return "\n".join(lines)

    def scan_and_report(self, text: str) -> tuple:
        """scan() y generate_report() en una llamada."""
        results = self.scan(text)
        report = self.generate_report(results)
        return results, report
