from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

_FONT = 'Segoe UI'


def init_fonts(root: tk.Misc) -> None:
    global _FONT
    families = set(tkfont.families(root))
    for name in ('Segoe UI', 'Inter', 'Helvetica Neue', 'Tahoma'):
        if name in families:
            _FONT = name
            break
    _refresh_type_scale()


class TypeScale:
    BRAND = ('Segoe UI', 18, 'bold')
    BRAND_SUB = ('Segoe UI', 8)
    PAGE_TITLE = ('Segoe UI', 22, 'bold')
    H2 = ('Segoe UI', 13, 'bold')
    H3 = ('Segoe UI', 11, 'bold')
    BODY = ('Segoe UI', 10)
    SMALL = ('Segoe UI', 9)
    CAPS = ('Segoe UI', 8, 'bold')
    MONO = ('Consolas', 10)
    MONO_SM = ('Consolas', 9)


def _refresh_type_scale():
    f = _FONT
    TypeScale.BRAND = (f, 18, 'bold')
    TypeScale.BRAND_SUB = (f, 8)
    TypeScale.PAGE_TITLE = (f, 22, 'bold')
    TypeScale.H2 = (f, 13, 'bold')
    TypeScale.H3 = (f, 11, 'bold')
    TypeScale.BODY = (f, 10)
    TypeScale.SMALL = (f, 9)
    TypeScale.CAPS = (f, 8, 'bold')


class Theme:
    BG_DEEP = '#0b111b'
    BG_MAIN = '#0f1720'
    SIDEBAR = '#0d1520'
    GLASS = '#16212b'
    GLASS_HOVER = '#1c2a38'
    GLASS_BORDER = '#243444'
    GLASS_INNER = '#0d1822'

    ACCENT = '#2bb38c'
    ACCENT_HOVER = '#34d399'
    ACCENT_DARK = '#1a8f6e'
    ACCENT_GLOW = '#143d32'
    ACCENT_TEAL = '#5eead4'

    SUCCESS = '#4ade80'
    SUCCESS_BG = '#14352a'
    DANGER = '#f87171'
    DANGER_BG = '#3d1f24'
    WARNING = '#fbbf24'

    TEXT = '#f8fafc'
    TEXT_SECOND = '#94a3b8'
    TEXT_DIM = '#64748b'

    DOT_RED = '#ff5f57'
    DOT_YELLOW = '#febc2e'
    DOT_GREEN = '#28c840'

    SIDEBAR_W = 240
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32
    BREAKPOINT = 960


T = Theme


class GradientBackground(tk.Canvas):
    ORBS = (
        ('#2bb38c', 0.15, 0.85, 0.35),
        ('#14b8a6', 0.85, 0.15, 0.30),
        ('#0d9488', 0.50, 0.50, 0.25),
    )

    def __init__(self, parent, **kw):
        kw.setdefault('highlightthickness', 0)
        kw.setdefault('bg', T.BG_DEEP)
        super().__init__(parent, **kw)
        self.bind('<Configure>', self._redraw)

    def _redraw(self, _e=None):
        w, h = max(self.winfo_width(), 1), max(self.winfo_height(), 1)
        self.delete('all')
        for i in range(20):
            t = i / 20
            c = int(11 + t * 8)
            self.create_rectangle(0, int(h * t), w, int(h * (t + 1 / 20)) + 1,
                                fill=f'#{c:02x}{c+4:02x}{c+10:02x}', outline='')
        for color, nx, ny, sc in self.ORBS:
            cx, cy = int(w * nx), int(h * ny)
            r = int(min(w, h) * sc)
            self.create_oval(cx - r, cy - r, cx + r, cy + r,
                            fill=color, outline='', stipple='gray50')


