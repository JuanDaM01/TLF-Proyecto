from validators import *
# =============================================================================
# ui/app.py
# Aplicación principal Tkinter
# Integra las dos pestañas: Escáner de Textos y Validador Interactivo
# =============================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.regex_engine import RegexEngine
from text_scanner.scanner import TextScanner
from patterns.definitions import PATTERNS
from core.engine_manager import EngineManager


# ===========================================================================
# VALIDADORES PARA EL FORMULARIO INTERACTIVO
# Cada función retorna (True, "") si válido, o (False, "mensaje_error")
# ===========================================================================


def validar_email(texto: str) -> tuple[bool, str]:
    """
    Valida el formato de un correo electrónico.
    Usa el motor compilado del EngineManager (sin recompilar).
    """
    texto = texto.strip()
    if not texto:
        return False, "El correo no puede estar vacío"
    try:
        engine = EngineManager.get('email')
        if engine.match(texto):
            return True, ""
        return False, "Formato inválido. Ej: usuario@dominio.com"
    except (KeyError, ValueError) as exc:
        return False, f"Error en validador de email: {exc}"


def validar_telefono(texto: str) -> tuple[bool, str]:
    """
    Valida un número telefónico colombiano (celular o fijo).
    """
    texto = texto.strip()
    if not texto:
        return False, "El teléfono no puede estar vacío"
    try:
        engine = EngineManager.get('telefono_co')
        if engine.match(texto):
            return True, ""
        return False, "Formato inválido. Ej: 3001234567 o +57 310 555 9999"
    except (KeyError, ValueError) as exc:
        return False, f"Error en validador de teléfono: {exc}"


def validar_fecha(texto: str) -> tuple[bool, str]:
    """
    Valida una fecha en formato DD/MM/AAAA, DD-MM-AAAA o DD.MM.AAAA.
    """
    texto = texto.strip()
    if not texto:
        return False, "La fecha no puede estar vacía"
    try:
        engine = EngineManager.get('fecha')
        if engine.match(texto):
            return True, ""
        return False, "Formato inválido. Use DD/MM/AAAA (Ej: 25/12/1990)"
    except (KeyError, ValueError) as exc:
        return False, f"Error en validador de fecha: {exc}"


def validar_cedula(texto: str) -> tuple[bool, str]:
    """
    Valida una cédula de ciudadanía colombiana (6 a 10 dígitos).
    """
    texto = texto.strip()
    if not texto:
        return False, "La cédula no puede estar vacía"
    try:
        engine = EngineManager.get('cedula_co')
        if engine.match(texto):
            return True, ""
        return False, "Debe tener entre 6 y 10 dígitos, sin separadores"
    except (KeyError, ValueError) as exc:
        return False, f"Error en validador de cédula: {exc}"


def validar_url(texto: str) -> tuple[bool, str]:
    """
    Valida una URL con esquema http, https o ftp.
    """
    texto = texto.strip()
    if not texto:
        return True, ""  # URL es campo opcional en el formulario
    try:
        engine = EngineManager.get('url')
        if engine.match(texto):
            return True, ""
        return False, "URL inválida. Debe iniciar con http://, https:// o ftp://"
    except (KeyError, ValueError) as exc:
        return False, f"Error en validador de URL: {exc}"


def validar_usuario(texto: str) -> tuple[bool, str]:
    """
    Valida nombre de usuario: 4-20 chars, letras/dígitos/guión bajo,
    debe iniciar con letra.
    """
    texto = texto.strip()
    if not texto:
        return False, "El usuario no puede estar vacío"
    if len(texto) < 4:
        return False, "Mínimo 4 caracteres"
    if len(texto) > 20:
        return False, "Máximo 20 caracteres"
    try:
        engine = EngineManager.get_custom(r'[a-zA-Z][a-zA-Z0-9_]+', key='usuario')
        if engine.match(texto):
            return True, ""
        return False, "Solo letras, dígitos y _, debe iniciar con letra"
    except ValueError as exc:
        return False, f"Error en validador de usuario: {exc}"


