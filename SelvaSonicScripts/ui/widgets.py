import tkinter as tk
from tkinter import ttk
from synth.config import SynthConfig, WaveType

# ─────────────────────────────────────────────────────────────────────────────
#  Paleta SelvaSonic (Fiel ao CSS)
# ─────────────────────────────────────────────────────────────────────────────
C_AMARELO  = "#F5C800"
C_VERDE    = "#1A7A2E"
C_MARROM   = "#5C3317"
C_AZUL     = "#1B4FD8"
C_VERMELHO = "#C8281E"
C_PRETO    = "#0A0A0A"
C_ROXO     = "#6B2D8B"
C_BG       = "#111111"
C_BG2      = "#1A1A1A"
C_BG3      = "#222222"
C_TEXTO    = "#E8E0C8"
C_TEXTO2   = "#A09880"

# ─────────────────────────────────────────────────────────────────────────────
#  Fontes Customizadas
# ─────────────────────────────────────────────────────────────────────────────
F_BEBAS  = ("Bebas Neue", 14)
F_BARLOW = ("Barlow Condensed", 10, "bold")
F_SPACE  = ("Space Mono", 9)


# ─────────────────────────────────────────────────────────────────────────────
#  Componentes Customizados (Canvas & Frames)
# ─────────────────────────────────────────────────────────────────────────────

class SelvaSlider(tk.Canvas):
    """Slider customizado para imitar o .ss-slider com clip-path poligonal no thumb."""
    def __init__(self, parent, width=150, height=22, from_=0.0, to_=1.0, init=0.5, command=None, accent=C_AMARELO):
        super().__init__(parent, width=width, height=height, bg=C_BG2, highlightthickness=0)
        self.width = width
        self.height = height
        self.from_ = from_
        self.to_ = to_
        self.value = init
        self.command = command
        self.accent = accent

        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.draw()

    def draw(self):
        self.delete("all")
        # Track (Fundo do slider)
        self.create_rectangle(0, 8, self.width, 14, fill=C_BG3, outline=C_MARROM, width=1)
        
        # Lógica de proporção
        val_range = self.to_ - self.from_
        percent = 0 if val_range == 0 else (self.value - self.from_) / val_range
        percent = max(0.0, min(1.0, percent))
        
        x_center = 8 + percent * (self.width - 16)
        
        # Thumb: clip-path: polygon(3px 0, 100% 0, calc(100% - 3px) 100%, 0 100%)
        x0, y0, y1 = x_center - 8, 0, self.height
        points = [x0+3, y0,  x0+16, y0,  x0+13, y1,  x0, y1]
        self.create_polygon(points, fill=self.accent, outline="")

    def _update_val_from_x(self, x):
        percent = (x - 8) / (self.width - 16)
        percent = max(0.0, min(1.0, percent))
        self.value = self.from_ + percent * (self.to_ - self.from_)
        self.draw()
        if self.command:
            self.command(self.value)

    def _on_click(self, event): self._update_val_from_x(event.x)
    def _on_drag(self, event):  self._update_val_from_x(event.x)
        
    def set(self, val):
        self.value = max(self.from_, min(self.to_, val))
        self.draw()


def _make_ss_label(parent, text, accent):
    """Label estilo placa marrom com recorte angular (tag)."""
    canvas = tk.Canvas(parent, width=110, height=22, bg=C_BG2, highlightthickness=0)
    # Clip-path visual: polygon(0 0, calc(100% - 6px) 0, 100% 50%, calc(100% - 6px) 100%, 0 100%)
    pts = [0, 0,  104, 0,  110, 11,  104, 22,  0, 22]
    canvas.create_polygon(pts, fill=C_MARROM, outline="")
    canvas.create_text(10, 11, text=text.upper(), fill=accent, font=F_BARLOW, anchor="w")
    return canvas