class Sidebar(tk.Frame):
    NAV = (
        ('scanner', 'Escáner de textos'),
        ('validator', 'Validador interactivo'),
        ('catalog', 'Catálogo de patrones'),
    )

    def __init__(self, parent, on_navigate, on_docs=None, on_support=None, **kw):
        kw.setdefault('bg', T.SIDEBAR)
        kw.setdefault('width', T.SIDEBAR_W)
        super().__init__(parent, **kw)
        self.pack_propagate(False)
        self._on_navigate = on_navigate
        self._on_docs = on_docs
        self._on_support = on_support
        self._buttons: dict[str, NavItem] = {}
        self._active = ''
        self._build()

    def _build(self):
        brand = tk.Frame(self, bg=T.SIDEBAR)
        brand.pack(fill='x', padx=T.SPACE_MD, pady=(T.SPACE_LG, T.SPACE_LG))
        tk.Label(brand, text='PATRONES TLF', bg=T.SIDEBAR, fg=T.TEXT,
                font=TypeScale.BRAND, anchor='w').pack(anchor='w')
        tk.Label(brand, text='Teoría de lenguajes formales', bg=T.SIDEBAR, fg=T.TEXT_DIM,
                font=TypeScale.BRAND_SUB, anchor='w').pack(anchor='w')

        nav = tk.Frame(self, bg=T.SIDEBAR)
        nav.pack(fill='x', padx=T.SPACE_SM)

        for key, label in self.NAV:
            btn = NavItem(nav, label, lambda k=key: self._on_navigate(k))
            btn.pack(fill='x', pady=2)
            self._buttons[key] = btn

        tk.Frame(self, bg=T.SIDEBAR, height=1).pack(fill='both', expand=True)

        bottom = tk.Frame(self, bg=T.SIDEBAR)
        bottom.pack(fill='x', padx=T.SPACE_MD, pady=T.SPACE_LG)

        if self._on_docs:
            LinkLabel(bottom, 'Ayuda', self._on_docs).pack(anchor='w', pady=3)
        if self._on_support:
            LinkLabel(bottom, 'Support', self._on_support).pack(anchor='w', pady=3)

    def set_active(self, key: str):
        self._active = key
        for k, btn in self._buttons.items():
            btn.set_active(k == key)


class NavItem(tk.Frame):
    def __init__(self, parent, label: str, command, **kw):
        super().__init__(parent, bg=T.SIDEBAR, cursor='hand2', **kw)
        self._command = command
        self._active = False

        self._bar = tk.Frame(self, bg=T.SIDEBAR, width=3)
        self._bar.pack(side='left', fill='y')

        self._inner = tk.Frame(self, bg=T.SIDEBAR)
        self._inner.pack(side='left', fill='x', expand=True, padx=(T.SPACE_SM, T.SPACE_SM), pady=8)
        inner = self._inner

        self._text_lbl = tk.Label(inner, text=label, bg=T.SIDEBAR, fg=T.TEXT_SECOND,
                                font=TypeScale.BODY, anchor='w')
        self._text_lbl.pack(side='left', fill='x', expand=True)

        for w in (self, inner, self._text_lbl):
            w.bind('<Button-1>', lambda _: self._command())
            w.bind('<Enter>', self._on_enter)
            w.bind('<Leave>', self._on_leave)

    def set_active(self, active: bool):
        self._active = active
        bg = T.ACCENT_GLOW if active else T.SIDEBAR
        bar = T.ACCENT if active else T.SIDEBAR
        self._bar.configure(bg=bar)
        self.configure(bg=bg)
        for w in (self._inner, self._text_lbl):
            w.configure(bg=bg)
        self._text_lbl.configure(fg=T.ACCENT if active else T.TEXT_SECOND)

    def _on_enter(self, _=None):
        if not self._active:
            for w in (self, self._inner, self._text_lbl):
                w.configure(bg=T.GLASS_HOVER)

    def _on_leave(self, _=None):
        self.set_active(self._active)


