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
                    # Filtrado específico: si el patrón es teléfono colombiano,
                    # ignorar coincidencias que estén inmediatamente precedidas por el prefijo +58.
                    if key == 'telefono_co':
                        # Tomar hasta 4 caracteres antes del match (ej: '+58 ' o '+58').
                        pref_start = max(0, m['start'] - 4)
                        prefix_slice = text[pref_start:m['start']]
                        if prefix_slice.rstrip().endswith('+58'):
                            # Ignorar esta coincidencia porque pertenece a un número con prefijo +58
                            continue
                    # Reglas generales para evitar matches parciales dentro de tokens más largos.
                    def _char_at(idx):
                        if idx < 0 or idx >= len(text):
                            return None
                        return text[idx]

                    def _is_digit(ch):
                        return ch is not None and ch.isdigit()

                    def _is_alnum(ch):
                        return ch is not None and ch.isalnum()

                    # Carácteres permitidos en la parte local de un email (incluye '+' para detección de subaddressing)
                    email_local_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._+-")

                    before = _char_at(m['start'] - 1)
                    after = _char_at(m['end'])

                    # Patrón por patrón: aplicar chequeos de delimitadores para evitar subcoincidencias.
                    if key in ('telefono_co', 'cedula_co', 'codigo_postal'):
                        # Estos son numéricos: rechazar si están dentro de un número más largo (vecino es dígito).
                        if _is_digit(before) or _is_digit(after):
                            continue

                    if key == 'ipv4':
                        # Evitar partir un número largo como '1928.168.0.100' -> no aceptar '28.168.0.100'
                        if _is_digit(before) or _is_digit(after):
                            continue

                    if key == 'hora':
                        # Evitar empates parciales: si el carácter inmediatamente
                        # antes o después es alfanumérico, es muy probable que estemos
                        # dentro de un token más grande (ej: '08L8:00' -> no aceptar '8:00').
                        if _is_alnum(before) or _is_alnum(after):
                            continue

                    if key == 'placa_co' or key == 'hashtag':
                        # Evitar matches embebidos en palabras (letras/dígitos contiguos).
                        if _is_alnum(before) or _is_alnum(after):
                            continue

                    if key == 'placa_co':
                        # Rechazar placas del tipo 'AAA-12A' (letra-letra-letra-guion-digitos-letra)
                        v = m['value']
                        if '-' in v:
                            import re
                            if re.fullmatch(r'[A-Z]{3}-[0-9]{2}[A-Z]', v):
                                continue

                    if key == 'email':
                        # Evitar detectar fragmentos de direcciones que contienen caracteres inválidos
                        # justo antes o después (ej: 'juan+perez@x' -> no detectar 'perez@x').
                        if before is not None and before in email_local_chars:
                            continue
                        if after is not None and (after.isalnum() or after in '._+-'):
                            continue

                    if key == 'url':
                        # Rechazar explícitamente esquemas ftp porque producen
                        # demasiados falsos positivos en textos malformados.
                        if m['value'].startswith('ftp://'):
                            continue
                        # Si el caracter inmediatamente después del match es '%', es malformed.
                        after_char = _char_at(m['end'])
                        if after_char == '%':
                            continue

                        # Extraer hostname simple y rechazar subdominios sospechosos como 'ww'
                        host_part = m['value']
                        # remover esquema
                        for scheme in ('http://', 'https://', 'ftp://'):
                            if host_part.startswith(scheme):
                                host_part = host_part[len(scheme):]
                                break
                        # aislar hasta '/' o '?' o ':'
                        for sep in ('/', '?', ':'):
                            if sep in host_part:
                                host_part = host_part.split(sep, 1)[0]
                        # host labels
                        labels = host_part.split('.') if host_part else []
                        if any(lbl == 'ww' for lbl in labels):
                            continue
                        # Evitar matches parciales: si el carácter justo después del match
                        # es alfanumérico, guion o punto, es probable que el match sea parcial.
                        if after_char is not None and (after_char.isalnum() or after_char in '-.'):
                            continue

                    context = self._extract_context(text, m['start'], m['end'])
                    results[key].append(ScanResult(
                        pattern_name=PATTERNS[key]['name'],
                        value=m['value'],
                        start=m['start'],
                        end=m['end'],
                        context=context
                    ))

        # Post-procesamiento: evitar reportar coincidencias numéricas (cédula/código postal)
        # que se solapen con teléfonos detectados, para reducir falsos positivos.
        if 'telefono_co' in results:
            phone_ranges = [(r.start, r.end) for r in results.get('telefono_co', [])]

            def _overlaps_any(start, end, ranges):
                for a, b in ranges:
                    if not (end <= a or start >= b):
                        return True
                return False

            for numeric_key in ('cedula_co', 'codigo_postal'):
                if numeric_key in results:
                    filtered = [r for r in results[numeric_key]
                                if not _overlaps_any(r.start, r.end, phone_ranges)]
                    if filtered:
                        results[numeric_key] = filtered
                    else:
                        del results[numeric_key]

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
