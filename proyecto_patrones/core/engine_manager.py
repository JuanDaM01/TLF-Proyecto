# =============================================================================
# core/engine_manager.py
# Gestor centralizado de motores RegexEngine con caché y thread-safety básica.
#
# Patrón: Registry + Lazy Initialization
#
# Motivación:
#   Compilar un RegexEngine implica: Lexer → Parser → Thompson → NFA.
#   Si se compila en cada pulsación de tecla del formulario, se desperdicia
#   CPU innecesariamente. Este módulo compila cada patrón UNA sola vez
#   y reutiliza el motor compilado en todas las llamadas posteriores.
#
# Uso:
#   engine = EngineManager.get('email')
#   engine.match("usuario@dominio.com")  # → True
# =============================================================================

from __future__ import annotations
from typing import Dict, Optional
import threading

from .regex_engine import RegexEngine
from patterns.definitions import PATTERNS


class EngineManager:
    """
    Gestor de motores RegexEngine con caché interna.

    Garantías:
      - Cada patrón se compila exactamente una vez (lazy init).
      - Thread-safe para uso concurrente básico (Lock por compilación).
      - Fallo explícito con excepción tipada si el patrón no existe.

    Ejemplo de uso:
        engine = EngineManager.get('email')
        ok = engine.match("user@example.com")

        # Para patrones ad-hoc no definidos en PATTERNS:
        engine = EngineManager.get_custom(r'\\d{4}-\\d{4}', key='codigo')
    """

    # Almacén interno de motores compilados {key → RegexEngine}
    _cache: Dict[str, RegexEngine] = {}

    # Lock para evitar compilación doble en entornos con threads
    _lock: threading.Lock = threading.Lock()

    # -----------------------------------------------------------------------
    # API pública
    # -----------------------------------------------------------------------

    @classmethod
    def get(cls, key: str) -> RegexEngine:
        """
        Retorna el motor compilado para el patrón identificado por `key`.

        Si el motor aún no está compilado, lo compila y lo almacena en caché.
        Si la clave no existe en PATTERNS, lanza KeyError.
        Si el patrón tiene sintaxis inválida, lanza ValueError con detalle.

        Args:
            key (str): Clave del patrón en patterns/definitions.py
                       Ej: 'email', 'telefono_co', 'url'

        Returns:
            RegexEngine: Motor compilado y listo para usar.

        Raises:
            KeyError: Si `key` no está registrado en PATTERNS.
            ValueError: Si el patrón regex tiene sintaxis inválida.
        """
        # Retorno rápido sin lock (double-checked locking pattern)
        if key in cls._cache:
            return cls._cache[key]

        with cls._lock:
            # Segunda verificación dentro del lock (puede que otro hilo
            # lo haya compilado mientras esperábamos el lock)
            if key in cls._cache:
                return cls._cache[key]

            if key not in PATTERNS:
                available = ", ".join(sorted(PATTERNS.keys()))
                raise KeyError(
                    f"Patrón '{key}' no registrado en PATTERNS.\n"
                    f"Disponibles: {available}"
                )

            pattern_str = PATTERNS[key]['pattern']
            try:
                engine = RegexEngine(pattern_str)
                cls._cache[key] = engine
                return engine
            except (SyntaxError, ValueError) as exc:
                raise ValueError(
                    f"Patrón '{key}' tiene sintaxis inválida: {exc}"
                ) from exc

    @classmethod
    def get_custom(cls, pattern: str, key: Optional[str] = None) -> RegexEngine:
        """
        Compila y cachea un patrón ad-hoc no definido en PATTERNS.

        Útil para patrones dinámicos ingresados por el usuario.

        Args:
            pattern (str): Expresión regular a compilar.
            key (str, optional): Clave de caché. Si es None, usa el propio
                                 patrón como clave (apropiado para patrones cortos).

        Returns:
            RegexEngine: Motor compilado.

        Raises:
            ValueError: Si el patrón tiene sintaxis inválida.
        """
        cache_key = f"__custom__{key or pattern}"

        if cache_key in cls._cache:
            return cls._cache[cache_key]

        with cls._lock:
            if cache_key in cls._cache:
                return cls._cache[cache_key]

            try:
                engine = RegexEngine(pattern)
                cls._cache[cache_key] = engine
                return engine
            except (SyntaxError, ValueError) as exc:
                raise ValueError(
                    f"Patrón inválido '{pattern}': {exc}"
                ) from exc

    @classmethod
    def precompile_all(cls) -> Dict[str, bool]:
        """
        Precompila todos los patrones registrados en PATTERNS.

        Útil para llamar al inicio de la aplicación y detectar errores
        de sintaxis temprano, en lugar de en tiempo de uso.

        Returns:
            dict: { key → True si compiló OK, False si falló }

        Ejemplo:
            results = EngineManager.precompile_all()
            failed = [k for k, ok in results.items() if not ok]
            if failed:
                print(f"Patrones con error: {failed}")
        """
        results = {}
        for key in PATTERNS:
            try:
                cls.get(key)
                results[key] = True
            except (KeyError, ValueError) as exc:
                print(f"[EngineManager] ✗ Error en '{key}': {exc}")
                results[key] = False
        return results

    @classmethod
    def status(cls) -> str:
        """
        Retorna un resumen del estado actual de la caché.

        Returns:
            str: Reporte legible con motores compilados y pendientes.
        """
        compiled   = [k for k in cls._cache if not k.startswith('__custom__')]
        custom     = [k for k in cls._cache if k.startswith('__custom__')]
        pending    = [k for k in PATTERNS if k not in cls._cache]

        lines = [
            "─── EngineManager Status ───────────────────────",
            f"  Compilados ({len(compiled)}): {', '.join(compiled) or 'ninguno'}",
            f"  Custom    ({len(custom)}): {len(custom)} patrones ad-hoc",
            f"  Pendientes({len(pending)}): {', '.join(pending) or 'ninguno'}",
            "────────────────────────────────────────────────",
        ]
        return "\n".join(lines)

    @classmethod
    def clear(cls, key: Optional[str] = None) -> None:
        """
        Limpia la caché de motores compilados.

        Args:
            key (str, optional): Si se indica, solo elimina ese motor.
                                 Si es None, limpia toda la caché.

        Uso típico: en pruebas unitarias, para garantizar estado limpio.
        """
        with cls._lock:
            if key is not None:
                cls._cache.pop(key, None)
            else:
                cls._cache.clear()