class TopBar(tk.Frame):
    def __init__(
        self,
        parent,
        title: str = '',
        subtitle: str = '',
        show_search: bool = True,
        show_actions: bool = False,
        on_export=None,
        on_search=None,
        search_placeholder: str = 'Buscar...',
        **kw,
    ):
        kw.setdefault('bg', T.BG_MAIN)
        super().__init__(parent, **kw)

        left = tk.Frame(self, bg=T.BG_MAIN)
        left.pack(side='left', fill='y', padx=T.SPACE_LG, pady=T.SPACE_MD)
        self._title_lbl = tk.Label(left, text=title, bg=T.BG_MAIN, fg=T.TEXT,
                                font=TypeScale.PAGE_TITLE, anchor='w')
        self._title_lbl.pack(anchor='w')
        if subtitle:
            tk.Label(left, text=subtitle, bg=T.BG_MAIN, fg=T.TEXT_SECOND,
                    font=TypeScale.BODY, anchor='w').pack(anchor='w', pady=(T.SPACE_XS, 0))

        self._search = None
        if show_search:
            self._search = SearchEntry(
                self, placeholder=search_placeholder, on_change=on_search,
            )
            self._search.pack(side='left', fill='x', expand=True,
                                padx=(T.SPACE_MD, T.SPACE_LG), pady=T.SPACE_MD, ipadx=120)

        if show_actions and on_export:
            GlassButton(self, 'Exportar', variant='outline', command=on_export
                        ).pack(side='right', padx=(0, T.SPACE_LG), pady=T.SPACE_MD)

    def set_title(self, title: str):
        self._title_lbl.configure(text=title)

    def get_search_query(self) -> str:
        return self._search.get_query() if self._search else ''

    @property
    def search_var(self) -> tk.StringVar:
        return self._search.var if self._search else tk.StringVar()


class SearchEntry(tk.Frame):
    """Campo de busqueda con placeholder y notificacion en cada tecla."""

    def __init__(self, parent, placeholder='Buscar...', on_change=None, **kw):
        super().__init__(parent, bg=T.GLASS, highlightbackground=T.GLASS_BORDER,
                         highlightthickness=1, **kw)
        self._ph = placeholder
        self._placeholder_active = True
        self._on_change = on_change
        self._suppress = False

        self.var = tk.StringVar(value=placeholder)
        self._entry = tk.Entry(
            self, textvariable=self.var, bg=T.GLASS, fg=T.TEXT_DIM,
            insertbackground=T.ACCENT, font=TypeScale.BODY,
            relief='flat', bd=0,
        )
        self._entry.pack(fill='x', expand=True, ipady=8, padx=12, pady=2)

        self._entry.bind('<FocusIn>', self._focus_in)
        self._entry.bind('<FocusOut>', self._focus_out)
        self._entry.bind('<KeyRelease>', lambda _: self._notify())
        self.var.trace_add('write', lambda *_: self._notify())

    def _focus_in(self, _=None):
        if self._placeholder_active:
            self._suppress = True
            self._placeholder_active = False
            self.var.set('')
            self._entry.configure(fg=T.TEXT)
            self._suppress = False

    def _focus_out(self, _=None):
        if not self.var.get().strip():
            self._suppress = True
            self._placeholder_active = True
            self.var.set(self._ph)
            self._entry.configure(fg=T.TEXT_DIM)
            self._suppress = False

    def _notify(self):
        if self._suppress or self._placeholder_active or not self._on_change:
            return
        self._on_change()

    def get_query(self) -> str:
        if self._placeholder_active:
            return ''
        return self.var.get().strip()


class IconBtn(tk.Label):
    def __init__(self, parent, text, **kw):
        kw.setdefault('bg', T.GLASS)
        kw.setdefault('fg', T.TEXT_SECOND)
        kw.setdefault('font', TypeScale.BODY)
        kw.setdefault('padx', 10)
        kw.setdefault('pady', 6)
        kw.setdefault('cursor', 'hand2')
        super().__init__(parent, text=text, **kw)
        self.bind('<Enter>', lambda _: self.configure(bg=T.GLASS_HOVER))
        self.bind('<Leave>', lambda _: self.configure(bg=T.GLASS))


class LumenCard(tk.Frame):
    def __init__(self, parent, title: str = '', badge: str = '', mac_dots: bool = False, **kw):
        kw.setdefault('bg', T.GLASS)
        kw.setdefault('highlightbackground', T.GLASS_BORDER)
        kw.setdefault('highlightthickness', 1)
        super().__init__(parent, **kw)
        self.body = tk.Frame(self, bg=T.GLASS)
        self.body.pack(fill='both', expand=True, padx=T.SPACE_MD, pady=T.SPACE_MD)

        if title or badge or mac_dots:
            hdr = tk.Frame(self.body, bg=T.GLASS)
            hdr.pack(fill='x', pady=(0, T.SPACE_SM))
            if title:
                tk.Label(hdr, text=title, bg=T.GLASS, fg=T.TEXT,
                        font=TypeScale.H2, anchor='w').pack(side='left')
            if badge:
                PillBadge(hdr, badge).pack(side='right')
            if mac_dots:
                dots = tk.Frame(hdr, bg=T.GLASS)
                dots.pack(side='right')
                for c in (T.DOT_RED, T.DOT_YELLOW, T.DOT_GREEN):
                    tk.Label(dots, text='●', bg=T.GLASS, fg=c, font=('Segoe UI', 7)
                            ).pack(side='left', padx=2)

    def pack_body(self, widget, **kw):
        widget.pack(in_=self.body, **kw)