def _styled_button(parent, text, command, accent=C_AMARELO, danger=False):
    """Botão dark com borda esquerda acentuada e hover color-fill."""
    btn_frame = tk.Frame(parent, bg=C_BG3, highlightthickness=1, highlightbackground=C_MARROM)
    
    accent_color = C_VERMELHO if danger else accent
    left_border = tk.Frame(btn_frame, width=3, bg=C_AMARELO if not danger else C_AMARELO)
    left_border.pack(side="left", fill="y")
    
    lbl = tk.Label(btn_frame, text=text.upper(), font=F_BARLOW, bg=C_BG3, fg=C_TEXTO, padx=12, pady=4, cursor="hand2")
    lbl.pack(side="left")

    def on_enter(e):
        btn_frame.config(highlightbackground=accent_color)
        left_border.config(bg=accent_color)
        lbl.config(bg=accent_color, fg=C_PRETO if not danger else "#FFFFFF")

    def on_leave(e):
        btn_frame.config(highlightbackground=C_MARROM)
        left_border.config(bg=C_AMARELO)
        lbl.config(bg=C_BG3, fg=C_TEXTO)

    def on_click(e):
        if command: command()

    for w in (btn_frame, left_border, lbl):
        w.bind("<Enter>", on_enter)
        w.bind("<Leave>", on_leave)
        w.bind("<Button-1>", on_click)
        
    return btn_frame


def _make_section_title(parent, text, accent=C_VERDE):
    """Título de seção estilo Bebas Neue com barra lateral."""
    f = tk.Frame(parent, bg=C_BG2)
    f.pack(fill="x", pady=(14, 10))
    tk.Frame(f, width=4, bg=accent).pack(side="left", fill="y")
    tk.Label(f, text=text.upper(), font=F_BEBAS, bg=C_BG2, fg=C_AMARELO, padx=8).pack(side="left")
    return f


def _make_subsection(parent, text):
    """Sub-título roxo com linha."""
    f = tk.Frame(parent, bg=C_BG2)
    f.pack(fill="x", pady=(10, 8))
    tk.Label(f, text=text.upper(), font=F_BARLOW, bg=C_BG2, fg=C_ROXO).pack(side="left")
    tk.Frame(f, height=1, bg=C_ROXO).pack(side="left", fill="x", expand=True, padx=(8, 0))
    return f


def _make_row(parent, label_text, accent=C_AMARELO):
    """Linha organizadora para label + controle."""
    row = tk.Frame(parent, bg=C_BG2)
    row.pack(fill="x", padx=0, pady=4)
    lbl = _make_ss_label(row, label_text, accent)
    lbl.pack(side="left", padx=(0, 10))
    
    content = tk.Frame(row, bg=C_BG2)
    content.pack(side="left", fill="x", expand=True)
    return row, content


def _make_slider_row(parent, label_text, from_, to_, init, command, accent=C_AMARELO, fmt="{:.2f}"):
    """Combinação de Row + SelvaSlider + Value Display."""
    row, content = _make_row(parent, label_text, accent)

    val_label = tk.Label(content, text=fmt.format(init), font=F_SPACE, bg=C_PRETO, fg=C_AMARELO, width=7, anchor="e", padx=4, pady=2, highlightthickness=1, highlightbackground=C_MARROM)
    val_label.pack(side="right", padx=(8, 0))

    def _internal_cmd(val):
        val_label.config(text=fmt.format(float(val)))
        if command: command(val)

    slider = SelvaSlider(content, from_=from_, to_=to_, init=init, command=_internal_cmd, accent=accent)
    slider.pack(side="left", fill="x", expand=True)

    return slider, val_label


def _make_combo_row(parent, label_text, values, init, command=None, accent=C_AMARELO):
    """Combinação de Row + Combobox."""
    row, content = _make_row(parent, label_text, accent)
    
    combo_frame = tk.Frame(content, bg=C_BG3, highlightthickness=1, highlightbackground=C_MARROM)
    combo_frame.pack(side="left", fill="x", expand=True)
    tk.Frame(combo_frame, width=3, bg=C_AMARELO).pack(side="left", fill="y")
    
    combo = ttk.Combobox(combo_frame, values=values, state="readonly", font=F_BARLOW)
    combo.set(init)
    combo.pack(side="left", fill="x", expand=True, padx=2, pady=2)
    
    if command:
        combo.bind("<<ComboboxSelected>>", command)
        
    return combo


def _panel(parent, scrollable=False):
    """Container principal para cada aba."""
    if scrollable:
        canvas = tk.Canvas(parent, bg=C_BG2, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=C_BG2)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=parent.winfo_width())
        parent.bind("<Configure>", lambda e: canvas.itemconfig(canvas.find_all()[0], width=e.width))
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=16, pady=4)
        return inner
    
    outer = tk.Frame(parent, bg=C_BG2)
    outer.pack(fill="both", expand=True, padx=16, pady=4)
    return outer


