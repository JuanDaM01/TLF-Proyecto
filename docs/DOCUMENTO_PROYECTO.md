# Proyecto: Búsqueda y validación de patrones en textos y sistemas interactivos

**Asignatura:** Teoría de Lenguajes Formales (TLF)  
**Tecnologías:** Python 3 · Tkinter · Motor regex propio (sin `import re`)

---

## 1. Objetivo general

Desarrollar una aplicación que detecte y valide patrones en textos mediante expresiones regulares y autómatas, y que verifique entradas en formularios interactivos según criterios sintácticos predefinidos.

## 2. Resultados de aprendizaje atendidos

| R.A. | Cómo se evidencia en el proyecto |
|------|----------------------------------|
| **R.A.1** Análisis léxico y sintáctico | Pipeline `Lexer → Parser → AST → NFA (Thompson) → DFA → match/search` en `core/` |
| **R.A.2** Teoría de lenguajes formales | Diseño de patrones, autómatas y validación estructurada en `patterns/` y `validators.py` |
| **R.A.3** Interacción humano-computador | Interfaz gráfica con validación en tiempo real, mensajes de error y flujo guiado en `ui/` |

## 3. Descripción de la solución

### Etapa A — Búsqueda y validación en textos

- Carga o escritura de texto libre.
- Selección de patrones (correo, teléfono, fecha, URL, cédula, placa, IPv4, hashtag, etc.).
- Extracción y reporte de coincidencias con contexto y posición.
- Exportación del reporte a archivo `.txt`.

**Módulos:** `text_scanner/scanner.py`, `patterns/definitions.py`, `core/regex_engine.py`

### Etapa B — Validación en sistemas interactivos

- Formulario con 8 campos y validación en tiempo real.
- Indicadores visuales (válido / inválido / neutro).
- Barra de progreso; envío habilitado solo si los obligatorios son correctos.
- Contraseña con reglas compuestas (longitud, mayúsculas, dígitos, especiales).

**Módulos:** `validators.py`, `ui/app.py` (pestaña Validador)

## 4. Fases del proyecto

| Fase | Entregable en repositorio |
|------|---------------------------|
| 1. Análisis y diseño | `docs/DOCUMENTO_PROYECTO.md`, `docs/MATRIZ_RUBRICA.md` |
| 2. Diseño técnico | `patterns/definitions.py`, diagrama de pipeline en sección 5 |
| 3. Implementación | `core/`, `ui/`, `validators.py`, `text_scanner/` |
| 4. Pruebas | `tests/test_cases.py`, `docs/TABLA_CASOS_PRUEBA.md` |
| 5. Documentación | `docs/GUIA_USUARIO.md`, ayuda integrada en la app |

## 5. Arquitectura técnica (sin librería `re`)

```
Expresión regular (str)
        │
        ▼
   Lexer (tokens)
        │
        ▼
   Parser (AST)
        │
        ▼
   ThompsonBuilder (NFA)
        │
        ▼
   SubsetConstructor (DFA)
        │
        ▼
   match() / search()
```

**Restricción cumplida:** no se usa `import re` ni `regex` de terceros para el motor principal.

## 6. Patrones implementados

| Clave | Descripción |
|-------|-------------|
| `email` | Correo electrónico |
| `telefono_co` | Teléfono colombiano |
| `fecha` / `fecha_iso` | Fechas DD/MM/AAAA e ISO |
| `url` | URL http/https/ftp |
| `cedula_co` | Cédula 6–10 dígitos |
| `placa_co` | Placa vehicular CO |
| `ipv4` | Dirección IPv4 |
| `hora` | Hora HH:MM |
| `hashtag` | Hashtag redes sociales |
| `tarjeta_credito` | 16 dígitos agrupados |
| `codigo_postal` | Código postal 6 dígitos |

## 7. Conclusiones

El proyecto integra fundamentos de lenguajes formales con una aplicación usable: el motor propio demuestra el pipeline léxico-sintáctico-automata, y la interfaz materializa la validación interactiva exigida en la Etapa B. Las pruebas automatizadas y la tabla de casos permiten verificar comportamiento ante entradas válidas e inválidas.

---

*Documento base para entrega académica. Complementar con portada institucional y nombres del equipo.*