class PillBadge(tk.Label):
    VARIANTS = {
        'ready': (T.SUCCESS_BG, T.SUCCESS),
        'validated': (T.SUCCESS_BG, T.SUCCESS),
        'pending': (T.ACCENT_GLOW, T.ACCENT_TEAL),
        'working': (T.ACCENT_GLOW, T.WARNING),
        'error': (T.DANGER_BG, T.DANGER),
    }

    def __init__(self, parent, text, variant='ready', **kw):
        bg, fg = self.VARIANTS.get(variant, self.VARIANTS['ready'])
        kw.setdefault('bg', bg)
        kw.setdefault('fg', fg)
        kw.setdefault('font', TypeScale.CAPS)
        kw.setdefault('padx', 10)
        kw.setdefault('pady', 3)
        super().__init__(parent, text=text.upper(), **kw)
        self._variant = variant

    def set_variant(self, text: str, variant: str):
        bg, fg = self.VARIANTS.get(variant, self.VARIANTS['ready'])
        self.configure(text=text.upper(), bg=bg, fg=fg)
        self._variant = variant


class HeroBanner(tk.Frame):
    """Franja con titulo, subtitulo y metricas."""

    def __init__(self, parent, title: str, subtitle: str, metrics: list[tuple[str, str]], **kw):
        kw.setdefault('bg', T.GLASS)
        kw.setdefault('highlightbackground', T.GLASS_BORDER)
        kw.setdefault('highlightthickness', 1)
        super().__init__(parent, **kw)

        inner = tk.Frame(self, bg=T.GLASS)
        inner.pack(fill='x', padx=T.SPACE_LG, pady=T.SPACE_MD)

        left = tk.Frame(inner, bg=T.GLASS)
        left.pack(side='left', fill='x', expand=True)
        tk.Label(left, text=title, bg=T.GLASS, fg=T.TEXT,
                font=TypeScale.PAGE_TITLE, anchor='w').pack(anchor='w')
        tk.Label(left, text=subtitle, bg=T.GLASS, fg=T.TEXT_SECOND,
                font=TypeScale.BODY, anchor='w').pack(anchor='w', pady=(T.SPACE_XS, 0))

        stats = tk.Frame(inner, bg=T.GLASS)
        stats.pack(side='right')
        for value, label in metrics:
            StatCard(stats, value, label).pack(side='left', padx=(T.SPACE_SM, 0))


class StatCard(tk.Frame):
    def __init__(self, parent, value: str, label: str, **kw):
        super().__init__(parent, bg=T.GLASS_INNER, highlightbackground=T.GLASS_BORDER,
                         highlightthickness=1, **kw)
        tk.Label(self, text=value, bg=T.GLASS_INNER, fg=T.ACCENT,
                font=(TypeScale.BODY[0], 16, 'bold'), padx=14).pack(pady=(10, 2))
        tk.Label(self, text=label.upper(), bg=T.GLASS_INNER, fg=T.TEXT_DIM,
                font=TypeScale.CAPS, padx=14).pack(pady=(0, 10))


class FilterToolbar(tk.Frame):
    """Seleccionar todos, ninguno y contador."""

    def __init__(self, parent, on_select_all, on_select_none, **kw):
        kw.setdefault('bg', T.GLASS)
        super().__init__(parent, **kw)
        GlassButton(self, 'Seleccionar todos', variant='ghost',
                    command=on_select_all).pack(side='left', padx=(0, T.SPACE_XS))
        GlassButton(self, 'Ninguno', variant='ghost',
                    command=on_select_none).pack(side='left')
        self.counter = tk.Label(self, text='', bg=T.GLASS, fg=T.ACCENT_TEAL,
                                font=TypeScale.SMALL)
        self.counter.pack(side='right')

    def set_count(self, selected: int, total: int):
        self.counter.configure(text=f'{selected} / {total} activos')