def validar_contrasena(texto: str) -> tuple[bool, str]:
    """
    Valida contraseña segura. Requisitos:
      - Mínimo 8 caracteres
      - Al menos una mayúscula
      - Al menos una minúscula
      - Al menos un dígito
      - Al menos un carácter especial: @#$%^&*()_+!

    Nota: Esta validación NO usa regex porque las restricciones son
    acumulativas (AND entre condiciones), no un patrón único.
    Una regex que valide todos los requisitos a la vez sería ilegible.
    La validación manual es más clara y mantenible aquí.
    """
    if not texto:
        return False, "La contraseña no puede estar vacía"
    if len(texto) < 8:
        return False, "Mínimo 8 caracteres"

    tiene_may = any(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in texto)
    tiene_min = any(c in 'abcdefghijklmnopqrstuvwxyz' for c in texto)
    tiene_dig = any(c in '0123456789' for c in texto)
    tiene_esp = any(c in '@#$%^&*()_+!' for c in texto)

    faltantes = []
    if not tiene_may: faltantes.append("mayúscula")
    if not tiene_min: faltantes.append("minúscula")
    if not tiene_dig: faltantes.append("dígito")
    if not tiene_esp: faltantes.append("especial (@#$%^&*)")

    if faltantes:
        return False, f"Falta: {', '.join(faltantes)}"
    return True, ""


# ===========================================================================
# COLORES DEL TEMA
# ===========================================================================
COLORS = {
    'bg_dark':     '#1e1e2e',   # Fondo principal (oscuro morado)
    'bg_panel':    '#2a2a3e',   # Panel secundario
    'bg_input':    '#313149',   # Fondo de campos de entrada
    'accent':      '#7c6af7',   # Acento morado
    'accent_2':    '#56d6a0',   # Acento verde (éxito)
    'danger':      '#f87171',   # Rojo (error)
    'warning':     '#fbbf24',   # Amarillo (advertencia)
    'text_main':   '#e2e8f0',   # Texto principal
    'text_muted':  '#94a3b8',   # Texto secundario
    'border':      '#3d3d5c',   # Bordes
}


# ===========================================================================
# CLASE PRINCIPAL DE LA APLICACIÓN
# ===========================================================================

class PatternApp(tk.Tk):
    """
    Aplicación principal del sistema de detección y validación de patrones.
    Hereda de tk.Tk para ser la ventana raíz.
    """

    def __init__(self):
        super().__init__()
        self.title("🔍 Sistema de Patrones — Análisis Léxico y Sintáctico")
        self.geometry("1024x768")
        self.minsize(800, 600)
        self.configure(bg=COLORS['bg_dark'])

        self._apply_styles()
        self._build_ui()

    def _apply_styles(self):
        """Aplica los estilos globales de la aplicación."""
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('TNotebook',
                         background=COLORS['bg_dark'],
                         borderwidth=0)
        style.configure('TNotebook.Tab',
                         background=COLORS['bg_panel'],
                         foreground=COLORS['text_muted'],
                         padding=[18, 8],
                         font=('Consolas', 10, 'bold'))
        style.map('TNotebook.Tab',
                  background=[('selected', COLORS['accent'])],
                  foreground=[('selected', '#ffffff')])

        style.configure('TFrame',
                         background=COLORS['bg_dark'])
        style.configure('TLabel',
                         background=COLORS['bg_dark'],
                         foreground=COLORS['text_main'],
                         font=('Consolas', 10))
        style.configure('TButton',
                         background=COLORS['accent'],
                         foreground='#ffffff',
                         font=('Consolas', 10, 'bold'),
                         padding=[12, 6],
                         borderwidth=0)
        style.map('TButton',
                  background=[('active', '#6357d9')])
        style.configure('Success.TLabel',
                         foreground=COLORS['accent_2'],
                         background=COLORS['bg_dark'],
                         font=('Consolas', 9))
        style.configure('Error.TLabel',
                         foreground=COLORS['danger'],
                         background=COLORS['bg_dark'],
                         font=('Consolas', 9))

    def _build_ui(self):
        """Construye la interfaz principal con pestañas."""
        # Encabezado
        header = tk.Frame(self, bg=COLORS['bg_panel'], pady=12)
        header.pack(fill='x')

        tk.Label(
            header,
            text="  🔍 Sistema de Búsqueda y Validación de Patrones",
            bg=COLORS['bg_panel'],
            fg=COLORS['accent'],
            font=('Consolas', 14, 'bold')
        ).pack(side='left', padx=16)

        tk.Label(
            header,
            text="Teoría de Lenguajes Formales — Motor Regex Propio  ",
            bg=COLORS['bg_panel'],
            fg=COLORS['text_muted'],
            font=('Consolas', 9)
        ).pack(side='right', padx=16)

        # Notebook (pestañas)
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Pestaña 1: Escáner de Textos
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="📄  Escáner de Textos")
        ScannerTab(tab1).pack(fill='both', expand=True)

        # Pestaña 2: Validador de Formulario
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="📝  Validador Interactivo")
        ValidatorTab(tab2).pack(fill='both', expand=True)

        # Pestaña 3: Tabla de Patrones
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="📊  Catálogo de Patrones")
        CatalogTab(tab3).pack(fill='both', expand=True)


