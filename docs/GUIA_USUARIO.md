# Guía de usuario — Lumen TLF

## Requisitos

- Python 3.10 o superior
- Tkinter (incluido con Python en Windows)

## Inicio rápido

```bash
# Desde la raíz del repositorio
python run_gui.py

# O desde proyecto_patrones/
cd proyecto_patrones
python main.py
```

## Navegación

| Sección | Función |
|---------|---------|
| **Escáner de Textos** | Detectar patrones en documentos o texto pegado |
| **Validador Interactivo** | Formulario con validación en tiempo real |
| **Catálogo de Patrones** | Consultar regex y ejemplos |

## Escáner de textos

1. En **Filtros de Patrón**, marque los tipos a buscar.
2. Use **Seleccionar todos** / **Ninguno** para gestionar filtros rápidamente.
3. Pegue texto o pulse **Cargar Archivo** (`.txt`).
4. Pulse **Analizar Texto**.
5. Revise **Resultados del Análisis** y el pie `// Total matches found...`.
6. Opcional: **Exportar Reporte** guarda un `.txt`.

## Validador interactivo

1. Complete los campos; cada uno muestra ✓ o ✕ al escribir.
2. La barra **PROGRESO DE VALIDACIÓN** indica cuántos campos obligatorios son válidos.
3. **Enviar Formulario** se activa solo con 7/7 obligatorios correctos.
4. **Mostrar/Ocultar** controla la visibilidad de la contraseña.

## Catálogo

- Busque patrones por nombre.
- Clic en una tarjeta: detalle completo.
- **Exportar Todo**: JSON o Markdown.
- **+ Crear Patrón**: prueba una regex personalizada.

## Pruebas automáticas (evidencia técnica)

```bash
cd proyecto_patrones
python main.py --tests
python main.py --export-tabla
```

## Soporte

Menú lateral → **Documentation** o **Support** dentro de la aplicación.