class LinkLabel(tk.Label):
    def __init__(self, parent, text, command, **kw):
        kw.setdefault('bg', T.SIDEBAR)
        kw.setdefault('fg', T.TEXT_DIM)
        kw.setdefault('font', TypeScale.SMALL)
        kw.setdefault('cursor', 'hand2')
        super().__init__(parent, text=text, **kw)
        self._cmd = command
        self.bind('<Button-1>', lambda _: self._cmd())
        self.bind('<Enter>', lambda _: self.configure(fg=T.ACCENT))
        self.bind('<Leave>', lambda _: self.configure(fg=T.TEXT_DIM))


class ScrollableChecks(tk.Frame):
    """Lista de checkboxes con scroll para muchos filtros."""

    def __init__(self, parent, height=220, **kw):
        kw.setdefault('bg', T.GLASS)
        super().__init__(parent, **kw)
        self._canvas = tk.Canvas(self, bg=T.GLASS, highlightthickness=0, height=height)
        self._bar = ttk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
        self.panel = tk.Frame(self._canvas, bg=T.GLASS)
        self._wid = self._canvas.create_window((0, 0), window=self.panel, anchor='nw')
        self._canvas.configure(yscrollcommand=self._bar.set)
        self._bar.pack(side='right', fill='y')
        self._canvas.pack(side='left', fill='both', expand=True)
        self.panel.bind('<Configure>', lambda _: self._canvas.configure(
            scrollregion=self._canvas.bbox('all')))
        self._canvas.bind('<Configure>', lambda e: self._canvas.itemconfig(self._wid, width=e.width))


class GlassButton(tk.Button):
    VARIANTS = {
        'primary': (T.ACCENT, '#ffffff', T.ACCENT_HOVER),
        'outline': (T.GLASS, T.TEXT, T.GLASS_HOVER),
        'ghost': (T.GLASS, T.TEXT_DIM, T.GLASS_HOVER),
        'success': (T.ACCENT, '#ffffff', T.ACCENT_HOVER),
        'text': (T.GLASS, T.TEXT_DIM, T.GLASS),
    }

    def __init__(self, parent, text='', command=None, variant='primary', **kw):
        bg, fg, hover = self.VARIANTS.get(variant, self.VARIANTS['primary'])
        kw.setdefault('bg', bg)
        kw.setdefault('fg', fg)
        kw.setdefault('activebackground', hover)
        kw.setdefault('activeforeground', fg)
        kw.setdefault('font', TypeScale.BODY)
        kw.setdefault('relief', 'flat')
        kw.setdefault('bd', 0)
        kw.setdefault('padx', 16)
        kw.setdefault('pady', 10)
        kw.setdefault('cursor', 'hand2')
        if variant == 'outline':
            kw.setdefault('highlightbackground', T.GLASS_BORDER)
            kw.setdefault('highlightthickness', 1)
        super().__init__(parent, text=text, command=command, **kw)
        self._bg, self._hover = bg, hover
        state = kw.get('state', 'normal')
        if state != 'disabled':
            self.bind('<Enter>', lambda _: self.configure(bg=self._hover))
            self.bind('<Leave>', lambda _: self.configure(bg=self._bg))


class TealCheck(tk.Checkbutton):
    def __init__(self, parent, text, variable, **kw):
        kw.setdefault('bg', T.GLASS)
        kw.setdefault('fg', T.TEXT)
        kw.setdefault('selectcolor', T.GLASS_INNER)
        kw.setdefault('activebackground', T.GLASS)
        kw.setdefault('activeforeground', T.TEXT)
        kw.setdefault('font', TypeScale.BODY)
        kw.setdefault('anchor', 'w')
        super().__init__(parent, text=text, variable=variable, **kw)


