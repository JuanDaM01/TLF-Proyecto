from __future__ import annotations
from typing import Dict, Optional
import threading

from .regex_engine import RegexEngine
from patterns.definitions import PATTERNS


class EngineManager:
    """Cache de RegexEngine por clave; compilacion lazy y thread-safe basica."""

    _cache: Dict[str, RegexEngine] = {}
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def get(cls, key: str) -> RegexEngine:
        """Motor del patron en PATTERNS. KeyError o ValueError si falla."""
        if key in cls._cache:
            return cls._cache[key]

        with cls._lock:
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
        """Compila y cachea un patron ad-hoc."""
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
        """Precompila todos los patrones de PATTERNS; devuelve exito por clave."""
        results = {}
        for key in PATTERNS:
            try:
                cls.get(key)
                results[key] = True
            except (KeyError, ValueError) as exc:
                print(f"[EngineManager] Error en '{key}': {exc}")
                results[key] = False
        return results

    @classmethod
    def status(cls) -> str:
        """Resumen de motores compilados y pendientes."""
        compiled = [k for k in cls._cache if not k.startswith('__custom__')]
        custom = [k for k in cls._cache if k.startswith('__custom__')]
        pending = [k for k in PATTERNS if k not in cls._cache]

        lines = [
            "--- EngineManager Status ---",
            f"  Compilados ({len(compiled)}): {', '.join(compiled) or 'ninguno'}",
            f"  Custom    ({len(custom)}): {len(custom)} patrones ad-hoc",
            f"  Pendientes({len(pending)}): {', '.join(pending) or 'ninguno'}",
            "----------------------------",
        ]
        return "\n".join(lines)

    @classmethod
    def clear(cls, key: Optional[str] = None) -> None:
        """Limpia la cache (toda o una clave)."""
        with cls._lock:
            if key is not None:
                cls._cache.pop(key, None)
            else:
                cls._cache.clear()
