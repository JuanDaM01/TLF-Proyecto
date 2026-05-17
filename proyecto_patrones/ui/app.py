# =============================================================================
# ui/app.py — Lumen TLF · Interfaz profesional completa
# =============================================================================

from __future__ import annotations

import os
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine_manager import EngineManager
from patterns.definitions import PATTERNS
from text_scanner.scanner import TextScanner
from validators import FORM_FIELDS
from ui.services import (
    HELP_DOCUMENTATION,
    export_catalog_json,
    export_catalog_markdown,
    export_text_report,
)
from ui.style import (
    T,
    TypeScale,
    FieldBox,
    FilterToolbar,
    GlassButton,
    GradientBackground,
    HeroBanner,
    LinkLabel,
    LumenCard,
    PillBadge,
    ProgressBar,
    ResponsiveGrid,
    ScrollableChecks,
    ScrollableFrame,
    Sidebar,
    TealCheck,
    TopBar,
    apply_ttk_styles,
    init_fonts,
)


# ===========================================================================
# APLICACIÓN PRINCIPAL
# ===========================================================================

class PatternApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Lumen — Academic Analytics · TLF')
        self.geometry('1320x880')
        self.minsize(960, 620)
        self.configure(bg=T.BG_DEEP)

        init_fonts(self)
        apply_ttk_styles(self)

        GradientBackground(self).place(relx=0, rely=0, relwidth=1, relheight=1)

        shell = tk.Frame(self, bg=T.BG_DEEP)
        shell.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._sidebar = Sidebar(
            shell,
            self._show_view,
            self._new_analysis,
            on_docs=self._show_docs,
            on_support=self._show_support,
        )
        self._sidebar.pack(side='left', fill='y')

        self._main = tk.Frame(shell, bg=T.BG_MAIN)
        self._main.pack(side='left', fill='both', expand=True)

        self._scanner = ScannerView(self._main, self)
        self._validator = ValidatorView(self._main, self)
        self._catalog = CatalogView(self._main, self)
        self._views = {
            'scanner': self._scanner,
            'validator': self._validator,
            'catalog': self._catalog,
        }
        self._show_view('scanner')

    def _show_view(self, key: str):
        for view in self._views.values():
            view.pack_forget()
        self._views[key].pack(fill='both', expand=True)
        self._sidebar.set_active(key)
        self._views[key].on_show()

    def _new_analysis(self):
        self._scanner.reset()
        self._show_view('scanner')

    def _show_docs(self):
        messagebox.showinfo('Documentación', HELP_DOCUMENTATION)

    def _show_support(self):
        messagebox.showinfo(
            'Soporte',
            'Proyecto TLF — Teoría de Lenguajes Formales\n\n'
            'Motor regex propio: Lexer → Parser → NFA → DFA\n'
            'Para incidencias, consulte la documentación del repositorio.',
        )


# ===========================================================================
# ESCÁNER
# ===========================================================================

