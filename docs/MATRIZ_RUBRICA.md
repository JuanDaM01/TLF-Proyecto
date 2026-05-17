# Matriz de cumplimiento — Rúbrica del proyecto

| Criterio | Peso | Evidencia en el repositorio | Estado |
|----------|------|-----------------------------|--------|
| 1. Análisis de requerimientos y diseño | 15% | `docs/DOCUMENTO_PROYECTO.md`, arquitectura en `core/`, patrones en `patterns/definitions.py` | Cumple |
| 2. Búsqueda de patrones (sin `re`) | 20% | `core/regex_engine.py`, `text_scanner/scanner.py`, pestaña Escáner en `ui/app.py` | Cumple |
| 3. Validación en sistemas interactivos | 20% | `validators.py`, pestaña Validador, feedback en tiempo real | Cumple |
| 4. Pruebas y casos de uso | 15% | `tests/test_cases.py`, `docs/TABLA_CASOS_PRUEBA.md` | Cumple |
| 5. Documentación técnica y guía | 15% | `docs/GUIA_USUARIO.md`, ayuda en app, comentarios en `core/` | Cumple |
| 6. Organización del código | 10% | Capas: `core/`, `patterns/`, `text_scanner/`, `ui/`, `validators.py` | Cumple |
| 7. Sustentación | 5% | Demo GUI + salida de `python main.py --tests` | Pendiente usuario |

## Etapa A — Patrones requeridos

| Patrón solicitado | Implementado |
|-------------------|--------------|
| Correos electrónicos | Sí (`email`) |
| Números telefónicos | Sí (`telefono_co`) |
| Fechas | Sí (`fecha`, `fecha_iso`) |
| Identificadores / documento | Sí (`cedula_co`) |
| URL | Sí (`url`) |
| Placas vehiculares | Sí (`placa_co`) |
| Otros pertinentes | IPv4, hora, hashtag, tarjeta, código postal |

## Etapa B — Validaciones del formulario

| Validación | Implementado |
|------------|--------------|
| Estructura de correo | Sí (`validar_email`) |
| Contraseña segura | Sí (`validar_contrasena`, reglas compuestas) |
| Teléfono | Sí (`validar_telefono`) |
| Fecha | Sí (`validar_fecha`) |
| Usuario / identificadores | Sí (`validar_usuario`, `validar_cedula`, `validar_nombre`) |

## Evidencias sugeridas para entrega

1. Capturas: Escáner con análisis, Validador con campos válidos/inválidos, Catálogo.
2. Archivo exportado: `reporte_patrones.txt`.
3. Consola: salida de `python main.py --tests`.
4. Tabla: `docs/TABLA_CASOS_PRUEBA.md`.