# ===========================================================================
# PESTAÑA 1: ESCÁNER DE TEXTOS
# ===========================================================================

class ScannerTab(tk.Frame):
    """
    Pestaña de búsqueda de patrones en texto libre.
    
    Funcionalidades:
    - Ingresar texto manualmente o cargar desde archivo .txt
    - Seleccionar qué patrones buscar
    - Mostrar resultados con contexto y posición
    - Exportar reporte
    """

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_dark'])
        self._build()

    def _build(self):
        # --- Panel izquierdo: controles ---
        left = tk.Frame(self, bg=COLORS['bg_panel'], width=220)
        left.pack(side='left', fill='y', padx=(5,0), pady=5)
        left.pack_propagate(False)

        tk.Label(left, text="PATRONES A BUSCAR",
                 bg=COLORS['bg_panel'], fg=COLORS['accent'],
                 font=('Consolas', 9, 'bold')).pack(pady=(12,4), padx=8)

        # Checkboxes para seleccionar patrones
        self._pattern_vars = {}
        for key, info in PATTERNS.items():
            var = tk.BooleanVar(value=True)
            self._pattern_vars[key] = var
            cb = tk.Checkbutton(
                left, text=info['name'], variable=var,
                bg=COLORS['bg_panel'], fg=COLORS['text_main'],
                selectcolor=COLORS['bg_input'],
                activebackground=COLORS['bg_panel'],
                font=('Consolas', 8),
                anchor='w'
            )
            cb.pack(fill='x', padx=10, pady=1)

        ttk.Separator(left, orient='horizontal').pack(fill='x', pady=8, padx=8)

        ttk.Button(left, text="✅ Marcar todos",
                   command=lambda: [v.set(True) for v in self._pattern_vars.values()]
                   ).pack(fill='x', padx=8, pady=2)
        ttk.Button(left, text="❌ Desmarcar todos",
                   command=lambda: [v.set(False) for v in self._pattern_vars.values()]
                   ).pack(fill='x', padx=8, pady=2)

        ttk.Separator(left, orient='horizontal').pack(fill='x', pady=8, padx=8)

        ttk.Button(left, text="📂 Cargar archivo .txt",
                   command=self._load_file).pack(fill='x', padx=8, pady=2)
        ttk.Button(left, text="🔍 ANALIZAR TEXTO",
                   command=self._analyze).pack(fill='x', padx=8, pady=(8,2))
        ttk.Button(left, text="🗑 Limpiar",
                   command=self._clear).pack(fill='x', padx=8, pady=2)

        # Estadísticas
        self._stats_label = tk.Label(
            left, text="", bg=COLORS['bg_panel'],
            fg=COLORS['accent_2'], font=('Consolas', 8),
            wraplength=190, justify='left'
        )
        self._stats_label.pack(padx=8, pady=8)

        # --- Panel central: texto de entrada ---
        center = tk.Frame(self, bg=COLORS['bg_dark'])
        center.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        tk.Label(center, text="TEXTO A ANALIZAR:",
                 bg=COLORS['bg_dark'], fg=COLORS['text_muted'],
                 font=('Consolas', 9, 'bold')).pack(anchor='w', padx=4)

        self._input_text = scrolledtext.ScrolledText(
            center,
            bg=COLORS['bg_input'], fg=COLORS['text_main'],
            insertbackground=COLORS['accent'],
            font=('Consolas', 10),
            relief='flat', borderwidth=0,
            height=12
        )
        self._input_text.pack(fill='both', expand=True, pady=(2,4))

        # Texto de ejemplo
        ejemplo = (
            "Contacte a juan.perez@empresa.com o soporte@tech.org para más info.\n"
            "Teléfonos: 3201234567 y +57 310 987 6543. Fijo: 601-5551234.\n"
            "Sitio web: https://www.mipagina.com/productos?ref=home\n"
            "Fecha de nacimiento: 15/08/1995. Cédula: 1234567890.\n"
            "Placa del vehículo: ABC-123. Moto: DEF78G.\n"
            "Servidor interno: 192.168.0.100. Backup: http://ftp.empresa.net\n"
            "Horario de atención: 08:00 AM a 06:00 PM.\n"
            "Síguenos en #ServicioAlCliente #Tecnología2024 #InnovaciónCO"
        )
        self._input_text.insert('1.0', ejemplo)

        # Resultados
        tk.Label(center, text="RESULTADOS:",
                 bg=COLORS['bg_dark'], fg=COLORS['text_muted'],
                 font=('Consolas', 9, 'bold')).pack(anchor='w', padx=4)

        self._output_text = scrolledtext.ScrolledText(
            center,
            bg='#0d0d1a', fg=COLORS['accent_2'],
            font=('Consolas', 9),
            relief='flat', borderwidth=0,
            height=15,
            state='disabled'
        )
        self._output_text.pack(fill='both', expand=True, pady=(2,0))

    def _load_file(self):
        """Abre un diálogo para cargar un archivo de texto."""
        path = filedialog.askopenfilename(
            title="Seleccionar archivo de texto",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos", "*.*")]
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                self._input_text.delete('1.0', 'end')
                self._input_text.insert('1.0', contenido)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

    def _analyze(self):
        """Ejecuta el análisis y muestra el reporte."""
        text = self._input_text.get('1.0', 'end').strip()
        if not text:
            messagebox.showwarning("Aviso", "Por favor ingrese texto para analizar.")
            return

        # Obtener patrones seleccionados
        selected = [k for k, v in self._pattern_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("Aviso", "Seleccione al menos un patrón.")
            return

        try:
            scanner          = TextScanner(selected_patterns=selected)
            results, report  = scanner.scan_and_report(text)

            # Actualizar estadísticas
            total = sum(len(v) for v in results.values())
            tipos = len(results)
            self._stats_label.config(
                text=f"✔ Análisis completado\n"
                     f"Coincidencias: {total}\n"
                     f"Tipos hallados: {tipos}/{len(selected)}"
            )

            # Mostrar reporte
            self._output_text.config(state='normal')
            self._output_text.delete('1.0', 'end')
            self._output_text.insert('1.0', report)
            self._output_text.config(state='disabled')

        except Exception as e:
            messagebox.showerror("Error en análisis", str(e))

    def _clear(self):
        """Limpia ambos campos de texto."""
        self._input_text.delete('1.0', 'end')
        self._output_text.config(state='normal')
        self._output_text.delete('1.0', 'end')
        self._output_text.config(state='disabled')
        self._stats_label.config(text="")


# ===========================================================================
# PESTAÑA 2: VALIDADOR INTERACTIVO (Formulario)
# ===========================================================================

class ValidatorTab(tk.Frame):
    """
    Pestaña de validación de formulario interactivo.
    
    Cada campo tiene:
    - Etiqueta con nombre y requisitos
    - Campo de entrada con detección de cambios en tiempo real
    - Indicador visual (✅ / ❌) actualizado inmediatamente
    - Mensaje de error descriptivo
    
    El formulario solo puede enviarse cuando TODOS los campos son válidos.
    """

    FIELDS = [
        ('nombre',     'Nombre completo',         validar_nombre,    'Ej: María García López'),
        ('usuario',    'Nombre de usuario',        validar_usuario,   'Ej: user_123  (4-20 chars)'),
        ('email',      'Correo electrónico',       validar_email,     'Ej: usuario@dominio.com'),
        ('password',   'Contraseña',               validar_contrasena,'Min 8 chars, mayús, dígito, especial'),
        ('telefono',   'Teléfono colombiano',      validar_telefono,  'Ej: 3001234567 o +57 310 555 0000'),
        ('cedula',     'Cédula de ciudadanía',     validar_cedula,    'Ej: 1234567890 (6-10 dígitos)'),
        ('fecha_nac',  'Fecha de nacimiento',      validar_fecha,     'Ej: 25/12/1990 (DD/MM/AAAA)'),
        ('sitio_web',  'Sitio web (opcional)',     None,              'Ej: https://mipagina.com'),
    ]

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_dark'])
        self._entries    = {}
        self._indicators = {}
        self._messages   = {}
        self._build()

    def _build(self):
        # Contenedor con scroll
        canvas    = tk.Canvas(self, bg=COLORS['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        container = tk.Frame(canvas, bg=COLORS['bg_dark'])

        container.bind('<Configure>',
                       lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=container, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Título del formulario
        header_f = tk.Frame(container, bg=COLORS['bg_panel'])
        header_f.pack(fill='x', padx=20, pady=(15,5))

        tk.Label(
            header_f,
            text="  📝  FORMULARIO DE REGISTRO — VALIDACIÓN EN TIEMPO REAL",
            bg=COLORS['bg_panel'], fg=COLORS['accent'],
            font=('Consolas', 12, 'bold'), pady=10
        ).pack(fill='x')

        tk.Label(
            header_f,
            text="  Cada campo se valida automáticamente mientras escribe. "
                 "Todos los campos (excepto sitio web) son obligatorios.",
            bg=COLORS['bg_panel'], fg=COLORS['text_muted'],
            font=('Consolas', 9), pady=4
        ).pack(fill='x')

        # Construir cada campo del formulario
        form_frame = tk.Frame(container, bg=COLORS['bg_dark'])
        form_frame.pack(fill='x', padx=20, pady=10)

        for field_key, label_text, validator, placeholder in self.FIELDS:
            self._build_field(form_frame, field_key, label_text,
                              validator, placeholder)

        # Barra de progreso del formulario
        self._progress_label = tk.Label(
            container,
            text="Campos válidos: 0 / 7",
            bg=COLORS['bg_dark'], fg=COLORS['text_muted'],
            font=('Consolas', 9)
        )
        self._progress_label.pack(pady=(5,0))

        self._progress_bar = tk.Canvas(
            container, height=8, bg=COLORS['bg_panel'],
            highlightthickness=0
        )
        self._progress_bar.pack(fill='x', padx=20, pady=(2,10))

        # Botones de acción
        btn_frame = tk.Frame(container, bg=COLORS['bg_dark'])
        btn_frame.pack(pady=10)

        self._submit_btn = ttk.Button(
            btn_frame, text="✅  ENVIAR FORMULARIO",
            command=self._submit, state='disabled'
        )
        self._submit_btn.pack(side='left', padx=8)

        ttk.Button(
            btn_frame, text="🗑  LIMPIAR FORMULARIO",
            command=self._reset
        ).pack(side='left', padx=8)

        # Panel de resultado del envío
        self._result_label = tk.Label(
            container, text="",
            bg=COLORS['bg_dark'], fg=COLORS['accent_2'],
            font=('Consolas', 10, 'bold')
        )
        self._result_label.pack(pady=8)

    def _build_field(self, parent, key, label_text, validator, placeholder):
        """Construye un campo de formulario completo con validación."""
        row = tk.Frame(parent, bg=COLORS['bg_dark'])
        row.pack(fill='x', pady=5)

        # Etiqueta + indicador
        label_row = tk.Frame(row, bg=COLORS['bg_dark'])
        label_row.pack(fill='x')

        tk.Label(
            label_row, text=label_text,
            bg=COLORS['bg_dark'], fg=COLORS['text_main'],
            font=('Consolas', 10, 'bold'), width=26, anchor='w'
        ).pack(side='left')

        indicator = tk.Label(
            label_row, text="○",
            bg=COLORS['bg_dark'], fg=COLORS['text_muted'],
            font=('Consolas', 12)
        )
        indicator.pack(side='left', padx=4)
        self._indicators[key] = indicator

        # Campo de entrada
        entry_frame = tk.Frame(row, bg=COLORS['border'], pady=1)
        entry_frame.pack(fill='x', pady=2)

        is_password = (key == 'password')
        entry = tk.Entry(
            entry_frame,
            bg=COLORS['bg_input'], fg=COLORS['text_main'],
            insertbackground=COLORS['accent'],
            font=('Consolas', 10),
            relief='flat', borderwidth=6,
            show='●' if is_password else ''
        )
        entry.pack(fill='x')
        self._entries[key] = entry

        # Placeholder (hint)
        tk.Label(
            row, text=f"  {placeholder}",
            bg=COLORS['bg_dark'], fg=COLORS['text_muted'],
            font=('Consolas', 8)
        ).pack(anchor='w')

        # Mensaje de error/éxito
        msg_label = tk.Label(
            row, text="",
            bg=COLORS['bg_dark'], fg=COLORS['danger'],
            font=('Consolas', 8)
        )
        msg_label.pack(anchor='w')
        self._messages[key] = msg_label

        # Binding para validación en tiempo real
        if validator:
            entry.bind('<KeyRelease>',
                       lambda e, k=key, v=validator: self._validate_field(k, v))
            entry.bind('<FocusOut>',
                       lambda e, k=key, v=validator: self._validate_field(k, v))

    def _validate_field(self, key, validator):
        """
        Ejecuta la validación de un campo y actualiza los indicadores visuales.
        
        Args:
            key (str): Clave del campo.
            validator (callable): Función de validación.
        """
        value = self._entries[key].get()
        is_valid, message = validator(value)

        if not value.strip():
            # Campo vacío → estado neutro
            self._indicators[key].config(text="○", fg=COLORS['text_muted'])
            self._messages[key].config(text="")
        elif is_valid:
            self._indicators[key].config(text="✅", fg=COLORS['accent_2'])
            self._messages[key].config(text="✓ Válido", fg=COLORS['accent_2'])
        else:
            self._indicators[key].config(text="❌", fg=COLORS['danger'])
            self._messages[key].config(text=f"✗ {message}", fg=COLORS['danger'])

        self._update_progress()

    def _count_valid_fields(self):
        """Cuenta cuántos campos obligatorios son válidos."""
        mandatory = [
            (k, v) for k, label, v, _ in self.FIELDS
            if v is not None
        ]
        count = 0
        for key, validator in mandatory:
            val = self._entries[key].get()
            if val.strip():
                ok, _ = validator(val)
                if ok:
                    count += 1
        return count, len(mandatory)

    def _update_progress(self):
        """Actualiza la barra de progreso y el estado del botón enviar."""
        valid, total = self._count_valid_fields()
        self._progress_label.config(text=f"Campos válidos: {valid} / {total}")

        # Actualizar barra gráfica
        self._progress_bar.delete('all')
        width = self._progress_bar.winfo_width() or 600
        if total > 0:
            fill_w = int(width * valid / total)
            self._progress_bar.create_rectangle(
                0, 0, fill_w, 8,
                fill=COLORS['accent_2'] if valid == total else COLORS['accent'],
                outline=''
            )

        # Habilitar o deshabilitar el botón según completitud
        if valid == total:
            self._submit_btn.config(state='normal')
        else:
            self._submit_btn.config(state='disabled')

    def _submit(self):
        """Procesa el envío del formulario."""
        datos = {k: self._entries[k].get().strip() for k in self._entries}
        self._result_label.config(
            text=f"✅  ¡Formulario enviado correctamente!\n"
                 f"   Usuario registrado: {datos['nombre']} (@{datos['usuario']})",
            fg=COLORS['accent_2']
        )

    def _reset(self):
        """Limpia todos los campos del formulario."""
        for key in self._entries:
            self._entries[key].delete(0, 'end')
            self._indicators[key].config(text="○", fg=COLORS['text_muted'])
            self._messages[key].config(text="")
        self._result_label.config(text="")
        self._submit_btn.config(state='disabled')
        self._update_progress()


# ===========================================================================
# PESTAÑA 3: CATÁLOGO DE PATRONES
# ===========================================================================

class CatalogTab(tk.Frame):
    """
    Catálogo visual de todos los patrones disponibles con ejemplos
    válidos e inválidos, y la expresión regular subyacente.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_dark'])
        self._build()

    def _build(self):
        tk.Label(
            self,
            text="📊  CATÁLOGO DE PATRONES — Expresiones Regulares Implementadas",
            bg=COLORS['bg_dark'], fg=COLORS['accent'],
            font=('Consolas', 11, 'bold')
        ).pack(pady=10)

        # Frame con scroll
        canvas    = tk.Canvas(self, bg=COLORS['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        container = tk.Frame(canvas, bg=COLORS['bg_dark'])

        container.bind('<Configure>',
                       lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=container, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        for key, info in PATTERNS.items():
            self._build_pattern_card(container, info)

    def _build_pattern_card(self, parent, info):
        """Construye una tarjeta visual para un patrón."""
        card = tk.Frame(parent, bg=COLORS['bg_panel'],
                        relief='flat', padx=12, pady=10)
        card.pack(fill='x', padx=15, pady=5)

        # Nombre del patrón
        tk.Label(card, text=f"🔹 {info['name']}",
                 bg=COLORS['bg_panel'], fg=COLORS['accent'],
                 font=('Consolas', 11, 'bold')).pack(anchor='w')

        # Descripción
        tk.Label(card, text=f"   {info['description']}",
                 bg=COLORS['bg_panel'], fg=COLORS['text_muted'],
                 font=('Consolas', 9)).pack(anchor='w', pady=2)

        # Regex (truncada para visualización)
        pattern_display = info['pattern'][:80] + "..." \
                         if len(info['pattern']) > 80 else info['pattern']
        tk.Label(card, text=f"   Regex: {pattern_display}",
                 bg=COLORS['bg_panel'], fg='#a0c8ff',
                 font=('Courier', 8)).pack(anchor='w', pady=2)

        # Ejemplos válidos
        valid_str = "  |  ".join(info['valid_ex'][:3])
        tk.Label(card, text=f"   ✅ Válidos: {valid_str}",
                 bg=COLORS['bg_panel'], fg=COLORS['accent_2'],
                 font=('Consolas', 8)).pack(anchor='w')

        # Ejemplos inválidos
        invalid_str = "  |  ".join(info['invalid_ex'][:3])
        tk.Label(card, text=f"   ❌ Inválidos: {invalid_str}",
                 bg=COLORS['bg_panel'], fg=COLORS['danger'],
                 font=('Consolas', 8)).pack(anchor='w')

        ttk.Separator(card, orient='horizontal').pack(fill='x', pady=(8,0))