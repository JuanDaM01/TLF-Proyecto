# =============================================================================
# text_scanner/scanner.py
# Módulo de búsqueda y extracción de patrones en texto libre
#
# Este módulo orquesta el RegexEngine para aplicar todos los patrones
# definidos sobre un texto de entrada y generar un reporte estructurado.
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.regex_engine import RegexEngine
from patterns.definitions import PATTERNS


class ScanResult:
    """
    Representa una coincidencia encontrada en el texto.
    
    Atributos:
        pattern_name (str): Nombre del patrón que hizo match.
        value (str): Subcadena encontrada.
        start (int): Posición inicial en el texto original.
        end (int): Posición final (exclusiva) en el texto original.
        context (str): Fragmento del texto alrededor de la coincidencia.
    """
    def __init__(self, pattern_name, value, start, end, context=""):
        self.pattern_name = pattern_name
        self.value        = value
        self.start        = start
        self.end          = end
        self.context      = context

    def __repr__(self):
        return (f"ScanResult(pattern='{self.pattern_name}', "
                f"value='{self.value}', pos={self.start}:{self.end})")


class TextScanner:
    """
    Escáner de patrones sobre texto libre.
    
    Compila una vez cada patrón y los aplica eficientemente
    sobre el texto de entrada. Genera un reporte con todas las
    coincidencias encontradas, organizadas por tipo de patrón.
    
    Ejemplo de uso:
        scanner = TextScanner()
        results = scanner.scan(texto_largo)
        report  = scanner.generate_report(results)
    """

    CONTEXT_WINDOW = 20  # Caracteres de contexto a cada lado del match

    def __init__(self, selected_patterns=None):
        """
        Inicializa el escáner y compila los motores regex.
        
        Args:
            selected_patterns (list[str], optional): Lista de claves de patrones
                a usar. Si es None, se usan todos los patrones disponibles.
        
        Nota: La compilación ocurre una sola vez en el constructor,
              no en cada llamada a scan(). Esto es una optimización importante
              para textos largos o múltiples escaneos.
        """
        self._engines = {}
        keys = selected_patterns or list(PATTERNS.keys())

        for key in keys:
            if key in PATTERNS:
                try:
                    self._engines[key] = RegexEngine(PATTERNS[key]['pattern'])
                except Exception as e:
                    print(f"[ADVERTENCIA] No se pudo compilar patrón '{key}': {e}")

    def _extract_context(self, text, start, end):
        """
        Extrae un fragmento de contexto alrededor de la coincidencia.
        
        Args:
            text (str): Texto completo.
            start (int): Inicio del match.
            end (int): Fin del match.
        
        Returns:
            str: Fragmento de contexto con '...' si fue truncado.
        """
        ctx_start = max(0, start - self.CONTEXT_WINDOW)
        ctx_end   = min(len(text), end + self.CONTEXT_WINDOW)

        prefix  = "..." if ctx_start > 0 else ""
        suffix  = "..." if ctx_end < len(text) else ""
        snippet = text[ctx_start:ctx_end]

        return f"{prefix}{snippet}{suffix}"

    def scan(self, text: str) -> dict:
        """
        Aplica todos los patrones compilados sobre el texto.
        
        Args:
            text (str): Texto libre a analizar.
        
        Returns:
            dict: Diccionario { pattern_key: [ScanResult, ...] }
                  con todas las coincidencias encontradas.
        """
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
                        pattern_name = PATTERNS[key]['name'],
                        value        = m['value'],
                        start        = m['start'],
                        end          = m['end'],
                        context      = context
                    ))

        return results

    def generate_report(self, results: dict) -> str:
        """
        Genera un reporte de texto formateado con todas las coincidencias.
        
        Args:
            results (dict): Resultado de scan().
        
        Returns:
            str: Reporte legible para mostrar al usuario.
        """
        if not results:
            return "⚠️  No se encontraron coincidencias en el texto analizado.\n"

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

            lines.append(f"\n🔍 {name.upper()} ({len(matches)} encontrado(s))")
            lines.append(f"   Descripción: {desc}")
            lines.append("   " + "-" * 55)

            for i, match in enumerate(matches, 1):
                lines.append(f"   [{i}] Valor   : '{match.value}'")
                lines.append(f"       Posición: {match.start} → {match.end}")
                lines.append(f"       Contexto: {match.context}")
                lines.append("")

        lines.append("=" * 65)
        return "\n".join(lines)

    def scan_and_report(self, text: str) -> tuple:
        """
        Combina scan() y generate_report() en una sola llamada.
        
        Returns:
            tuple: (results_dict, report_string)
        """
        results = self.scan(text)
        report  = self.generate_report(results)
        return results, report
