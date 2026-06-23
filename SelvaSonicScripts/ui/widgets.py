import tkinter as tk
from tkinter import ttk
from synth.config import SynthConfig, WaveType

# ─────────────────────────────────────────────────────────────────────────────
#  Paleta SelvaSonic
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
#  Helpers de layout reutilizáveis
# ─────────────────────────────────────────────────────────────────────────────
class CustomSlider(tk.Canvas):
    def __init__(self, parent, width=200, height=20, accent=C_AMARELO):
        super().__init__(parent, width=width, height=height, bg=C_BG2, highlightthickness=0)
        self.accent = accent
        self.value = 0.5
        self.bind("<Button-1>", self._on_drag)
        self.bind("<B1-Motion>", self._on_drag)
        self.draw()

    def draw(self):
        self.delete("all")
        # Desenha track
        self.create_rectangle(0, 8, 200, 12, fill=C_BG3, outline="")
        # Desenha progresso
        self.create_rectangle(0, 8, 200 * self.value, 12, fill=self.accent, outline="")
        # Desenha Thumb
        self.create_rectangle(200 * self.value - 7, 0, 200 * self.value + 7, 20, fill=self.accent)

    def _on_drag(self, event):
        self.value = max(0, min(1, event.x / 200))
        self.draw()

def create_arrow_label(parent, text, bg=C_MARROM, fg=C_AMARELO):
    """Cria a label com terminação em triângulo."""
    frame = tk.Frame(parent, bg=bg)
    
    # Texto
    lbl = tk.Label(frame, text=text.upper(), font=("Helvetica", 8, "bold"),
                   bg=bg, fg=fg, padx=8, pady=3)
    lbl.pack(side="left")
    
    # Triângulo (Seta)
    canvas = tk.Canvas(frame, width=8, height=22, bg=bg, highlightthickness=0)
    canvas.pack(side="left")
    canvas.create_polygon(0, 0, 8, 11, 0, 22, fill=bg, outline="")
    
    return frame

def _make_section_bar(parent, text, accent=C_AMARELO):
    """Faixa de título de seção: borda esquerda colorida + texto em caixa alta."""
    bar = tk.Frame(parent, bg=C_BG2)
    bar.pack(fill="x", pady=(10, 4))
    tk.Frame(bar, width=4, bg=accent).pack(side="left", fill="y")
    tk.Label(
        bar, text=text.upper(),
        font=("Helvetica", 10, "bold"),
        bg=C_BG2, fg=accent,
        padx=8, pady=3
    ).pack(side="left")
    return bar


def _make_subsection(parent, text):
    """Sub-título roxo com linha separadora."""
    frame = tk.Frame(parent, bg=C_BG2)
    frame.pack(fill="x", pady=(8, 2))
    tk.Label(
        frame, text=text.upper(),
        font=("Helvetica", 8, "bold"),
        bg=C_BG2, fg=C_ROXO,
        padx=6
    ).pack(side="left")
    tk.Frame(frame, height=1, bg=C_ROXO).pack(side="left", fill="x", expand=True, padx=(4, 6))
    return frame


def _make_row(parent, label_text, accent=C_AMARELO):
    """
    Linha com label estilo 'placa' (fundo marrom, seta) + área para slider/combo.
    Retorna (row_frame, content_frame).
    """
    row = tk.Frame(parent, bg=C_BG2)
    row.pack(fill="x", padx=8, pady=3)

    # Label estilo placa com clip visual (triângulo no final via padding)
    lbl_frame = tk.Frame(row, bg=C_MARROM)
    lbl_frame.pack(side="left")
    tk.Label(
        lbl_frame, text=label_text.upper(),
        font=("Helvetica", 8, "bold"),
        bg=C_MARROM, fg=accent,
        padx=8, pady=3,
        width=14, anchor="w"
    ).pack(side="left")
    # "Seta" visual: pequeno canvas triangular
    arrow = tk.Canvas(row, width=10, height=22, bg=C_BG2, highlightthickness=0)
    arrow.pack(side="left")
    arrow.create_polygon(0, 0, 10, 11, 0, 22, fill=C_MARROM, outline="")

    content = tk.Frame(row, bg=C_BG2)
    content.pack(side="left", fill="x", expand=True)
    return row, content