# ─────────────────────────────────────────────────────────────────────────────
#  Painéis do Sintetizador
# ─────────────────────────────────────────────────────────────────────────────

def create_oscillator_controls(parent, config, on_waveform_change, on_pulse, on_ss_voices):
    panel = _panel(parent)
    _make_section_title(panel, "Oscilador", accent=C_VERDE)

    waveform_combo = _make_combo_row(panel, "Waveform", values=[w.value for w in WaveType], init=config.default_waveform.value, command=on_waveform_change)

    pulse_frame = tk.Frame(panel, bg=C_BG2)
    _make_subsection(pulse_frame, "Pulse Width")
    pulse_scale, pulse_label = _make_slider_row(pulse_frame, "Width", from_=0.1, to_=0.9, init=config.pulse_width, command=None, accent=C_AMARELO)
    if on_pulse:
        pulse_scale.command = lambda v: on_pulse(v, pulse_label)

    super_saw_frame = tk.Frame(panel, bg=C_BG2)
    _make_subsection(super_saw_frame, "Super Saw")
    ss_voices, ss_voices_label = _make_slider_row(super_saw_frame, "Voices", from_=2, to_=12, init=config.super_saw_voices, command=None, accent=C_VERDE, fmt="{:.0f}")
    if on_ss_voices:
        ss_voices.command = lambda v: on_ss_voices(int(round(float(v))), ss_voices_label)

    return {
        "frame": panel,
        "waveform_combo": waveform_combo,
        "pulse_frame": pulse_frame,
        "pulse_label": pulse_label,
        "pulse_scale": pulse_scale,
        "super_saw_frame": super_saw_frame,
        "ss_voices_label": ss_voices_label,
        "ss_voices": ss_voices,
    }


def create_envelope_controls(parent, config, on_adsr_change, on_curve_change):
    panel = _panel(parent)
    _make_section_title(panel, "Envelope ADSR", accent=C_AMARELO)

    adsr_params = [
        ("Attack",  "attack",  C_AMARELO,  0.0, 2.0,  config.attack_time),
        ("Decay",   "decay",   C_VERDE,    0.0, 2.0,  config.decay_time),
        ("Sustain", "sustain", C_AZUL,     0.0, 1.0,  config.sustain_level),
        ("Release", "release", C_ROXO,     0.0, 2.0,  config.release_time),
    ]

    sliders, labels = {}, {}
    for name, key, accent, mn, mx, init in adsr_params:
        slider, lbl = _make_slider_row(panel, name, from_=mn, to_=mx, init=init, command=None, accent=accent)
        slider.command = lambda v, k=key, l=lbl: on_adsr_change(k, float(v), l)
        sliders[key] = slider
        labels[key]  = lbl

    _make_subsection(panel, "Curve Type")
    curve_combo = _make_combo_row(panel, "Curva", values=["Linear", "Exponential"], init=config.adsr_curve.value.capitalize(), command=on_curve_change, accent=C_TEXTO2)

    return panel, sliders, labels, curve_combo


