# Tabla de casos de prueba

Proyecto: Busqueda y validacion de patrones — TLF

| Modulo | Caso | Entrada | Resultado esperado | Resultado |
|--------|------|---------|-------------------|-----------|
| Escanner (Correo Electrónico) | Valido | `usuario@ejemplo.com` | Aceptar | EXITOSO |
| Escanner (Correo Electrónico) | Valido | `nombre.apellido@empresa.co` | Aceptar | EXITOSO |
| Escanner (Correo Electrónico) | Invalido | `@sinusuario.com` | Rechazar | EXITOSO |
| Escanner (Correo Electrónico) | Invalido | `sin_arroba.com` | Rechazar | EXITOSO |
| Escanner (Teléfono Colombiano) | Valido | `3001234567` | Aceptar | EXITOSO |
| Escanner (Teléfono Colombiano) | Valido | `300 123 4567` | Aceptar | EXITOSO |
| Escanner (Teléfono Colombiano) | Invalido | `123456` | Rechazar | EXITOSO |
| Escanner (Teléfono Colombiano) | Invalido | `12345678901` | Rechazar | EXITOSO |
| Escanner (Fecha) | Valido | `15/06/2023` | Aceptar | EXITOSO |
| Escanner (Fecha) | Valido | `01-12-1999` | Aceptar | EXITOSO |
| Escanner (Fecha) | Invalido | `32/01/2023` | Rechazar | EXITOSO |
| Escanner (Fecha) | Invalido | `00/13/2023` | Rechazar | EXITOSO |
| Escanner (Fecha ISO 8601) | Valido | `2023-06-15` | Aceptar | EXITOSO |
| Escanner (Fecha ISO 8601) | Valido | `1999-12-31` | Aceptar | EXITOSO |
| Escanner (Fecha ISO 8601) | Invalido | `23-06-15` | Rechazar | EXITOSO |
| Escanner (Fecha ISO 8601) | Invalido | `2023-13-01` | Rechazar | EXITOSO |
| Escanner (URL / Dirección Web) | Valido | `https://www.google.com` | Aceptar | EXITOSO |
| Escanner (URL / Dirección Web) | Valido | `http://ejemplo.co/ruta` | Aceptar | EXITOSO |
| Escanner (URL / Dirección Web) | Invalido | `www.google.com` | Rechazar | EXITOSO |
| Escanner (URL / Dirección Web) | Invalido | `ftp:/dominio.com` | Rechazar | EXITOSO |
| Escanner (Placa Vehicular Colombiana) | Valido | `ABC123` | Aceptar | EXITOSO |
| Escanner (Placa Vehicular Colombiana) | Valido | `XYZ-456` | Aceptar | EXITOSO |
| Escanner (Placa Vehicular Colombiana) | Invalido | `AB123` | Rechazar | EXITOSO |
| Escanner (Placa Vehicular Colombiana) | Invalido | `ABCD123` | Rechazar | EXITOSO |
| Escanner (Cédula de Ciudadanía) | Valido | `123456` | Aceptar | EXITOSO |
| Escanner (Cédula de Ciudadanía) | Valido | `1234567890` | Aceptar | EXITOSO |
| Escanner (Cédula de Ciudadanía) | Invalido | `12345` | Rechazar | EXITOSO |
| Escanner (Cédula de Ciudadanía) | Invalido | `12345678901` | Rechazar | EXITOSO |
| Escanner (Código Postal) | Valido | `110111` | Aceptar | EXITOSO |
| Escanner (Código Postal) | Valido | `050001` | Aceptar | EXITOSO |
| Escanner (Código Postal) | Invalido | `11011` | Rechazar | EXITOSO |
| Escanner (Código Postal) | Invalido | `1100111` | Rechazar | EXITOSO |
| Escanner (Dirección IPv4) | Valido | `192.168.1.1` | Aceptar | EXITOSO |
| Escanner (Dirección IPv4) | Valido | `10.0.0.1` | Aceptar | EXITOSO |
| Escanner (Dirección IPv4) | Invalido | `256.1.1.1` | Rechazar | EXITOSO |
| Escanner (Dirección IPv4) | Invalido | `192.168.1` | Rechazar | EXITOSO |
| Escanner (Hora) | Valido | `08:30` | Aceptar | EXITOSO |
| Escanner (Hora) | Valido | `23:59:59` | Aceptar | EXITOSO |
| Escanner (Hora) | Invalido | `25:00` | Rechazar | EXITOSO |
| Escanner (Hora) | Invalido | `08:60` | Rechazar | EXITOSO |
| Escanner (Hashtag) | Valido | `#Python` | Aceptar | EXITOSO |
| Escanner (Hashtag) | Valido | `#IA2024` | Aceptar | EXITOSO |
| Escanner (Hashtag) | Invalido | `#` | Rechazar | EXITOSO |
| Escanner (Hashtag) | Invalido | `#123inicio` | Rechazar | EXITOSO |
| Escanner (Número de Tarjeta de Crédito) | Valido | `4111111111111111` | Aceptar | EXITOSO |
| Escanner (Número de Tarjeta de Crédito) | Valido | `4111-1111-1111-1111` | Aceptar | EXITOSO |
| Escanner (Número de Tarjeta de Crédito) | Invalido | `411111111111111` | Rechazar | EXITOSO |
| Escanner (Número de Tarjeta de Crédito) | Invalido | `4111-111-1111-1111` | Rechazar | EXITOSO |
| Formulario | validar_email | `user@test.com` | Valido | EXITOSO |
| Formulario | validar_email | `mal-correo` | Invalido | EXITOSO |
| Formulario | validar_contrasena | `Segura1!` | Valido | EXITOSO |
| Formulario | validar_contrasena | `corta` | Invalido | EXITOSO |
| Formulario | Campo Nombre Completo | (ver suite tests) | Regla definida | PENDIENTE/manual |
| Formulario | Campo Nombre de Usuario | (ver suite tests) | Regla definida | PENDIENTE/manual |
| Formulario | Campo Correo Electrónico | (ver suite tests) | Regla definida | PENDIENTE/manual |
| Formulario | Campo Contraseña | (ver suite tests) | Regla definida | PENDIENTE/manual |
| Formulario | Campo Teléfono Colombiano | (ver suite tests) | Regla definida | PENDIENTE/manual |
| Formulario | Campo Cédula de Ciudadanía | (ver suite tests) | Regla definida | PENDIENTE/manual |
| Formulario | Campo Fecha de Nacimiento | (ver suite tests) | Regla definida | PENDIENTE/manual |
| Formulario | Campo Sitio Web (opcional) | (ver suite tests) | Regla definida | PENDIENTE/manual |
