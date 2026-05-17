# TLF — Búsqueda y validación de patrones

Aplicación académica para **Teoría de Lenguajes Formales**: detección de patrones en textos con un **motor de expresiones regulares propio** (sin `import re`) y **validación interactiva** en formularios.

## Estructura del proyecto

```
TLF-Proyecto/
├── run_gui.py                 # Lanzar interfaz gráfica
├── docs/                      # Entregables documentales
│   ├── DOCUMENTO_PROYECTO.md
│   ├── GUIA_USUARIO.md
│   ├── MATRIZ_RUBRICA.md
│   └── TABLA_CASOS_PRUEBA.md  # Generada con --export-tabla
└── proyecto_patrones/
    ├── main.py                # GUI | --tests | --export-tabla
    ├── validators.py          # Etapa B: reglas del formulario
    ├── core/                  # Lexer, Parser, NFA, DFA, RegexEngine
    ├── patterns/              # Definición de patrones del dominio
    ├── text_scanner/          # Escáner de texto libre
    ├── ui/                    # Interfaz (Tkinter)
    └── tests/                 # Casos de prueba automatizados
```

## Comandos

```bash
# Interfaz gráfica
python run_gui.py

# Ejecutar todas las pruebas
cd proyecto_patrones
python main.py --tests

# Generar tabla de casos de prueba
python main.py --export-tabla
```

## Pipeline del motor regex

`Cadena regex → Lexer → Parser → NFA (Thompson) → DFA → match / search`

Ver documentación completa en [`docs/DOCUMENTO_PROYECTO.md`](docs/DOCUMENTO_PROYECTO.md).