def create_modulation_controls(parent, config, on_fm_freq, on_fm_index, on_additive, on_lfo_freq, on_lfo_depth, on_lfo_target, on_hfo_freq, on_hfo_depth, on_hfo_target, on_filter_type, on_filter_freq, on_filter_q):
    panel = _panel(parent, scrollable=True)

    _make_section_title(panel, "Modulação FM")
    fm_freq, fm_freq_label = _make_slider_row(panel, "FM Frequency", 0.1, 5000, config.fm_mod_freq, on_fm_freq, C_AMARELO, "{:.1f}")
    fm_index, fm_index_label = _make_slider_row(panel, "FM Index", 0, 10, config.fm_mod_index, on_fm_index, C_AMARELO, "{:.2f}")
    additive_scale, additive_label = _make_slider_row(panel, "Add. Harmonics", 1, 16, config.additive_harmonics, on_additive, C_VERDE, "{:.0f}")

    _make_subsection(panel, "LFO")
    lfo_freq, lfo_freq_label = _make_slider_row(panel, "LFO Freq", 0.1, 20.0, config.lfo_freq, on_lfo_freq, C_AZUL, "{:.2f} Hz")
    lfo_depth, lfo_depth_label = _make_slider_row(panel, "LFO Depth", 0.0, 1.0, config.lfo_depth, on_lfo_depth, C_AZUL, "{:.2f}")
    lfo_target = _make_combo_row(panel, "LFO Target", ["pitch", "pulse"], config.lfo_target, on_lfo_target, C_AZUL)

    _make_subsection(panel, "HFO")
    hfo_freq, hfo_freq_label = _make_slider_row(panel, "HFO Freq", 20, 8000, config.hfo_freq, on_hfo_freq, C_ROXO, "{:.1f} Hz")
    hfo_depth, hfo_depth_label = _make_slider_row(panel, "HFO Depth", 0.0, 1.0, config.hfo_depth, on_hfo_depth, C_ROXO, "{:.2f}")
    hfo_target = _make_combo_row(panel, "HFO Target", ["pitch"], config.hfo_target, on_hfo_target, C_ROXO)

    _make_section_title(panel, "Filtro", accent=C_VERMELHO)
    filter_frame = tk.Frame(panel, bg=C_BG2)
    filter_frame.pack(fill="x")
    
    filter_type = _make_combo_row(filter_frame, "Type", ["lowpass", "highpass", "bandpass", "notch"], config.filter_type, on_filter_type, C_VERMELHO)
    filter_freq, filter_freq_label = _make_slider_row(filter_frame, "Cutoff (Hz)", 20, 20000, config.filter_freq, on_filter_freq, C_VERMELHO, "{:.0f}")
    filter_q, filter_q_label = _make_slider_row(filter_frame, "Q", 0.1, 10.0, config.filter_q, on_filter_q, C_VERMELHO, "{:.2f}")

    return {
        "frame": panel,
        "fm_freq": fm_freq, "fm_freq_label": fm_freq_label, "fm_index": fm_index, "fm_index_label": fm_index_label,
        "additive_scale": additive_scale, "additive_label": additive_label,
        "lfo_freq": lfo_freq, "lfo_freq_label": lfo_freq_label, "lfo_depth": lfo_depth, "lfo_depth_label": lfo_depth_label, "lfo_target": lfo_target,
        "hfo_freq": hfo_freq, "hfo_freq_label": hfo_freq_label, "hfo_depth": hfo_depth, "hfo_depth_label": hfo_depth_label, "hfo_target": hfo_target,
        "filter_type": filter_type, "filter_freq": filter_freq, "filter_freq_label": filter_freq_label, "filter_q": filter_q, "filter_q_label": filter_q_label,
        "filter_frame": filter_frame,
    }


def create_system_controls(parent, config, on_sample_rate, on_buffer_size, on_polyphony, on_save, on_load, on_wavetable):
    panel = _panel(parent)
    _make_section_title(panel, "Sistema", accent=C_AZUL)

    try:
        import mido
        midi_inputs = mido.get_input_names()
    except ImportError:
        midi_inputs = []

    midi_devices = _make_combo_row(panel, "MIDI Input", midi_inputs or ["— nenhum —"], midi_inputs[0] if midi_inputs else "— nenhum —", None, C_AMARELO)
    polyphony, polyphony_label = _make_slider_row(panel, "Max Poliphony", 1, 16, config.max_polyphony, lambda v: on_polyphony(v, polyphony_label), C_VERDE, "{:.0f}")
    
    _make_subsection(panel, "Hardware")
    sample_rate = _make_combo_row(panel, "Sample Rate", [44100, 48000, 96000], config.sample_rate, on_sample_rate, C_AMARELO)
    buffer_size = _make_combo_row(panel, "Buffer Size", [128, 256, 512, 1024], config.buffer_size, on_buffer_size, C_AMARELO)

    _make_subsection(panel, "Arquivos")
    
    row1 = tk.Frame(panel, bg=C_BG2)
    row1.pack(fill="x", pady=4)
    _styled_button(row1, "▲ Load Wavetable", on_wavetable, C_VERDE).pack(side="left")

    tk.Frame(panel, height=1, bg=C_MARROM).pack(fill="x", pady=12)

    row2 = tk.Frame(panel, bg=C_BG2)
    row2.pack(fill="x")
    _styled_button(row2, "↓ Salvar Configuração", on_save, C_AMARELO).pack(side="left", padx=(0, 8))
    _styled_button(row2, "↑ Carregar Configuração", on_load, C_AMARELO).pack(side="left")

    return {
        "frame": panel, "midi_devices": midi_devices, "polyphony": polyphony, "polyphony_label": polyphony_label,
        "sample_rate": sample_rate, "buffer_size": buffer_size,
    }