def _make_slider_row(parent, label_text, from_, to_, init, command,
                     accent=C_AMARELO, fmt="{:.2f}"):
    """
    Linha completa: label + slider estilizado + label de valor.
    Retorna (slider_widget, value_label).
    """
    _, content = _make_row(parent, label_text, accent)

    val_label = tk.Label(
        content, text=fmt.format(init),
        font=("Courier", 9, "bold"),
        bg=C_PRETO, fg=accent,
        width=7, anchor="e", padx=4, pady=2,
        relief="flat"
    )
    val_label.pack(side="right", padx=(4, 6))

    slider = tk.Scale(
        content,
        from_=from_, to=to_,
        orient="horizontal",
        showvalue=False,
        resolution=(to_ - from_) / 1000,
        bg=C_BG2,
        fg=accent,
        troughcolor=C_BG3,
        activebackground=accent,
        highlightthickness=1,
        highlightbackground=C_MARROM,
        sliderlength=14,
        bd=0,
    )
    slider.set(init)
    slider.pack(side="left", fill="x", expand=True, padx=(0, 4))

    def _update(v):
        val_label.config(text=fmt.format(float(v)))
        if command:
            command(v)

    slider.config(command=_update)
    return slider, val_label


def _make_combo_row(parent, label_text, values, init, command=None, accent=C_AMARELO):
    """Linha com label + combobox estilizado."""
    _, content = _make_row(parent, label_text, accent)
    combo = ttk.Combobox(content, values=values, state="readonly",
                         font=("Helvetica", 9))
    combo.set(init)
    combo.pack(side="left", fill="x", expand=True, padx=(0, 6), pady=2)
    if command:
        combo.bind("<<ComboboxSelected>>", command)
    return combo


def _panel(parent, scrollable=False):
    """Frame interno de painel com fundo escuro."""
    outer = tk.Frame(parent, bg=C_BG2)
    outer.pack(fill="both", expand=True)
    if scrollable:
        canvas = tk.Canvas(outer, bg=C_BG2, highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=C_BG2)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        return inner
    return outer


# ─────────────────────────────────────────────────────────────────────────────
#  Oscilador
# ─────────────────────────────────────────────────────────────────────────────

def create_oscillator_controls(parent, config, on_waveform_change, on_pulse, on_ss_voices):
    """
    Cria o painel de controles do Oscilador com a estética SelvaSonic.

    Parâmetros:
        parent: Widget pai.
        config: Objeto SynthConfig.
        on_waveform_change: Callback <<ComboboxSelected>>.
        on_pulse: Callback(value, label) para pulse width.
        on_ss_voices: Callback(value, label) para vozes Super Saw.

    Retorna:
        dict com chaves: frame, waveform_combo, pulse_frame, pulse_label,
                         pulse_scale, super_saw_frame, ss_voices_label, ss_voices.
    """
    panel = _panel(parent)

    _make_section_bar(panel, "Oscilador")

    # ── Waveform ──────────────────────────────────────────────────────────────
    waveform_combo = _make_combo_row(
        panel, "Waveform",
        values=[w.value for w in WaveType],
        init=config.default_waveform.value,
        command=on_waveform_change,
        accent=C_AMARELO
    )

    # ── Pulse Width ───────────────────────────────────────────────────────────
    pulse_frame = tk.Frame(panel, bg=C_BG2)
    pulse_frame.pack(fill="x")
    _make_subsection(pulse_frame, "Pulse Width")
    pulse_scale, pulse_label = _make_slider_row(
        pulse_frame, "Width",
        from_=0.1, to_=0.9, init=config.pulse_width,
        command=None,           # sobrescrito em interface.py
        accent=C_AMARELO
    )
    if on_pulse:
        pulse_scale.config(command=lambda v: on_pulse(v, pulse_label))

    # ── Super Saw ─────────────────────────────────────────────────────────────
    super_saw_frame = tk.Frame(panel, bg=C_BG2)
    super_saw_frame.pack(fill="x")
    _make_subsection(super_saw_frame, "Super Saw")
    ss_voices, ss_voices_label = _make_slider_row(
        super_saw_frame, "Voices",
        from_=2, to_=12, init=config.super_saw_voices,
        command=None,
        accent=C_VERDE, fmt="{:.0f}"
    )
    if on_ss_voices:
        ss_voices.config(command=lambda v: on_ss_voices(int(round(float(v))), ss_voices_label))

    # grid shim para compatibilidade com interface.py que faz .grid_remove()
    pulse_frame.grid_propagate(False)
    super_saw_frame.grid_propagate(False)

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