class ScannerView(tk.Frame):
    EJEMPLO = (
        'Contacte a juan.perez@empresa.com o soporte@tech.org para más info.\n'
        'Teléfonos: 3201234567 y +57 310 987 6543. Fijo: 601-5551234.\n'
        'Sitio web: https://www.mipagina.com/productos?ref=home\n'
        'Fecha de nacimiento: 15/08/1995. Cédula: 1234567890.\n'
        'Placa del vehículo: ABC-123. Moto: DEF78G.\n'
        'Servidor interno: 192.168.0.100. Backup: http://ftp.empresa.net\n'
        'Horario de atención: 08:00 AM a 06:00 PM.\n'
        'Síguenos en #ServicioAlCliente #Tecnología2024 #InnovaciónCO'
    )

    def __init__(self, parent, app: PatternApp):
        super().__init__(parent, bg=T.BG_MAIN)
        self._app = app
        self._pattern_vars: dict[str, tk.BooleanVar] = {}
        self._last_report = ''
        self._build()

    def on_show(self):
        pass

    def _build(self):
        HeroBanner(
            self,
            title='Detección inteligente de patrones',
            subtitle='Motor regex propio · Análisis en milisegundos · Exportación de reportes',
            metrics=[
                (str(len(PATTERNS)), 'Patrones'),
                ('<1ms', 'Por match'),
                ('100%', 'Offline'),
            ],
        ).pack(fill='x', padx=T.SPACE_LG, pady=(T.SPACE_MD, T.SPACE_SM))

        self._top = TopBar(
            self,
            title='Escáner de Textos',
            search_placeholder='Buscar en resultados...',
        )
        self._top.pack(fill='x')
        self._top.search_var.trace_add('write', lambda *_: self._filter_output())

        workspace = tk.Frame(self, bg=T.BG_MAIN)
        workspace.pack(fill='both', expand=True, padx=T.SPACE_LG, pady=(0, T.SPACE_LG))
        workspace.columnconfigure(1, weight=1)
        workspace.rowconfigure(0, weight=1)

        filters = LumenCard(workspace, title='Filtros de Patrón')
        filters.grid(row=0, column=0, sticky='ns', padx=(0, T.SPACE_MD))
        filters.configure(width=300)
        filters.grid_propagate(False)

        self._filter_toolbar = FilterToolbar(
            filters.body,
            on_select_all=lambda: self._set_all_patterns(True),
            on_select_none=lambda: self._set_all_patterns(False),
        )
        self._filter_toolbar.pack(fill='x', pady=(0, T.SPACE_SM))

        checks_scroll = ScrollableChecks(filters.body, height=240)
        checks_scroll.pack(fill='both', expand=True)

        for key, info in PATTERNS.items():
            var = tk.BooleanVar(value=True)
            self._pattern_vars[key] = var
            var.trace_add('write', lambda *_: self._update_filter_count())
            TealCheck(checks_scroll.panel, info['name'], var).pack(fill='x', pady=2)

        self._stats = tk.Label(
            filters.body, text='', bg=T.GLASS, fg=T.SUCCESS,
            font=TypeScale.SMALL, wraplength=260, justify='left', anchor='w',
        )
        self._stats.pack(fill='x', pady=(T.SPACE_SM, 0))

        tk.Frame(filters.body, bg=T.GLASS, height=T.SPACE_SM).pack()

        GlassButton(filters.body, 'Analizar Texto', variant='primary',
                    command=self._analyze).pack(fill='x', pady=(0, T.SPACE_XS))
        GlassButton(filters.body, 'Cargar Archivo', variant='outline',
                    command=self._load_file).pack(fill='x', pady=(0, T.SPACE_XS))
        GlassButton(filters.body, 'Exportar Reporte', variant='outline',
                    command=self._export_report).pack(fill='x', pady=(0, T.SPACE_XS))
        GlassButton(filters.body, 'Limpiar Todo', variant='text',
                    command=self.reset).pack(fill='x')

        self._update_filter_count()

        right = tk.Frame(workspace, bg=T.BG_MAIN)
        right.grid(row=0, column=1, sticky='nsew')
        right.rowconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        input_card = LumenCard(right, title='Texto a Analizar', mac_dots=True)
        input_card.grid(row=0, column=0, sticky='nsew', pady=(0, T.SPACE_SM))

        self._input = scrolledtext.ScrolledText(
            input_card.body, bg=T.GLASS_INNER, fg=T.TEXT,
            insertbackground=T.ACCENT, font=TypeScale.MONO,
            relief='flat', highlightthickness=0, wrap='word',
        )
        self._input.pack(fill='both', expand=True)
        self._input.insert('1.0', self.EJEMPLO)

        self._result_card = LumenCard(right, title='Resultados del Análisis')
        self._result_card.grid(row=1, column=0, sticky='nsew')
        hdr = self._result_card.body.winfo_children()[0]
        self._status_badge = PillBadge(hdr, 'STATUS: READY', variant='ready')
        self._status_badge.pack(side='right')

        self._output = scrolledtext.ScrolledText(
            self._result_card.body, bg=T.GLASS_INNER, fg=T.ACCENT_TEAL,
            font=TypeScale.MONO_SM, relief='flat', highlightthickness=0,
            state='disabled', wrap='word',
        )
        self._output.pack(fill='both', expand=True)

        self._footer = tk.Label(
            self._result_card.body,
            text='// Total matches found: 0. Analysis pending.',
            bg=T.GLASS, fg=T.TEXT_DIM, font=TypeScale.MONO_SM, anchor='w',
        )
        self._footer.pack(fill='x', pady=(T.SPACE_SM, 0))

    def _set_all_patterns(self, value: bool):
        for var in self._pattern_vars.values():
            var.set(value)
        self._update_filter_count()

    def _update_filter_count(self):
        n = sum(1 for v in self._pattern_vars.values() if v.get())
        total = len(self._pattern_vars)
        self._filter_toolbar.set_count(n, total)

    def reset(self):
        self._input.delete('1.0', 'end')
        self._input.insert('1.0', self.EJEMPLO)
        self._output.config(state='normal')
        self._output.delete('1.0', 'end')
        self._output.config(state='disabled')
        self._last_report = ''
        self._footer.config(text='// Total matches found: 0. Analysis pending.')
        self._stats.config(text='')
        self._status_badge.set_variant('STATUS: READY', 'ready')
        self._set_all_patterns(True)

    def _load_file(self):
        path = filedialog.askopenfilename(
            title='Seleccionar archivo de texto',
            filetypes=[('Archivos de texto', '*.txt'), ('Todos', '*.*')],
        )
        if not path:
            return
        try:
            with open(path, encoding='utf-8') as f:
                self._input.delete('1.0', 'end')
                self._input.insert('1.0', f.read())
        except OSError as exc:
            messagebox.showerror('Error', f'No se pudo leer el archivo:\n{exc}')

    def _export_report(self):
        if not self._last_report.strip():
            messagebox.showwarning('Aviso', 'Ejecute un análisis antes de exportar.')
            return
        path = filedialog.asksaveasfilename(
            title='Guardar reporte',
            defaultextension='.txt',
            filetypes=[('Texto', '*.txt'), ('Todos', '*.*')],
            initialfile='reporte_patrones.txt',
        )
        if not path:
            return
        try:
            export_text_report(self._last_report, path)
            messagebox.showinfo('Exportación', f'Reporte guardado en:\n{path}')
        except OSError as exc:
            messagebox.showerror('Error', str(exc))

    def _filter_output(self):
        q = self._top._search.get_query().lower()
        if not self._last_report or not q:
            if self._last_report:
                self._output.config(state='normal')
                self._output.delete('1.0', 'end')
                self._output.insert('1.0', self._last_report)
                self._output.config(state='disabled')
            return
        lines = [ln for ln in self._last_report.splitlines() if q in ln.lower()]
        filtered = '\n'.join(lines) if lines else '(Sin coincidencias para la búsqueda)'
        self._output.config(state='normal')
        self._output.delete('1.0', 'end')
        self._output.insert('1.0', filtered)
        self._output.config(state='disabled')

    def _analyze(self):
        text = self._input.get('1.0', 'end').strip()
        if not text:
            messagebox.showwarning('Aviso', 'Ingrese texto para analizar.')
            return
        selected = [k for k, v in self._pattern_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning('Aviso', 'Seleccione al menos un patrón.')
            return

        self._status_badge.set_variant('ANALIZANDO...', 'working')
        self.update_idletasks()

        t0 = time.perf_counter()
        try:
            scanner = TextScanner(selected_patterns=selected)
            results, report = scanner.scan_and_report(text)
            elapsed = int((time.perf_counter() - t0) * 1000)
            total = sum(len(v) for v in results.values())
            tipos = len(results)

            self._last_report = report
            self._output.config(state='normal')
            self._output.delete('1.0', 'end')
            self._output.insert('1.0', report)
            self._output.config(state='disabled')

            self._footer.config(
                text=f'// Total matches found: {total}. '
                     f'Analysis completed in {elapsed}ms.',
            )
            self._stats.config(
                text=f'✔ Análisis completado\n'
                     f'Coincidencias: {total}\n'
                     f'Tipos detectados: {tipos}/{len(selected)}',
            )
            self._status_badge.set_variant('STATUS: READY', 'ready')
        except Exception as exc:
            self._status_badge.set_variant('ERROR', 'error')
            messagebox.showerror('Error en análisis', str(exc))


# ===========================================================================
# VALIDADOR
# ===========================================================================

class ValidatorView(tk.Frame):
    _HINTS = {
        'nombre': 'Ej: María García López',
        'usuario': '4-20 chars, inicia con letra',
        'email': 'usuario@dominio.com',
        'password': 'Mín. 8 · mayús · dígito · especial',
        'telefono': '3001234567 o +57 310 555 0000',
        'cedula': '6-10 dígitos',
        'fecha_nac': 'DD/MM/AAAA',
        'sitio_web': 'https://mipagina.com',
    }
    def __init__(self, parent, app: PatternApp):
        super().__init__(parent, bg=T.BG_MAIN)
        self._app = app
        self.FIELDS = [(k, label, fn, self._HINTS[k]) for k, label, fn in FORM_FIELDS]
        self._fields: dict[str, FieldBox] = {}
        self._msgs: dict[str, tk.Label] = {}
        self._show_password = False
        self._build()

    def on_show(self):
        self._update_progress()

    def _build(self):
        HeroBanner(
            self,
            title='Validador Interactivo',
            subtitle='Validación en tiempo real con motor regex y reglas de negocio',
            metrics=[('7', 'Campos obligatorios'), ('Live', 'Feedback'), ('DFA', 'Motor')],
        ).pack(fill='x', padx=T.SPACE_LG, pady=(T.SPACE_MD, T.SPACE_SM))

        TopBar(self, title='', search_placeholder='Filtrar campos...').pack(fill='x')

        outer = tk.Frame(self, bg=T.BG_MAIN)
        outer.pack(fill='both', expand=True, padx=T.SPACE_LG, pady=(0, T.SPACE_LG))

        card = LumenCard(outer)
        card.pack(fill='both', expand=True)

        prog_hdr = tk.Frame(card.body, bg=T.GLASS)
        prog_hdr.pack(fill='x', pady=(0, T.SPACE_SM))
        tk.Label(prog_hdr, text='PROGRESO DE VALIDACIÓN', bg=T.GLASS, fg=T.TEXT_DIM,
                 font=TypeScale.CAPS).pack(side='left')
        self._prog_lbl = tk.Label(prog_hdr, text='Campos Válidos: 0/7', bg=T.GLASS,
                                  fg=T.ACCENT, font=TypeScale.BODY)
        self._prog_lbl.pack(side='right')

        self._progress = ProgressBar(card.body, height=8)
        self._progress.pack(fill='x', pady=(0, T.SPACE_LG))

        grid_frame = tk.Frame(card.body, bg=T.GLASS)
        grid_frame.pack(fill='both', expand=True)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        for i, (key, label, validator, hint) in enumerate(self.FIELDS):
            cell = tk.Frame(grid_frame, bg=T.GLASS)
            cell.grid(row=i // 2, column=i % 2, sticky='ew', padx=T.SPACE_SM, pady=T.SPACE_SM)

            lbl_row = tk.Frame(cell, bg=T.GLASS)
            lbl_row.pack(fill='x')
            tk.Label(lbl_row, text=label, bg=T.GLASS, fg=T.TEXT_SECOND,
                     font=TypeScale.SMALL).pack(side='left')
            if key == 'password':
                self._pw_toggle = tk.Label(
                    lbl_row, text='Mostrar', bg=T.GLASS, fg=T.ACCENT,
                    font=TypeScale.SMALL, cursor='hand2',
                )
                self._pw_toggle.pack(side='right')
                self._pw_toggle.bind('<Button-1>', self._toggle_password)

            box = FieldBox(cell, show='●' if key == 'password' else '')
            box.pack(fill='x', pady=(T.SPACE_XS, 0))
            self._fields[key] = box

            tk.Label(cell, text=hint, bg=T.GLASS, fg=T.TEXT_DIM,
                     font=TypeScale.SMALL, anchor='w').pack(anchor='w')

            msg = tk.Label(cell, text='', bg=T.GLASS, fg=T.DANGER,
                           font=TypeScale.SMALL, anchor='w', wraplength=320)
            msg.pack(anchor='w', pady=(2, 0))
            self._msgs[key] = msg

            if validator:
                box.entry.bind('<KeyRelease>', lambda _, k=key, v=validator: self._validate(k, v))
                box.entry.bind('<FocusOut>', lambda _, k=key, v=validator: self._validate(k, v))

        actions = tk.Frame(card.body, bg=T.GLASS)
        actions.pack(fill='x', pady=(T.SPACE_LG, 0))

        self._submit = GlassButton(
            actions, 'Enviar Formulario', variant='primary',
            command=self._submit_form, state='disabled',
        )
        self._submit.pack(fill='x', pady=(0, T.SPACE_SM))

        GlassButton(actions, '↻  Limpiar Formulario', variant='outline',
                    command=self.reset).pack(fill='x')

        self._result = tk.Label(card.body, text='', bg=T.GLASS, fg=T.SUCCESS,
                                font=TypeScale.H3, wraplength=700, justify='left')
        self._result.pack(anchor='w', pady=(T.SPACE_MD, 0))

    @staticmethod
    def _field_label(key: str) -> str:
        for k, label, *_ in FORM_FIELDS:
            if k == key:
                return label
        return key

    def _toggle_password(self, _=None):
        self._show_password = not self._show_password
        self._fields['password'].entry.configure(show='' if self._show_password else '●')
        self._pw_toggle.configure(text='Ocultar' if self._show_password else 'Mostrar')

    def _validate(self, key, validator):
        val = self._fields[key].entry.get()
        optional_empty = key == 'sitio_web' and not val.strip()

        if optional_empty:
            self._fields[key].set_status('neutral')
            self._msgs[key].config(text='')
        elif not val.strip():
            self._fields[key].set_status('neutral')
            self._msgs[key].config(text='Este campo es obligatorio.' if validator else '', fg=T.DANGER)
        else:
            ok, msg = validator(val)
            if ok:
                self._fields[key].set_status('valid')
                self._msgs[key].config(
                    text=f'✓ {self._field_label(key)} verificado correctamente.', fg=T.SUCCESS,
                )
            else:
                self._fields[key].set_status('invalid')
                self._msgs[key].config(text=f'✗ {msg}', fg=T.DANGER)
        self._update_progress()

    def _update_progress(self):
        mandatory = [(k, v) for k, _, v, _ in self.FIELDS if v is not None and k != 'sitio_web']
        valid = 0
        for key, validator in mandatory:
            val = self._fields[key].entry.get().strip()
            if val and validator(val)[0]:
                valid += 1
        total = len(mandatory)
        self._prog_lbl.config(text=f'Campos Válidos: {valid}/{total}')
        self._progress.set_progress(valid, total)
        self._submit.config(state='normal' if valid == total else 'disabled')

    def _submit_form(self):
        datos = {k: b.entry.get().strip() for k, b in self._fields.items()}
        self._result.config(
            text=f'✅ Formulario enviado correctamente\n'
                 f'Usuario registrado: {datos["nombre"]} (@{datos["usuario"]})',
            fg=T.SUCCESS,
        )

    def reset(self):
        for key, box in self._fields.items():
            box.entry.delete(0, 'end')
            box.set_status('neutral')
            self._msgs[key].config(text='')
        self._result.config(text='')
        self._submit.config(state='disabled')
        self._update_progress()


# ===========================================================================
# CATÁLOGO
# ===========================================================================

class CatalogView(tk.Frame):
    ICONS = {
        'email': '✉', 'telefono_co': '☎', 'fecha': '📅', 'fecha_iso': '📅',
        'url': '🔗', 'placa_co': '🚗', 'cedula_co': '🪪', 'codigo_postal': '📮',
        'ipv4': '🌐', 'hora': '🕐', 'hashtag': '#', 'tarjeta_credito': '💳',
    }

    def __init__(self, parent, app: PatternApp):
        super().__init__(parent, bg=T.BG_MAIN)
        self._app = app
        self._card_data: list[tuple[tk.Frame, str, str]] = []
        self._build()

    def on_show(self):
        pass

    def _build(self):
        HeroBanner(
            self,
            title='Catálogo de Patrones',
            subtitle='Expresiones regulares del motor propio — exportables y extensibles',
            metrics=[(str(len(PATTERNS)), 'Patrones'), ('Regex', 'Motor TLF'), ('JSON', 'Export')],
        ).pack(fill='x', padx=T.SPACE_LG, pady=(T.SPACE_MD, T.SPACE_SM))

        self._top = TopBar(
            self,
            title='',
            show_actions=True,
            on_export=self._export_catalog,
            on_create=self._create_pattern,
            search_placeholder='Buscar patrones por nombre...',
        )
        self._top.pack(fill='x')
        self._top.set_title('')

        scroll = ScrollableFrame(self, bg=T.BG_MAIN)
        scroll.pack(fill='both', expand=True, padx=T.SPACE_LG, pady=(0, T.SPACE_LG))
        root = scroll.content

        self._grid = ResponsiveGrid(root, columns_wide=3, min_col=300)
        self._grid.pack(fill='both', expand=True)

        for key, info in PATTERNS.items():
            card = self._make_card(self._grid, key, info)
            self._grid.add_cell(card)
            self._card_data.append((card, key, info['name'].lower()))

        request = tk.Frame(
            self._grid, bg=T.GLASS,
            highlightbackground=T.TEXT_DIM, highlightthickness=1,
        )
        inner = tk.Frame(request, bg=T.GLASS)
        inner.pack(expand=True, fill='both', padx=T.SPACE_LG, pady=T.SPACE_XL)
        tk.Label(inner, text='+', bg=T.GLASS, fg=T.TEXT_DIM, font=('Segoe UI', 28)).pack(
            pady=(T.SPACE_LG, T.SPACE_SM),
        )
        tk.Label(inner, text='Solicitar Patrón', bg=T.GLASS, fg=T.TEXT,
                 font=TypeScale.H2).pack()
        tk.Label(
            inner,
            text='¿Necesitas detectar un formato específico?\n'
                 'Contacta al equipo o crea un patrón personalizado.',
            bg=T.GLASS, fg=T.TEXT_DIM, font=TypeScale.SMALL, justify='center',
        ).pack(pady=T.SPACE_SM)
        GlassButton(inner, 'Solicitar', variant='outline',
                    command=self._request_pattern).pack(pady=T.SPACE_SM)
        self._grid.add_cell(request)

        self._top.search_var.trace_add('write', lambda *_: self._filter_cards())

    def _make_card(self, parent, key, info):
        card = tk.Frame(parent, bg=T.GLASS, highlightbackground=T.GLASS_BORDER,
                        highlightthickness=1, cursor='hand2')
        inner = tk.Frame(card, bg=T.GLASS)
        inner.pack(fill='both', expand=True, padx=T.SPACE_MD, pady=T.SPACE_MD)

        hdr = tk.Frame(inner, bg=T.GLASS)
        hdr.pack(fill='x')
        tk.Label(hdr, text=self.ICONS.get(key, '◆'), bg=T.GLASS,
                 fg=T.ACCENT, font=('Segoe UI', 16)).pack(side='left')
        PillBadge(hdr, 'Validated', variant='validated').pack(side='right')

        tk.Label(inner, text=info['name'], bg=T.GLASS, fg=T.TEXT,
                 font=TypeScale.H2, anchor='w').pack(fill='x', pady=(T.SPACE_SM, T.SPACE_XS))
        tk.Label(inner, text=info['description'], bg=T.GLASS, fg=T.TEXT_SECOND,
                 font=TypeScale.SMALL, anchor='w', wraplength=280).pack(fill='x')

        pat = info['pattern'] if len(info['pattern']) <= 72 else info['pattern'][:72] + '…'
        code = tk.Frame(inner, bg=T.GLASS_INNER)
        code.pack(fill='x', pady=T.SPACE_SM)
        tk.Label(code, text=pat, bg=T.GLASS_INNER, fg=T.ACCENT_TEAL,
                 font=TypeScale.MONO_SM, anchor='w', padx=10, pady=8).pack(fill='x')

        tk.Label(inner, text='✓  ' + '   ✓  '.join(info['valid_ex'][:2]),
                 bg=T.GLASS, fg=T.SUCCESS, font=TypeScale.SMALL,
                 anchor='w', wraplength=280).pack(fill='x', pady=(T.SPACE_XS, 2))
        tk.Label(inner, text='✕  ' + '   ✕  '.join(info['invalid_ex'][:2]),
                 bg=T.GLASS, fg=T.DANGER, font=TypeScale.SMALL,
                 anchor='w', wraplength=280).pack(fill='x')

        for w in (card, inner):
            w.bind('<Button-1>', lambda _, k=key, i=info: self._show_detail(k, i))
        return card

    def _show_detail(self, key: str, info: dict):
        pat = info['pattern']
        msg = (
            f"{info['name']}\n\n{info['description']}\n\n"
            f"Regex:\n{pat}\n\n"
            f"Válidos: {', '.join(info['valid_ex'])}\n"
            f"Inválidos: {', '.join(info['invalid_ex'])}"
        )
        messagebox.showinfo(f'Patrón — {key}', msg)

    def _filter_cards(self):
        q = self._top._search.get_query().lower()
        for card, key, name in self._card_data:
            if not q or q in name or q in key:
                card.grid()
            else:
                card.grid_remove()

    def _export_catalog(self):
        path = filedialog.asksaveasfilename(
            title='Exportar catálogo',
            defaultextension='.json',
            filetypes=[
                ('JSON', '*.json'),
                ('Markdown', '*.md'),
                ('Todos', '*.*'),
            ],
            initialfile='catalogo_patrones.json',
        )
        if not path:
            return
        try:
            if path.endswith('.md'):
                export_catalog_markdown(path)
            else:
                export_catalog_json(path)
            messagebox.showinfo('Exportación', f'Catálogo exportado:\n{path}')
        except OSError as exc:
            messagebox.showerror('Error', str(exc))

    def _create_pattern(self):
        nombre = simpledialog.askstring('Crear patrón', 'Nombre del patrón:', parent=self)
        if not nombre:
            return
        regex = simpledialog.askstring('Crear patrón', 'Expresión regular:', parent=self)
        if not regex:
            return
        try:
            eng = EngineManager.get_custom(regex, key=f'custom_{nombre[:12]}')
            prueba = simpledialog.askstring(
                'Probar patrón', 'Texto de prueba (opcional):', parent=self,
            ) or ''
            ok = eng.match(prueba) if prueba else True
            messagebox.showinfo(
                'Patrón creado',
                f'Patrón "{nombre}" compilado correctamente.\n'
                f'Prueba: {"coincide" if ok else "no coincide"}',
            )
        except Exception as exc:
            messagebox.showerror('Error de compilación', str(exc))

    def _request_pattern(self):
        desc = simpledialog.askstring(
            'Solicitar patrón',
            'Describe el formato que necesitas detectar:',
            parent=self,
        )
        if desc:
            messagebox.showinfo(
                'Solicitud registrada',
                f'Solicitud anotada:\n"{desc}"\n\n'
                'En producción esto se enviaría al equipo de desarrollo.',
            )
