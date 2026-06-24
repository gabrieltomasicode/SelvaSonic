import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from queue import Empty, Queue
from synth.audio import visual_queue
from synth.wavetables import generate_bandlimited_tables
from .keyboard import KeyboardMIDI
from synth.synth import MidiSynth
from synth.file_io import save_config, load_config
from synth.config import SynthConfig, WaveType

# Importações de Controles e Lógica
from .controls.envelope_controls import update_adsr, update_adsr_curve
from .controls.modulation_controls import (
    update_lfo_freq, update_lfo_depth, update_lfo_target,
    update_hfo_freq, update_hfo_depth, update_hfo_target,
    update_fm_freq, update_fm_index,
)
from .controls.filter_controls import (
    update_filter_type, update_filter_freq, update_filter_q
)
from .controls.polyphony_controls import update_polyphony

from ui.controls.pulse_controls import update_pulse
from ui.controls.supersaw_controls import update_ss_voices
from ui.controls.aditive_controls import update_additive

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import soundfile as sf

from synth.waveforms import generate_wave
from synth.envelopes import calculate_adsr
from .visuals import generate_static_wave, update_waveform_plot
from .widgets import (
    create_oscillator_controls,
    create_envelope_controls,
    create_modulation_controls,
    create_system_controls,
    _styled_button,
)

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