# ─────────────────────────────────────────────────────────────────────────────
#  Envelope ADSR
# ─────────────────────────────────────────────────────────────────────────────

def create_envelope_controls(parent, config, on_adsr_change, on_curve_change):
    """
    Cria o painel de Envelope ADSR com estética SelvaSonic.

    Retorna:
        (frame, sliders_dict, labels_dict, curve_combo)
    """
    frame = tk.Frame(parent, bg=C_BG2)
    frame.pack(fill="both", expand=True)

    _make_section_bar(frame, "Envelope ADSR")

    adsr_params = [
        ("Attack",  "attack",  C_AMARELO,  0.0, 2.0,  config.attack_time),
        ("Decay",   "decay",   C_VERDE,    0.0, 2.0,  config.decay_time),
        ("Sustain", "sustain", C_AZUL,     0.0, 1.0,  config.sustain_level),
        ("Release", "release", C_ROXO,     0.0, 2.0,  config.release_time),
    ]

    sliders = {}
    labels  = {}

    for name, key, accent, mn, mx, init in adsr_params:
        slider, lbl = _make_slider_row(
            frame, name,
            from_=mn, to_=mx, init=init,
            command=lambda v, k=key, l=None: None,   # placeholder
            accent=accent
        )
        # Reconecta o command correto com a referência ao label real
        slider.config(command=lambda v, k=key, l=lbl: on_adsr_change(k, float(v), l))
        sliders[key] = slider
        labels[key]  = lbl

    # ── Curve Type ────────────────────────────────────────────────────────────
    _make_subsection(frame, "Curva")
    curve_combo = _make_combo_row(
        frame, "Curve Type",
        values=["Linear", "Exponential"],
        init=config.adsr_curve.value.capitalize(),
        command=on_curve_change,
        accent=C_TEXTO2
    )

    return frame, sliders, labels, curve_combo


# ─────────────────────────────────────────────────────────────────────────────
#  Modulação / Filtros
# ─────────────────────────────────────────────────────────────────────────────