class FieldBox(tk.Frame):
    """Campo con icono de estado a la derecha (validador)."""

    def __init__(self, parent, show='', **kw):
        super().__init__(parent, bg=T.GLASS_BORDER, **kw)
        inner = tk.Frame(self, bg=T.GLASS_INNER)
        inner.pack(fill='x', padx=1, pady=1)

        self.entry = tk.Entry(inner, bg=T.GLASS_INNER, fg=T.TEXT,
                            insertbackground=T.ACCENT, font=TypeScale.MONO,
                            relief='flat', bd=0, show=show)
        self.entry.pack(side='left', fill='x', expand=True, ipady=10, padx=(12, 4))

        self.status = tk.Label(inner, text='○', bg=T.GLASS_INNER, fg=T.TEXT_DIM,
                            font=TypeScale.BODY, width=2)
        self.status.pack(side='right', padx=(0, 10))

    def set_status(self, state: str):
        icons = {'neutral': ('○', T.TEXT_DIM), 'valid': ('✓', T.SUCCESS),
                'invalid': ('✕', T.DANGER)}
        sym, fg = icons.get(state, icons['neutral'])
        self.status.configure(text=sym, fg=fg)


class ProgressBar(tk.Canvas):
    def __init__(self, parent, height=8, **kw):
        kw.setdefault('bg', T.GLASS_INNER)
        kw.setdefault('highlightthickness', 0)
        kw.setdefault('height', height)
        super().__init__(parent, **kw)
        self._ratio = 0.0
        self.bind('<Configure>', lambda _: self.draw())

    def set_progress(self, current: int, total: int):
        self._ratio = current / total if total else 0.0
        self.draw()

    def draw(self):
        self.delete('all')
        w, h = max(self.winfo_width(), 1), max(self.winfo_height(), 1)
        fw = int(w * self._ratio)
        if fw > 2:
            self.create_rectangle(0, 0, fw, h, fill=T.ACCENT, outline='')


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg=T.BG_MAIN, **kw):
        super().__init__(parent, bg=bg, **kw)
        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self._bar = ttk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
        self.content = tk.Frame(self._canvas, bg=bg)
        self._wid = self._canvas.create_window((0, 0), window=self.content, anchor='nw')
        self._canvas.configure(yscrollcommand=self._bar.set)
        self._bar.pack(side='right', fill='y')
        self._canvas.pack(side='left', fill='both', expand=True)
        self.content.bind('<Configure>', lambda _: self._canvas.configure(
            scrollregion=self._canvas.bbox('all')))
        self._canvas.bind('<Configure>', lambda e: self._canvas.itemconfig(self._wid, width=e.width))
        self._canvas.bind('<Enter>', lambda _: self._canvas.bind_all('<MouseWheel>', self._wheel))
        self._canvas.bind('<Leave>', lambda _: self._canvas.unbind_all('<MouseWheel>'))

    def _wheel(self, e):
        self._canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')


class ResponsiveGrid(tk.Frame):
    def __init__(self, parent, columns_wide=3, min_col=300, **kw):
        kw.setdefault('bg', T.BG_MAIN)
        super().__init__(parent, **kw)
        self._cols_wide = columns_wide
        self._min_col = min_col
        self._cells: list[tk.Widget] = []
        self._visible: set[tk.Widget] | None = None
        self.bind('<Configure>', self._relayout)

    def add_cell(self, w: tk.Widget):
        self._cells.append(w)
        self._relayout()

    def set_visible(self, widgets: list[tk.Widget] | None):
        """None = mostrar todas las celdas; lista = solo esas (orden original)."""
        self._visible = None if widgets is None else set(widgets)
        self._relayout()

    def _active_cells(self) -> list[tk.Widget]:
        if self._visible is None:
            return self._cells
        return [c for c in self._cells if c in self._visible]

    def _relayout(self, _=None):
        w = self.winfo_width()
        cols = max(1, min(self._cols_wide, w // self._min_col)) if w > 1 else 1
        for c in range(cols):
            self.columnconfigure(c, weight=1, uniform='g')
        active = self._active_cells()
        for cell in self._cells:
            cell.grid_forget()
        for i, cell in enumerate(active):
            r, c = divmod(i, cols)
            cell.grid(row=r, column=c, sticky='nsew', padx=T.SPACE_SM, pady=T.SPACE_SM)


def apply_ttk_styles(root: tk.Misc):
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('Vertical.TScrollbar', background=T.GLASS, troughcolor=T.GLASS_INNER)