class FullSynthInterface:
    """
    Interface gráfica SelvaSonic — Estética Brasil/Jamaica refinada.
    """

    def __init__(self, master, synth):
        self.master = master
        self.synth  = synth
        self.config = synth.config
        self.visual_update_id = None
        self.visual_paused    = False
        self.last_keycode     = None
        self.pressed_notes    = set()

        self.keyboard_midi = KeyboardMIDI(self.synth, self.master)
        self.keyboard_midi.status_callback = self.update_note_status
        

        # ── Configuração da Janela Principal ──────────────────────────────────
        self.master.configure(bg=C_BG)
        self.master.title("SelvaSonic Synthesizer")
        
        # O grid agora possui:
        # row 0: Header
        # row 1: Tab Bar
        # row 2: Content Area (Expande)
        # row 3: Waveform Area
        # row 4: Teclado Help
        # row 5: Footer
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(2, weight=1)

        # ── Construção da Interface ───────────────────────────────────────────
        self._build_header()
        self._build_custom_tabs_and_panels()
        self._build_waveform_area()
        self._build_keyboard_help()
        self._build_footer()

        # ── Inicialização e Bindings ──────────────────────────────────────────
        self.update_waveform_visibility()
        self.update_filter_q_visibility()
        self.setup_bindings()
        self.setup_visuals()

        self.synth.start()
        self.keyboard_midi.start()
        self.update_visuals()

    # ─────────────────────────────────────────────────────────────────────────
    #  Header
    # ─────────────────────────────────────────────────────────────────────────
    def _build_header(self):
        hf = tk.Frame(self.master, bg=C_PRETO)
        hf.grid(row=0, column=0, sticky="ew")
        hf.columnconfigure(0, weight=1)

        # Gradiente 4 cores no topo
        stripe = tk.Canvas(hf, height=3, bg=C_PRETO, highlightthickness=0)
        stripe.grid(row=0, column=0, columnspan=2, sticky="ew")
        stripe.bind("<Configure>", lambda e: self._draw_stripe(stripe, e.width))

        # Logo
        logo_frame = tk.Frame(hf, bg=C_PRETO)
        logo_frame.grid(row=1, column=0, sticky="w", padx=16, pady=8)

        # Sombra simulada por deslocamento (offset de 3px)
        lbl_selva_shadow = tk.Label(logo_frame, text="SELVA", font=("Bebas Neue", 22), bg=C_PRETO, fg=C_VERDE)
        lbl_selva_shadow.place(x=3, y=3)
        lbl_selva = tk.Label(logo_frame, text="SELVA", font=("Bebas Neue", 22), bg=C_PRETO, fg=C_AMARELO)
        lbl_selva.pack(side="left")

        lbl_sonic_shadow = tk.Label(logo_frame, text="SONIC", font=("Bebas Neue", 22), bg=C_PRETO, fg=C_AMARELO)
        lbl_sonic_shadow.place(x=lbl_selva.winfo_reqwidth() + 3, y=3)
        lbl_sonic = tk.Label(logo_frame, text="SONIC", font=("Bebas Neue", 22), bg=C_PRETO, fg=C_VERDE)
        lbl_sonic.pack(side="left")

        # Indicador de Status e Nota
        right_frame = tk.Frame(hf, bg=C_PRETO)
        right_frame.grid(row=1, column=1, sticky="e", padx=16, pady=8)

        live_box = tk.Frame(right_frame, bg="#1A7A2E", highlightthickness=1, highlightbackground=C_VERDE)
        live_box.pack(side="left", padx=(0, 10))
        tk.Label(live_box, text="● AO VIVO", font=("Space Mono", 10), bg=C_PRETO, fg=C_VERDE, padx=8, pady=3).pack()

        self.status_label = tk.Label(
            right_frame, text="NOTA: — | FREQ: — Hz | VEL: —",
            font=("Space Mono", 10), bg=C_PRETO, fg=C_TEXTO2
        )
        self.status_label.pack(side="left")

        tk.Frame(hf, height=2, bg=C_AMARELO).grid(row=2, column=0, columnspan=2, sticky="ew")

    @staticmethod
    def _draw_stripe(canvas, width):
        canvas.delete("all")
        seg = max(1, width // 4)
        colors = [C_AMARELO, C_VERDE, C_AZUL, C_VERMELHO]
        for i, c in enumerate(colors):
            canvas.create_rectangle(i * seg, 0, (i + 1) * seg, 3, fill=c, outline="")

    def update_note_status(self, is_on, note=None, freq=None, velocity=None):
        """
        Atualiza os indicadores de Nota, Frequência e Velocity na barra superior (Header).
        """
        if is_on and note is not None:
            # Formata os valores. Freq e Vel com 2 casas decimais.
            status_text = f"NOTA: {note} | FREQ: {freq:.2f} Hz | VEL: {velocity:.2f}"
            # Muda a cor para amarelo para dar destaque visual de "ligado"
            self.status_label.config(text=status_text, fg=C_AMARELO)
        else:
            # Volta para o estado neutro/desligado
            self.status_label.config(text="NOTA: — | FREQ: — Hz | VEL: —", fg=C_TEXTO2)


    # ─────────────────────────────────────────────────────────────────────────
    #  Sistema Personalizado de Abas (Tabs) e Painéis
    # ─────────────────────────────────────────────────────────────────────────
    def _build_custom_tabs_and_panels(self):
        # Tab Bar Container
        self.tab_bar = tk.Frame(self.master, bg=C_PRETO)
        self.tab_bar.grid(row=1, column=0, sticky="ew")
        tk.Frame(self.tab_bar, height=2, bg=C_MARROM).pack(side="bottom", fill="x")

        tab_container = tk.Frame(self.tab_bar, bg=C_PRETO)
        tab_container.pack(side="left", padx=8)

        self.tab_buttons = {}
        self.panels = {}
        self.current_tab = None

        tabs_info = [
            ("osc", "Oscilador"),
            ("adsr", "Envelope ADSR"),
            ("mod", "Modulação/Filtros"),
            ("sys", "Sistema")
        ]

        # Content Area onde os painéis serão embutidos
        self.content_area = tk.Frame(self.master, bg=C_BG, highlightthickness=2, highlightbackground=C_AMARELO)
        self.content_area.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 8))

        # Cria os botões (Canvas com formato de trapézio)
        for tab_id, text in tabs_info:
            btn = tk.Canvas(tab_container, width=150, height=32, bg=C_PRETO, highlightthickness=0, cursor="hand2")
            btn.pack(side="left", padx=1)
            
            # Eventos
            btn.bind("<Button-1>", lambda e, tid=tab_id: self.select_tab(tid))
            btn.bind("<Enter>", lambda e, tid=tab_id: self._on_tab_hover(tid, True))
            btn.bind("<Leave>", lambda e, tid=tab_id: self._on_tab_hover(tid, False))
            
            self.tab_buttons[tab_id] = {"canvas": btn, "text": text}

        # Constrói o conteúdo interno
        self._build_all_panels()
        # Define a aba padrão
        self.select_tab("osc")

    def _on_tab_hover(self, tab_id, hovering):
        if self.current_tab == tab_id: return
        c = self.tab_buttons[tab_id]["canvas"]
        # Atualiza apenas a cor do texto no hover se não estiver ativo
        color = C_AMARELO if hovering else C_TEXTO2
        c.itemconfig("text_element", fill=color)

    def select_tab(self, tab_id):
        self.current_tab = tab_id
        
        # Atualiza a interface gráfica das abas
        for tid, data in self.tab_buttons.items():
            c = data["canvas"]
            text = data["text"]
            c.delete("all")
            
            # Clip-path: polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)
            pts = [6, 0, 150, 0, 144, 32, 0, 32]
            
            if tid == tab_id:
                c.create_polygon(pts, fill=C_AMARELO, outline="")
                c.create_text(75, 16, text=text.upper(), font=("Barlow Condensed", 11, "bold"), fill=C_PRETO, tags="text_element")
            else:
                c.create_text(75, 16, text=text.upper(), font=("Barlow Condensed", 11, "bold"), fill=C_TEXTO2, tags="text_element")

        # Exibe apenas o painel correspondente
        for tid, panel in self.panels.items():
            if tid == tab_id:
                panel.pack(fill="both", expand=True)
            else:
                panel.pack_forget()

    def _build_all_panels(self):
        # ── Aba 1: Oscilador
        self.panels["osc"] = tk.Frame(self.content_area, bg=C_BG2)
        osc_widgets = create_oscillator_controls(
            self.panels["osc"], self.config,
            self.on_waveform_change, None, None
        )
        self.osc_frame        = osc_widgets["frame"]
        self.waveform_combo   = osc_widgets["waveform_combo"]
        self.pulse_frame      = osc_widgets["pulse_frame"]
        self.pulse_label      = osc_widgets["pulse_label"]
        self.pulse_scale      = osc_widgets["pulse_scale"]
        self.super_saw_frame  = osc_widgets["super_saw_frame"]
        self.ss_voices_label  = osc_widgets["ss_voices_label"]
        self.ss_voices        = osc_widgets["ss_voices"]

        # Callbacks customizados para os novos SelvaSliders
        self.pulse_scale.command = lambda v: [
            update_pulse(self.config, v, self.pulse_label),
            self.synth.set_pulse_width(float(v))
        ]
        self.ss_voices.command = lambda v: [
            update_ss_voices(self.config, v, self.ss_voices_label),
            self.synth.set_supersaw_voices(int(float(v))),
            self.update_visuals()
        ]

        # ── Aba 2: Envelope ADSR
        self.panels["adsr"] = tk.Frame(self.content_area, bg=C_BG2)
        env_frame, env_sliders, env_labels, curve_combo = create_envelope_controls(
            self.panels["adsr"], self.config,
            None, # Injetado manualmente abaixo
            lambda e: update_adsr_curve(self.config, self.adsr_curve)
        )
        self.attack_slider  = env_sliders["attack"]
        self.decay_slider   = env_sliders["decay"]
        self.sustain_slider = env_sliders["sustain"]
        self.release_slider = env_sliders["release"]
        self.attack_label   = env_labels["attack"]
        self.decay_label    = env_labels["decay"]
        self.sustain_label  = env_labels["sustain"]
        self.release_label  = env_labels["release"]
        self.adsr_curve     = curve_combo
        
        def _bind_adsr(slider_widget, param_name, label_widget):
            slider_widget.command = lambda v: [
                update_adsr(self.config, param_name, v, label_widget),
                self.update_adsr_param(param_name, v)
            ]
            
        _bind_adsr(self.attack_slider, "attack", self.attack_label)
        _bind_adsr(self.decay_slider, "decay", self.decay_label)
        _bind_adsr(self.sustain_slider, "sustain", self.sustain_label)
        _bind_adsr(self.release_slider, "release", self.release_label)

        # ── Aba 3: Modulação e Filtros
        self.panels["mod"] = tk.Frame(self.content_area, bg=C_BG2)
        mod_widgets = create_modulation_controls(
            self.panels["mod"], self.config,
            None, None, None, None, None, None,
            None, None, None, None, None, None
        )
        mod_widgets["fm_freq"].command = lambda v: [
            update_fm_freq(self.config, v, mod_widgets["fm_freq_label"]),
            setattr(self.synth.config, "fm_mod_freq", float(v))
        ]
        mod_widgets["fm_index"].command = lambda v: [
            update_fm_index(self.config, v, mod_widgets["fm_index_label"]),
            setattr(self.synth.config, "fm_mod_index", float(v))
        ]
        mod_widgets["additive_scale"].command = lambda v: update_additive(self.config, v, mod_widgets["additive_label"])
        
        mod_widgets["lfo_freq"].command = lambda v: update_lfo_freq(self.config, v, mod_widgets["lfo_freq_label"])
        mod_widgets["lfo_depth"].command = lambda v: update_lfo_depth(self.config, v, mod_widgets["lfo_depth_label"])
        mod_widgets["lfo_target"].bind("<<ComboboxSelected>>", lambda e: update_lfo_target(self.config, mod_widgets["lfo_target"]))
        
        mod_widgets["hfo_freq"].command = lambda v: update_hfo_freq(self.config, v, mod_widgets["hfo_freq_label"])
        mod_widgets["hfo_depth"].command = lambda v: update_hfo_depth(self.config, v, mod_widgets["hfo_depth_label"])
        mod_widgets["hfo_target"].bind("<<ComboboxSelected>>", lambda e: update_hfo_target(self.config, mod_widgets["hfo_target"]))
        
        mod_widgets["filter_type"].bind("<<ComboboxSelected>>", lambda e: [
            update_filter_type(self.config, mod_widgets["filter_type"]),
            self.update_filter_q_visibility()
        ])
        mod_widgets["filter_freq"].command = lambda v: [
            update_filter_freq(self.config, v, mod_widgets["filter_freq_label"]),
            setattr(self.synth.config, "filter_freq", float(v))
        ]
        mod_widgets["filter_q"].command = lambda v: [
            update_filter_q(self.config, v, mod_widgets["filter_q_label"]),
            setattr(self.synth.config, "filter_q", float(v))
        ]
        
        self.filter_type    = mod_widgets["filter_type"]
        self.filter_q       = mod_widgets["filter_q"]
        self.filter_q_label = mod_widgets["filter_q_label"]

        # ── Aba 4: Sistema
        self.panels["sys"] = tk.Frame(self.content_area, bg=C_BG2)
        sys_widgets = create_system_controls(
            self.panels["sys"], self.config,
            self.update_sample_rate, self.update_buffer_size,
            self.on_polyphony, self.save_config_dialog,
            self.load_config_dialog, self.load_wavetable
        )
        self.sample_rate     = sys_widgets["sample_rate"]
        self.buffer_size     = sys_widgets["buffer_size"]
        self.polyphony       = sys_widgets["polyphony"]
        self.polyphony_label = sys_widgets["polyphony_label"]

    # ─────────────────────────────────────────────────────────────────────────
    #  Área do gráfico de forma de onda (Matplotlib)
    # ─────────────────────────────────────────────────────────────────────────
    def _build_waveform_area(self):
        wave_container = tk.Frame(self.master, bg=C_PRETO, highlightthickness=1, highlightbackground=C_MARROM)
        wave_container.grid(row=3, column=0, sticky="ew", padx=16, pady=(4, 8))

        title_bar = tk.Frame(wave_container, bg=C_PRETO)
        title_bar.pack(fill="x")
        tk.Frame(title_bar, width=4, bg=C_VERDE).pack(side="left", fill="y")
        tk.Label(title_bar, text="▶ WAVEFORM PREVIEW (AO VIVO)", font=("Bebas Neue", 12), bg=C_PRETO, fg=C_VERDE, padx=8, pady=4).pack(side="left")

        self.fig, self.ax = plt.subplots(figsize=(8, 1.8), facecolor=C_PRETO)
        self._style_axes()

        self.canvas_mpl = FigureCanvasTkAgg(self.fig, master=wave_container)
        self.canvas_mpl.get_tk_widget().pack(fill="x", padx=4, pady=(0, 4))

    def _style_axes(self):
        self.ax.set_facecolor(C_PRETO)
        self.ax.axhline(0, color='#333', lw=0.8, ls='--')
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.ax.spines["bottom"].set_color(C_AMARELO)
        for spine in ["top", "right", "left"]:
            self.ax.spines[spine].set_visible(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_ylim(-1.1, 1.1)

    # ─────────────────────────────────────────────────────────────────────────
    #  Barra de ajuda do Teclado MIDI
    # ─────────────────────────────────────────────────────────────────────────
    def _build_keyboard_help(self):
        kf = tk.Frame(self.master, bg=C_BG2, highlightthickness=1, highlightbackground=C_AZUL)
        kf.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 8))

        tk.Frame(kf, width=4, bg=C_AZUL).pack(side="left", fill="y")
        
        # Estética de tag militar/industrial
        tag = tk.Frame(kf, bg=C_AZUL, padx=10, pady=2)
        tag.pack(side="left", padx=(0, 16))
        tk.Label(tag, text="TECLADO MIDI", font=("Bebas Neue", 12), bg=C_AZUL, fg=C_PRETO).pack()

        hints = [
            ("A–K", "Notas naturais"),
            ("W E T Y U", "Sustenidos"),
            ("– / =", "Oitava ↓ / ↑"),
        ]
        for key, desc in hints:
            tk.Label(kf, text=f"{key}: {desc}", font=("Space Mono", 9), bg=C_BG2, fg=C_TEXTO2, padx=12).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    #  Rodapé
    # ─────────────────────────────────────────────────────────────────────────
    def _build_footer(self):
        footer = tk.Frame(self.master, bg=C_PRETO, highlightthickness=1, highlightbackground=C_VERDE)
        footer.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 16))

        self.pause_button = _styled_button(footer, "⏸ Pausar Visualização", self.toggle_visual, accent=C_VERDE)
        self.pause_button.pack(side="left", padx=8, pady=5)

        tk.Label(footer, text="SelvaSonic v1.0", font=("Space Mono", 10), bg=C_PRETO, fg=C_TEXTO2).pack(side="right", padx=10)

    # ─────────────────────────────────────────────────────────────────────────
    #  Visuals e Atualização Gráfica
    # ─────────────────────────────────────────────────────────────────────────
    def setup_visuals(self):
        self.wave_line = None
        self.wave_fill = None
        self.visual_update_id = None

    def update_visuals(self):
        if self.visual_paused:
            self.visual_update_id = self.master.after(50, self.update_visuals)
            return

        try:
            buffer = None
            while not visual_queue.empty():
                buffer = visual_queue.get_nowait()

            if buffer is not None:
                mix = np.clip(buffer[::4, 0], -1.0, 1.0)

                if self.wave_line is None:
                    self.ax.clear()
                    self._style_axes()
                    duration  = len(mix) / (self.config.sample_rate / 4)
                    self.t_axis = np.linspace(0, duration, len(mix))
                    self.wave_line, = self.ax.plot(self.t_axis, mix, color=C_VERDE, linewidth=1.8)
                    self.wave_fill = self.ax.fill_between(self.t_axis, mix, 0, color=C_VERDE, alpha=0.25)
                    self.canvas_mpl.draw()
                else:
                    self.wave_line.set_ydata(mix)
                    if self.wave_fill in self.ax.collections:
                        self.wave_fill.remove()
                    self.wave_fill = self.ax.fill_between(self.t_axis, mix, 0, color=C_AMARELO, alpha=0.18)
                    self.canvas_mpl.draw_idle()

        except Exception:
            pass  # Prevenção rigorosa contra queda do motor de áudio

        self.visual_update_id = self.master.after(50, self.update_visuals)

    def start_visual_updates(self):
        if self.visual_update_id:
            self.master.after_cancel(self.visual_update_id)
        self.visual_update_id = self.master.after(100, self.update_visuals)

    def toggle_visual(self):
        self.visual_paused = not self.visual_paused
        
        # Atualizar texto no Custom Button exige acessar as children do Frame
        lbl = self.pause_button.winfo_children()[1] 
        new_text = "▶ Retomar Visualização" if self.visual_paused else "⏸ Pausar Visualização"
        lbl.config(text=new_text.upper())

        if self.visual_paused:
            t = np.linspace(0, 0.03, 500)
            phase = 2 * np.pi * 440 * t
            wave  = generate_static_wave(phase, self.config)
            update_waveform_plot(self.ax, t, wave, title="Waveform Preview (Pausado)")
            self.canvas_mpl.draw()

    # ─────────────────────────────────────────────────────────────────────────
    #  Bindings e Visibilidade Condicional
    # ─────────────────────────────────────────────────────────────────────────
    def setup_bindings(self):
        self.waveform_combo.bind("<<ComboboxSelected>>", self.on_waveform_change)
        self.adsr_curve.bind("<<ComboboxSelected>>", lambda e: update_adsr_curve(self.config, self.adsr_curve))
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind_all("<Key>", self.block_keyboard_input)
        self.master.bind("<Control-s>", lambda e: self.save_config_dialog())
        self.master.bind("<Control-o>", lambda e: self.load_config_dialog())

    def block_keyboard_input(self, event):
        if isinstance(self.master.focus_get(), ttk.Combobox):
            if event.keysym not in ("Up", "Down", "Return", "Tab"):
                return "break"

    def update_waveform_visibility(self):
        wave = WaveType(self.waveform_combo.get())
        for frame in (self.pulse_frame, self.super_saw_frame):
            frame.pack_forget()
        if wave == WaveType.PULSE:
            self.pulse_frame.pack(fill="x")
        elif wave == WaveType.SUPER_SAW:
            self.super_saw_frame.pack(fill="x")

    def update_filter_q_visibility(self):
        filter_type = getattr(self, "filter_type", None)
        if filter_type and filter_type.get() == "bandpass":
            self.filter_q.pack(fill="x", expand=True)
            self.filter_q_label.pack(side="right")
        else:
            try:
                self.filter_q.pack_forget()
                self.filter_q_label.pack_forget()
            except Exception:
                pass

    # ─────────────────────────────────────────────────────────────────────────
    #  Callbacks de controle do Sintetizador
    # ─────────────────────────────────────────────────────────────────────────
    def on_waveform_change(self, event):
        new_wave = WaveType(self.waveform_combo.get())
        self.config.default_waveform = new_wave
        self.synth.set_waveform(new_wave)
        self.update_waveform_visibility()

    def on_polyphony(self, value, label=None):
        update_polyphony(self.config, value, label)
        if hasattr(self.synth, "set_polyphony"):
            self.synth.set_polyphony(int(float(value)))

    def update_adsr_param(self, param, value):
        if param in ("attack", "decay", "release"):
            setattr(self.synth.config, f"{param}_time", float(value))
        elif param == "sustain":
            setattr(self.synth.config, "sustain_level", float(value))

    def update_controls_from_config(self):
        self.waveform_combo.set(self.config.default_waveform.value)
        self.pulse_scale.set(self.config.pulse_width)
        self.pulse_label.config(text=f"{self.config.pulse_width:.2f}")
        self.ss_voices.set(self.config.super_saw_voices)
        self.ss_voices_label.config(text=str(self.config.super_saw_voices))

        self.attack_slider.set(self.config.attack_time)
        self.attack_label.config(text=f"{self.config.attack_time:.2f}")
        self.decay_slider.set(self.config.decay_time)
        self.decay_label.config(text=f"{self.config.decay_time:.2f}")
        self.sustain_slider.set(self.config.sustain_level)
        self.sustain_label.config(text=f"{self.config.sustain_level:.2f}")
        self.release_slider.set(self.config.release_time)
        self.release_label.config(text=f"{self.config.release_time:.2f}")
        self.adsr_curve.set(self.config.adsr_curve.value.capitalize())

        self.polyphony.set(self.config.max_polyphony)
        self.polyphony_label.config(text=str(self.config.max_polyphony))
        self.sample_rate.set(self.config.sample_rate)
        self.buffer_size.set(self.config.buffer_size)

        self.update_waveform_visibility()

    # ─────────────────────────────────────────────────────────────────────────
    #  I/O de Configuração e Wavetable
    # ─────────────────────────────────────────────────────────────────────────
    def save_config_dialog(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Configuração SelvaSonic", "*.json")],
            title="Salvar configuração",
        )
        if path:
            save_config(self.config, filename=path)
            messagebox.showinfo("SelvaSonic", "Configuração salva com sucesso!")

    def load_config_dialog(self):
        path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("Configuração SelvaSonic", "*.json")],
            title="Carregar configuração",
        )
        if path:
            old_rate = self.config.sample_rate
            load_config(self.config, filename=path)
            if self.config.sample_rate != old_rate:
                self.config.bandlimited_tables = generate_bandlimited_tables(self.config.sample_rate)
                self.restart_audio_stream()
            self.synth.config = self.config
            self.update_controls_from_config()
            messagebox.showinfo("SelvaSonic", "Configuração carregada com sucesso!")

    def load_wavetable(self):
        path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")], title="Carregar Wavetable")
        if path:
            try:
                data, _ = sf.read(path)
                if data is None or len(data) == 0:
                    raise ValueError("Arquivo WAV inválido ou vazio.")
                self.config.wavetable = data
                self.synth.config.wavetable = data
            except Exception as e:
                messagebox.showerror("SelvaSonic", f"Erro ao carregar wavetable:\n{e}")

    # ─────────────────────────────────────────────────────────────────────────
    #  Gestão de Áudio
    # ─────────────────────────────────────────────────────────────────────────
    def update_sample_rate(self, event):
        try:
            self.config.sample_rate = int(self.sample_rate.get())
            self.config.bandlimited_tables = generate_bandlimited_tables(self.config.sample_rate)
            self.restart_audio_stream()
        except Exception as e:
            print(f"Erro ao atualizar sample rate: {e}")

    def update_buffer_size(self, event):
        try:
            self.config.buffer_size = int(self.buffer_size.get())
            self.restart_audio_stream()
        except Exception as e:
            print(f"Erro ao atualizar buffer size: {e}")

    def restart_audio_stream(self):
        try:
            if self.synth: self.synth.stop()
            self.synth = MidiSynth(self.config)
            self.synth.start()
            self.keyboard_midi.synth = self.synth
        except Exception as e:
            print(f"Erro ao reiniciar stream de áudio: {e}")

    def on_close(self):
            # 1. Para os processos visuais e de áudio
            if self.visual_update_id:
                self.master.after_cancel(self.visual_update_id)
                self.visual_update_id = None
            if hasattr(self, "synth") and self.synth:
                self.synth.stop()
                if hasattr(self.synth, "on_close"):
                    self.synth.on_close()
            if hasattr(self, "keyboard_midi") and self.keyboard_midi:
                if hasattr(self.keyboard_midi, "stop"):
                    self.keyboard_midi.stop()
            
            # 2. Destrói a interface gráfica
            self.master.destroy()

            # 3. Executa a limpeza do cache silenciosamente no background
            #lazy_load = True
            try:
                import os
                import sys
                
                # Localiza a raiz do projeto (pasta SelvaSonicScripts)
                root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                # Adiciona ao sys.path para garantir que consegue achar o cleancache.py
                if root_dir not in sys.path:
                    sys.path.append(root_dir)
                
                # Importa e roda o limpador
                from cleancache import remove_pycache_and_pyc
                remove_pycache_and_pyc(root_dir)
                print("[SelvaSonic] Encerrado com sucesso. Cache limpo.")
                
            except ImportError:
                print("[SelvaSonic] Encerrado. (Aviso: script cleancache.py não encontrado para limpeza automática).")
            except Exception as e:
                print(f"[SelvaSonic] Encerrado. (Aviso na limpeza de cache: {e})")