def create_modulation_controls(
    parent, config,
    on_fm_freq, on_fm_index, on_additive,
    on_lfo_freq, on_lfo_depth, on_lfo_target,
    on_hfo_freq, on_hfo_depth, on_hfo_target,
    on_filter_type, on_filter_freq, on_filter_q
):
    """
    Cria o painel de Modulação e Filtros com estética SelvaSonic.

    Retorna:
        dict com todas as referências de widget necessárias para interface.py.
    """
    panel = _panel(parent, scrollable=True)

    # ── FM ────────────────────────────────────────────────────────────────────
    _make_section_bar(panel, "Modulação FM")

    fm_freq, fm_freq_label = _make_slider_row(
        panel, "FM Frequency",
        from_=0.1, to_=5000, init=config.fm_mod_freq,
        command=on_fm_freq, accent=C_AMARELO, fmt="{:.1f}"
    )
    fm_index, fm_index_label = _make_slider_row(
        panel, "FM Index",
        from_=0, to_=10, init=config.fm_mod_index,
        command=on_fm_index, accent=C_AMARELO, fmt="{:.2f}"
    )
    additive_scale, additive_label = _make_slider_row(
        panel, "Add. Harmonics",
        from_=1, to_=16, init=config.additive_harmonics,
        command=on_additive, accent=C_VERDE, fmt="{:.0f}"
    )

    # ── LFO ───────────────────────────────────────────────────────────────────
    _make_section_bar(panel, "LFO", accent=C_AZUL)

    lfo_freq, lfo_freq_label = _make_slider_row(
        panel, "LFO Freq",
        from_=0.1, to_=20.0, init=config.lfo_freq,
        command=on_lfo_freq, accent=C_AZUL, fmt="{:.2f} Hz"
    )
    lfo_depth, lfo_depth_label = _make_slider_row(
        panel, "LFO Depth",
        from_=0.0, to_=1.0, init=config.lfo_depth,
        command=on_lfo_depth, accent=C_AZUL, fmt="{:.2f}"
    )
    lfo_target = _make_combo_row(
        panel, "LFO Target",
        values=["pitch", "pulse"],
        init=config.lfo_target,
        command=on_lfo_target, accent=C_AZUL
    )

    # ── HFO ───────────────────────────────────────────────────────────────────
    _make_section_bar(panel, "HFO", accent=C_ROXO)

    hfo_freq, hfo_freq_label = _make_slider_row(
        panel, "HFO Freq",
        from_=20, to_=8000, init=config.hfo_freq,
        command=on_hfo_freq, accent=C_ROXO, fmt="{:.1f} Hz"
    )
    hfo_depth, hfo_depth_label = _make_slider_row(
        panel, "HFO Depth",
        from_=0.0, to_=1.0, init=config.hfo_depth,
        command=on_hfo_depth, accent=C_ROXO, fmt="{:.2f}"
    )
    hfo_target = _make_combo_row(
        panel, "HFO Target",
        values=["pitch"],
        init=config.hfo_target,
        command=on_hfo_target, accent=C_ROXO
    )

    # ── Filtro ────────────────────────────────────────────────────────────────
    _make_section_bar(panel, "Filtro", accent=C_VERMELHO)

    filter_frame = tk.Frame(panel, bg=C_BG2)
    filter_frame.pack(fill="x")

    filter_type = _make_combo_row(
        filter_frame, "Type",
        values=["lowpass", "highpass", "bandpass"],
        init=config.filter_type,
        command=on_filter_type, accent=C_VERMELHO
    )
    filter_freq, filter_freq_label = _make_slider_row(
        filter_frame, "Cutoff (Hz)",
        from_=1, to_=config.sample_rate // 2 - 1,
        init=config.filter_freq,
        command=on_filter_freq, accent=C_VERMELHO, fmt="{:.0f}"
    )
    filter_q, filter_q_label = _make_slider_row(
        filter_frame, "Q",
        from_=0.1, to_=10.0, init=config.filter_q,
        command=on_filter_q, accent=C_VERMELHO, fmt="{:.2f}"
    )

    return {
        "frame": panel,
        "fm_freq": fm_freq, "fm_freq_label": fm_freq_label,
        "fm_index": fm_index, "fm_index_label": fm_index_label,
        "additive_scale": additive_scale, "additive_label": additive_label,
        "lfo_freq": lfo_freq, "lfo_freq_label": lfo_freq_label,
        "lfo_depth": lfo_depth, "lfo_depth_label": lfo_depth_label,
        "lfo_target": lfo_target,
        "hfo_freq": hfo_freq, "hfo_freq_label": hfo_freq_label,
        "hfo_depth": hfo_depth, "hfo_depth_label": hfo_depth_label,
        "hfo_target": hfo_target,
        "filter_type": filter_type,
        "filter_freq": filter_freq, "filter_freq_label": filter_freq_label,
        "filter_q": filter_q, "filter_q_label": filter_q_label,
        "filter_frame": filter_frame,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Sistema
# ─────────────────────────────────────────────────────────────────────────────

def create_system_controls(
    parent, config,
    on_sample_rate, on_buffer_size, on_polyphony,
    on_save, on_load, on_wavetable
):
    """
    Cria o painel de Sistema com estética SelvaSonic.

    Retorna:
        dict com: frame, midi_devices, polyphony, polyphony_label,
                  sample_rate, buffer_size.
    """
    panel = _panel(parent)

    _make_section_bar(panel, "Sistema")

    # ── MIDI Input ────────────────────────────────────────────────────────────
    try:
        import mido
        midi_inputs = mido.get_input_names()
    except ImportError:
        midi_inputs = []

    midi_devices = _make_combo_row(
        panel, "MIDI Input",
        values=midi_inputs or ["— nenhum —"],
        init=midi_inputs[0] if midi_inputs else "— nenhum —",
        accent=C_AMARELO
    )

    # ── Polifonia ─────────────────────────────────────────────────────────────
    polyphony, polyphony_label = _make_slider_row(
        panel, "Max Poliphony",
        from_=1, to_=64, init=config.max_polyphony,
        command=lambda v: on_polyphony(v, polyphony_label),
        accent=C_VERDE, fmt="{:.0f}"
    )

    # ── Load Wavetable ────────────────────────────────────────────────────────
    _make_subsection(panel, "Wavetable")
    btn_row = tk.Frame(panel, bg=C_BG2)
    btn_row.pack(fill="x", padx=10, pady=4)
    _styled_button(btn_row, "▲  Load Wavetable", on_wavetable, accent=C_VERDE).pack(side="left")

    # ── Sample Rate ───────────────────────────────────────────────────────────
    _make_subsection(panel, "Hardware")
    sample_rate = _make_combo_row(
        panel, "Sample Rate (Hz)",
        values=[22050, 32000, 44100, 48000, 96000],
        init=config.sample_rate,
        command=on_sample_rate, accent=C_AMARELO
    )
    buffer_size = _make_combo_row(
        panel, "Buffer Size",
        values=[32, 64, 128, 256, 512],
        init=config.buffer_size,
        command=on_buffer_size, accent=C_AMARELO
    )

    # ── Salvar / Carregar ─────────────────────────────────────────────────────
    _make_subsection(panel, "Configuração")
    cfg_row = tk.Frame(panel, bg=C_BG2)
    cfg_row.pack(fill="x", padx=10, pady=6)
    _styled_button(cfg_row, "↓  Salvar", on_save, accent=C_AMARELO).pack(side="left", padx=(0, 8))
    _styled_button(cfg_row, "↑  Carregar", on_load, accent=C_TEXTO2).pack(side="left")

    return {
        "frame": panel,
        "midi_devices": midi_devices,
        "polyphony": polyphony,
        "polyphony_label": polyphony_label,
        "sample_rate": sample_rate,
        "buffer_size": buffer_size,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Botão estilizado (helper interno)
# ─────────────────────────────────────────────────────────────────────────────

def _styled_button(parent, text, command, accent=C_AMARELO):
    """Botão com borda esquerda colorida e hover amarelo/preto."""
    btn = tk.Button(
        parent, text=text.upper(),
        command=command,
        font=("Helvetica", 8, "bold"),
        bg=C_BG3, fg=C_TEXTO,
        activebackground=accent, activeforeground=C_PRETO,
        relief="flat",
        bd=0,
        padx=12, pady=5,
        highlightthickness=2,
        highlightbackground=accent,
        cursor="hand2"
    )
    return btn
