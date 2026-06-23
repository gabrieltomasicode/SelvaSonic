import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from queue import Empty, Queue
from synth.audio import visual_queue
from synth.wavetables import generate_bandlimited_tables
from .keyboard import KeyboardMIDI
from synth.synth import MidiSynth
from synth.file_io import save_config, load_config
from synth.config import SynthConfig, WaveType
from .controls.envelope_controls import update_adsr,update_adsr_curve
from .controls.modulation_controls import update_lfo_freq, update_lfo_depth, update_lfo_target
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .controls.polyphony_controls import update_polyphony
import soundfile as sf
from synth.waveforms import generate_wave
from synth.envelopes import calculate_adsr
from ui.controls.pulse_controls import update_pulse
from ui.controls.supersaw_controls import update_ss_voices
from .visuals import generate_static_wave, update_waveform_plot
from .widgets import (
    create_oscillator_controls,
    create_envelope_controls,
    create_modulation_controls,
    create_system_controls,
)
from ui.controls.pulse_controls import update_pulse
from ui.controls.supersaw_controls import update_ss_voices
from ui.controls.aditive_controls import update_additive
from ui.controls.envelope_controls import update_adsr
from ui.controls.modulation_controls import (
    update_lfo_freq, update_lfo_depth, update_lfo_target,
    update_hfo_freq, update_hfo_depth, update_hfo_target, update_fm_freq, update_fm_index,
)
from ui.controls.filter_controls import (
    update_filter_type, update_filter_freq, update_filter_q
)
from ui.controls.polyphony_controls import update_polyphony

class FullSynthInterface:
    """
    Interface gráfica para controle do sintetizador.

    Atributos:
        master: Janela principal do Tkinter.
        config: Configuração do sintetizador.
        synth: Instância do sintetizador MIDI.
        keyboard_midi: Instância do teclado MIDI virtual.
    """
    def __init__(self, master, synth):
        self.master = master
        self.synth = synth
        self.visual_update_id = None
        self.config = synth.config
        
        self.visual_paused = False
        self.last_keycode = None
        self.pressed_notes = set()

        # Inicia teclado
        self.keyboard_midi = KeyboardMIDI(self.synth, self.master)

        # 1. Aplica o CSS
        self.setup_styles()
        
        # 2. Desenha o Header (Gradiente e Logo)
        self.create_header()

        # 3. Cria o container principal do meio da tela
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)

        # 4. Criação das Abas, Controles e Gráfico...
        self.create_widgets()
        self.setup_visuals()
        self.setup_bindings()
        
        self.current_waveform = self.config.default_waveform
        self.create_keyboard_help()

        self.update_visuals()
        self.synth.start()
        self.keyboard_midi.start()

    def setup_styles(self):
        """
        Aplica a estética do protótipo HTML (Brasil + Jamaica) ao Tkinter.
        """
        style = ttk.Style()
        style.theme_use('clam')

        # Variáveis CSS do seu protótipo
        self.c_amarelo = "#F5C800"
        self.c_verde = "#1A7A2E"
        self.c_marrom = "#5C3317"
        self.c_azul = "#1B4FD8"
        self.c_vermelho = "#C8281E"
        self.c_preto = "#0A0A0A"
        self.c_bg = "#111111"
        self.c_bg2 = "#1A1A1A"
        self.c_bg3 = "#222222"
        self.c_texto = "#E8E0C8"
        self.c_texto2 = "#A09880"

        # Fundo geral do app
        self.master.configure(bg=self.c_bg)

        # Frames e Painéis
        style.configure('TFrame', background=self.c_bg)
        style.configure('Panel.TFrame', background=self.c_bg2)
        style.configure('TLabelframe', background=self.c_bg2, bordercolor=self.c_marrom, borderwidth=1)
        style.configure('TLabelframe.Label', background=self.c_bg2, foreground=self.c_amarelo, font=("Helvetica", 11, "bold"))

        # Abas (Notebook)
        style.configure('TNotebook', background=self.c_bg, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.c_preto, foreground=self.c_texto2, padding=[20, 5], font=("Helvetica", 10, "bold"))
        style.map('TNotebook.Tab', 
                  background=[('selected', self.c_amarelo)], 
                  foreground=[('selected', self.c_preto)])

        # Textos e Labels
        style.configure('TLabel', background=self.c_bg2, foreground=self.c_texto, font=("Helvetica", 9))
        
        # Sliders
        style.configure('Horizontal.TScale', background=self.c_bg2, troughcolor=self.c_bg3, borderwidth=1, bordercolor=self.c_marrom)

        # Botões
        style.configure('TButton', background=self.c_bg3, foreground=self.c_texto, borderwidth=1, bordercolor=self.c_marrom, font=("Helvetica", 9, "bold"))
        style.map('TButton', 
                  background=[('active', self.c_amarelo)], 
                  foreground=[('active', self.c_preto)])

        # Combobox
        style.configure('TCombobox', fieldbackground=self.c_bg3, background=self.c_bg3, foreground=self.c_texto, bordercolor=self.c_marrom)
    
    def create_header(self):
        """
        Cria o topo da aplicação usando grid (compatível com o resto da interface).
        """
        # Criamos um Frame para o Header para que ele fique isolado
        header_frame = ttk.Frame(self.master)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # O Canvas agora fica dentro desse Frame
        header = tk.Canvas(header_frame, height=50, bg=self.c_preto, highlightthickness=0)
        header.pack(fill="x") # pack aqui é seguro pois está dentro de um frame que usa grid

        # Desenho do gradiente e logo...
        w = 1000 
        header.create_rectangle(0, 0, w*0.25, 3, fill=self.c_amarelo, outline="")
        header.create_rectangle(w*0.25, 0, w*0.5, 3, fill=self.c_verde, outline="")
        header.create_rectangle(w*0.5, 0, w*0.75, 3, fill=self.c_azul, outline="")
        header.create_rectangle(w*0.75, 0, w, 3, fill=self.c_vermelho, outline="")

        header.create_text(20, 25, text="SELVA", fill=self.c_amarelo, font=("Helvetica", 18, "bold"), anchor="w")
        header.create_text(90, 25, text="SONIC", fill=self.c_verde, font=("Helvetica", 18, "bold"), anchor="w")
        
        header.create_rectangle(200, 15, 270, 35, fill="#0a2a12", outline=self.c_verde)
        header.create_text(210, 25, text="● AO VIVO", fill=self.c_verde, font=("Courier", 9, "bold"), anchor="w")

    def update_controls_from_config(self):
        """
        Atualiza os controles da interface gráfica com base na configuração atual do sintetizador.

        Notas:
            - Sincroniza sliders, labels e combos com os valores do objeto de configuração.
        """
        # Oscilador
        self.waveform_combo.set(self.config.default_waveform.value)
        self.pulse_scale.set(self.config.pulse_width)
        self.pulse_label.config(text=f"{self.config.pulse_width:.2f}")
        self.ss_voices.set(self.config.super_saw_voices)
        self.ss_voices_label.config(text=str(self.config.super_saw_voices))

        # Envelope ADSR
        self.attack_slider.set(self.config.attack_time)
        self.attack_label.config(text=f"{self.config.attack_time:.2f}")
        self.decay_slider.set(self.config.decay_time)
        self.decay_label.config(text=f"{self.config.decay_time:.2f}")
        self.sustain_slider.set(self.config.sustain_level)
        self.sustain_label.config(text=f"{self.config.sustain_level:.2f}")
        self.release_slider.set(self.config.release_time)
        self.release_label.config(text=f"{self.config.release_time:.2f}")
        self.adsr_curve.set(self.config.adsr_curve.value.capitalize())

        # Polyphony, Sample Rate, Buffer Size
        self.polyphony.set(self.config.max_polyphony)
        self.polyphony_label.config(text=str(self.config.max_polyphony))
        self.sample_rate.set(self.config.sample_rate)
        self.buffer_size.set(self.config.buffer_size)

        # Atualize visibilidade dos controles condicionais
        self.update_waveform_visibility()

    def save_config_dialog(self):
        """
        Abre um diálogo para salvar a configuração atual do sintetizador em um arquivo JSON.

        Notas:
            - Exibe mensagem de confirmação ou erro ao usuário.
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Configuração do Sintetizador", "*.json")],
            title="Salvar configuração como"
        )
        if file_path:
            save_config(self.config, filename=file_path)
            messagebox.showinfo("Configuração", "Configuração salva com sucesso!")
        else:
            print("Salvamento cancelado pelo usuário.")

    def load_config_dialog(self):
        """
        Abre um diálogo para carregar uma configuração de sintetizador de um arquivo JSON.

        Notas:
            - Atualiza a interface e o sintetizador com a configuração carregada.
        """
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("Configuração do Sintetizador", "*.json")],
            title="Carregar configuração"
        )
        if file_path:
            print("Carregando configuração de:", file_path)
            
            # 🔄 NOVO: Guardamos o sample_rate que está a rodar atualmente antes de carregar o novo
            old_sample_rate = self.config.sample_rate
            
            load_config(self.config, filename=file_path)
            
            # 🔄 NOVO: Se o ficheiro JSON alterou o sample_rate, recalculamos as Wavetables limitadas em banda
            if self.config.sample_rate != old_sample_rate:
                print(f"🔄 Taxa de amostragem alterada de {old_sample_rate}Hz para {self.config.sample_rate}Hz. Recalculando as tabelas...")
                from synth.wavetables import generate_bandlimited_tables
                
                # Força a atualização do cache de ondas limpas de aliasing
                self.config.bandlimited_tables = generate_bandlimited_tables(self.config.sample_rate)
                
                # Como a taxa de amostragem mudou, reiniciamos também a placa de som (hardware stream)
                self.restart_audio_stream()
            
            self.synth.config = self.config
            self.update_controls_from_config()
            messagebox.showinfo("Configuração", "Configuração carregada com sucesso!")
        else:
            print("Carregamento cancelado pelo usuário.")
    
    def on_pulse(self, value, label=None):
        """
        Callback para atualização do parâmetro pulse width.

        Parâmetros:
            value: Novo valor de pulse width.
            label: Label opcional para exibir o valor.
        """
        update_pulse(self.config, value, label or self.pulse_label)

    def on_ss_voices(self, value, label=None):
        """
        Callback para atualização do número de vozes Super Saw.

        Parâmetros:
            value: Novo valor de vozes.
            label: Label opcional para exibir o valor.
        """
        update_ss_voices(self.config, value, label or self.ss_voices_label)
    
    def on_polyphony(self, value, label=None):
        """
        Callback para atualização da polifonia máxima.

        Parâmetros:
            value: Novo valor de polifonia.
            label: Label opcional para exibir o valor.
        """
        update_polyphony(self.config, value, label)
        if hasattr(self.synth, "set_polyphony"):
            self.synth.set_polyphony(value)

    def update_adsr_param(self, param, value):
        """
        Atualiza o parâmetro ADSR no sintetizador em tempo real.

        Parâmetros:
            param: Nome do parâmetro ('attack', 'decay', 'sustain', 'release').
            value: Novo valor do parâmetro.
        """
        if param in ["attack", "decay", "release"]:
            setattr(self.synth.config, f"{param}_time", float(value))
        elif param == "sustain":
            setattr(self.synth.config, "sustain_level", float(value))

    def create_keyboard_help(self):
        """
        Cria uma seção de ajuda para o teclado MIDI virtual.

        Notas:
            - Exibe informações sobre as teclas do teclado virtual.
        """
        help_frame = ttk.LabelFrame(self.master, text="Teclado MIDI")
        help_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        keys = [
            "A-K: Notas naturais",
            "W,E,T,Y,U: Sustenidos",
            "Pressione as teclas para tocar"
        ]
        
        for i, text in enumerate(keys):
            ttk.Label(help_frame, text=text).grid(row=i, column=0, sticky='w')

    def create_widgets(self):
        """
        Cria e organiza todos os widgets da interface gráfica.

        Notas:
            - Inclui abas para oscilador, envelope, modulação/filtros e sistema.
            - Configura callbacks e atualiza referências internas.
        """
        # Crie o notebook (abas)
        notebook = ttk.Notebook(self.main_frame)
        notebook.grid(row=0, column=0, sticky="nsew")

        # Aba de Osciladores
        osc_frame = ttk.Frame(notebook)
        osc_frame.rowconfigure(0, weight=1)      
        osc_frame.columnconfigure(0, weight=1)
        osc_widgets = create_oscillator_controls(
            osc_frame,  # <-- Corrija aqui!
            self.config,
            self.on_waveform_change,
            self.on_pulse,
            self.on_ss_voices
        )
        self.osc_frame = osc_widgets["frame"]
        self.waveform_combo = osc_widgets["waveform_combo"]
        self.pulse_frame = osc_widgets["pulse_frame"]
        self.pulse_label = osc_widgets["pulse_label"]
        self.pulse_scale = osc_widgets["pulse_scale"]
        self.super_saw_frame = osc_widgets["super_saw_frame"]
        self.ss_voices_label = osc_widgets["ss_voices_label"]
        self.ss_voices = osc_widgets["ss_voices"]

        self.pulse_scale.config(command=lambda v: [update_pulse(self.config, v, self.pulse_label), self.synth.set_pulse_width(v)])
        self.ss_voices.config(command=lambda v: [
        update_ss_voices(self.config, v, self.ss_voices_label),
        self.synth.set_supersaw_voices(v),
        self.update_visuals()  
        ])

        self.osc_frame.grid(row=0, column=0, sticky="nsew")
        notebook.add(osc_frame, text="Oscilador")

        # Envelope (ADSR) em aba separada
        env_frame, env_sliders, env_labels, curve_combo = create_envelope_controls(
            notebook, self.config,
            lambda param, v, lbl: [update_adsr(self.config, param, v, lbl), self.update_adsr_param(param, v)],
            lambda e: update_adsr_curve(self.config, curve_combo)
        )
        env_frame.rowconfigure(0, weight=1)      
        env_frame.columnconfigure(0, weight=1)   
        env_frame.grid(row=0, column=0, sticky="nsew")
        notebook.add(env_frame, text="Envelope (ADSR)")
        self.env_frame = env_frame
        self.attack_slider = env_sliders["attack"]
        self.decay_slider = env_sliders["decay"]
        self.sustain_slider = env_sliders["sustain"]
        self.release_slider = env_sliders["release"]
        self.attack_label = env_labels["attack"]
        self.decay_label = env_labels["decay"]
        self.sustain_label = env_labels["sustain"]
        self.release_label = env_labels["release"]
        self.adsr_curve = curve_combo

        env_frame.grid(row=0, column=0, sticky="nsew")
        notebook.add(env_frame, text="Envelope (ADSR)")

        # Modulação e Filtros
        mod_frame = ttk.Frame(notebook)
        mod_frame.rowconfigure(0, weight=1)     
        mod_frame.columnconfigure(0, weight=1)
        mod_widgets = create_modulation_controls(
            mod_frame, self.config,
            None, None, None, None, None, None, None, None, None, None, None, None
        )

        # Salve as referências dos widgets de filtro para uso em update_filter_q_visibility
        self.filter_type = mod_widgets["filter_type"]
        self.filter_q = mod_widgets["filter_q"]
        self.filter_q_label = mod_widgets["filter_q_label"]

        mod_widgets["fm_freq"].config(command=lambda v: [update_fm_freq(self.config, v, mod_widgets["fm_freq_label"]), self.synth.set_fm_freq(v)])
        mod_widgets["fm_index"].config(command=lambda v: [update_fm_index(self.config, v, mod_widgets["fm_index_label"]), self.synth.set_fm_index(v)])
        mod_widgets["additive_scale"].config(command=lambda v: [update_additive(self.config, v, mod_widgets["additive_label"]), self.synth.set_additive(v)])
        mod_widgets["lfo_freq"].config(command=lambda v: [update_lfo_freq(self.config, v, mod_widgets["lfo_freq_label"]), self.synth.set_lfo_freq(v)])
        mod_widgets["lfo_depth"].config(command=lambda v: [update_lfo_depth(self.config, v, mod_widgets["lfo_depth_label"]), self.synth.set_lfo_depth(v)])
        mod_widgets["lfo_target"].bind('<<ComboboxSelected>>', lambda e: [update_lfo_target(self.config, mod_widgets["lfo_target"].get()), self.synth.set_lfo_target(mod_widgets["lfo_target"].get())])
        mod_widgets["hfo_freq"].config(command=lambda v: [update_hfo_freq(self.config, v, mod_widgets["hfo_freq_label"]), self.synth.set_hfo_freq(v)])
        mod_widgets["hfo_depth"].config(command=lambda v: [update_hfo_depth(self.config, v, mod_widgets["hfo_depth_label"]), self.synth.set_hfo_depth(v)])
        mod_widgets["hfo_target"].bind('<<ComboboxSelected>>', lambda e: [update_hfo_target(self.config, mod_widgets["hfo_target"].get()), self.synth.set_hfo_target(mod_widgets["hfo_target"].get())])
        mod_widgets["filter_type"].bind(
            '<<ComboboxSelected>>',
            lambda e: [
                update_filter_type(self.config, mod_widgets["filter_type"].get()),
                setattr(self.synth.config, "filter_type", mod_widgets["filter_type"].get()),
                self.update_filter_q_visibility()  # Atualiza visibilidade do Q ao trocar tipo de filtro
            ]
        )
        mod_widgets["filter_freq"].config(
            command=lambda v: [
                update_filter_freq(self.config, v, mod_widgets["filter_freq_label"]),
                setattr(self.synth.config, "filter_freq", float(v))
            ]
        )
        mod_widgets["filter_q"].config(
            command=lambda v: [
                update_filter_q(self.config, v, mod_widgets["filter_q_label"]),
                setattr(self.synth.config, "filter_q", float(v))
            ]
        )

        mod_frame.grid(row=0, column=0, sticky="nsew")
        notebook.add(mod_frame, text="Modulação/Filtros")

        # Aba de Sistema/Configurações
        sys_frame = ttk.Frame(notebook)
        sys_frame.rowconfigure(0, weight=1)      
        sys_frame.columnconfigure(0, weight=1)
        sys_widgets = create_system_controls(
            sys_frame,
            self.config,
            self.update_sample_rate,
            self.update_buffer_size,
            self.on_polyphony,
            self.save_config_dialog,
            self.load_config_dialog,
            self.load_wavetable
        )
        self.sample_rate = sys_widgets["sample_rate"]
        self.buffer_size = sys_widgets["buffer_size"]
        self.polyphony = sys_widgets["polyphony"]
        self.polyphony_label = sys_widgets["polyphony_label"]
        sys_frame.grid(row=0, column=0, sticky="nsew")
        notebook.add(sys_frame, text="Sistema")

        # Atualize visibilidade dos controles condicionais
        self.update_waveform_visibility()
        self.update_filter_q_visibility()  # Garante visibilidade correta do Q ao iniciar

    def setup_bindings(self):
        """
        Configura os bindings de eventos para a interface gráfica.

        Notas:
            - Inclui bindings para seleção de forma de onda, atalhos de teclado e fechamento da janela.
        """
        self.waveform_combo.bind('<<ComboboxSelected>>', self.on_waveform_change)
        self.adsr_curve.bind('<<ComboboxSelected>>', lambda e: update_adsr(self.config, self.adsr_curve))
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        # Binding global para bloquear entrada de teclado em Combobox
        self.master.bind_all("<Key>", self.block_keyboard_input)
        self.master.bind("<Control-s>", lambda e: self.save_config())
        self.master.bind("<Control-o>", lambda e: self.load_config())
    def block_keyboard_input(self, event):
        """
        Bloqueia a entrada de teclado em widgets interativos.

        Parâmetros:
            event: Evento de teclado.
        """
        print(f"Tecla pressionada: {event.keysym}")  # Debug
        focused_widget = self.master.focus_get()
        if isinstance(focused_widget, ttk.Combobox):
            # Permite navegação dentro do Combobox (setas, Enter, etc.)
            if event.keysym in ["Up", "Down", "Return", "Tab"]:
                return
            # Bloqueia outros eventos de teclado
            return "break"

    def update_waveform_visibility(self):
        """
        Atualiza a visibilidade dos controles de forma de onda com base na seleção atual.

        Notas:
            - Exibe ou oculta controles específicos conforme o tipo de onda.
        """
        wave = WaveType(self.waveform_combo.get())
        visibility = {
            WaveType.PULSE: [self.pulse_frame],
            WaveType.SUPER_SAW: [self.super_saw_frame],
        }
        
        # Esconde todos os frames específicos primeiro
        for frame in [self.pulse_frame, self.super_saw_frame]:
            frame.grid_remove()

        # Mostra apenas o frame relevante para a forma de onda selecionada
        if wave == WaveType.PULSE:
            self.pulse_frame.grid()
        elif wave == WaveType.SUPER_SAW:
            self.super_saw_frame.grid()

    def update_filter_q_visibility(self):
        """
        Atualiza a visibilidade do controle Q do filtro com base no tipo de filtro selecionado.

        Notas:
            - Exibe Q apenas para filtros do tipo bandpass.
        """
        filter_type = self.filter_type.get() if hasattr(self, "filter_type") else None
        if filter_type == "bandpass":
            self.filter_q.grid()
            self.filter_q_label.grid()
        else:
            self.filter_q.grid_remove()
            self.filter_q_label.grid_remove()

    def on_waveform_change(self, event):
        """
        Processa mudanças na forma de onda selecionada.

        Parâmetros:
            event: Evento de seleção do Combobox.
        """
        new_wave = WaveType(self.waveform_combo.get())
        self.config.default_waveform = new_wave
        self.synth.set_waveform(new_wave)
        self.update_waveform_visibility()

    def load_wavetable(self):
        """
        Carrega uma tabela de ondas a partir de um arquivo WAV.

        Notas:
            - Atualiza a configuração e o sintetizador com a wavetable carregada.
        """
        file_path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if file_path:
            try:
                data, _ = sf.read(file_path)
                if data is None or len(data) == 0:
                    raise ValueError("⚠️ Arquivo WAV inválido ou vazio.")
                self.config.wavetable = data
                self.synth.config.wavetable = data

            except Exception as e:
                print(f"Error loading wavetable: {e}")
    def update_sample_rate(self, event):
        """
        Atualiza a taxa de amostragem do sintetizador.

        Parâmetros:
            event: Evento de seleção do Combobox.
        """
        try:
            new_rate = int(self.sample_rate.get())
            self.config.sample_rate = new_rate
            self.config.bandlimited_tables = generate_bandlimited_tables(new_rate)
            self.restart_audio_stream()
        except Exception as e:
            print(f"Erro ao atualizar sample rate: {e}")

    def update_buffer_size(self, event):
        """
        Atualiza o tamanho do buffer do sintetizador.

        Parâmetros:
            event: Evento de seleção do Combobox.
        """
        try:
            new_size = int(self.buffer_size.get())
            self.config.buffer_size = new_size
            self.restart_audio_stream()
        except Exception as e:
            print(f"Erro ao atualizar buffer size: {e}")

    def update_adsr_param(self, param, value):
        """
        Atualiza o parâmetro ADSR no sintetizador em tempo real.

        Parâmetros:
            param (str): Nome do parâmetro ('attack', 'decay', 'sustain', 'release').
            value (float): Novo valor do parâmetro.
        """
        if param in ["attack", "decay", "release"]:
            setattr(self.synth.config, f"{param}_time", float(value))
        elif param == "sustain":
            setattr(self.synth.config, "sustain_level", float(value))

    def restart_audio_stream(self):
        """
        Reinicia o stream de áudio com as novas configurações.

        Notas:
            - Cria uma nova instância do sintetizador e atualiza o teclado MIDI.
        """
        try:
            print("Reiniciando stream de áudio com nova configuração...")
            
            # Parar o stream atual
            if self.synth:
                self.synth.stop()
            
            # Criar uma nova instância do sintetizador com as configurações atualizadas
            self.synth = MidiSynth(self.config)
            self.synth.start()

            # Atualizar a referência do teclado MIDI para o novo sintetizador
            self.keyboard_midi.synth = self.synth

            print("Stream de áudio reiniciado com sucesso.")
        except Exception as e:
            print(f"Erro ao reiniciar stream de áudio: {e}")

    def setup_visuals(self):
            self.fig, self.ax = plt.subplots(figsize=(8, 2), facecolor='#0A0A0A')
            self.ax.set_facecolor('#0A0A0A')
            
            # Pinta a borda de baixo de amarelo, e esconde as outras
            self.ax.spines['bottom'].set_color('#F5C800')
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            self.ax.spines['left'].set_visible(False)
                    
            # Remove os números dos eixos e esconde os ticks
            self.ax.set_xticks([])
            self.ax.set_yticks([])

            self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
            self.canvas.get_tk_widget().grid(row=1, column=0, sticky="ew", padx=10, pady=10)

            # Resto do seu código original (botão de pause, etc...)
            self.visual_paused = False
            self.pause_button = ttk.Button(self.master, text="⏸ Pausar Visualização", command=self.toggle_visual)
            self.pause_button.grid(row=3, column=0, pady=5, padx=10, sticky="ew")

            self.start_visual_updates()

    def update_visuals(self):
        """
        Atualiza a visualização da onda com custo de CPU ultrabaixo, 
        incluindo efeito de preenchimento (fill) abaixo da linha.
        """
        if getattr(self, 'visual_paused', False):
            self.visual_update_id = self.master.after(50, self.update_visuals)
            return

        try:
            from synth.audio import visual_queue
            
            # Pega o buffer mais recente e descarta os antigos
            buffer = None
            while not visual_queue.empty():
                buffer = visual_queue.get_nowait()
            
            if buffer is not None:
                # 1. DOWNSAMPLING: Pega apenas 1 a cada 4 frames
                mix = buffer[::4, 0] 
                mix = np.clip(mix, -1.0, 1.0)

                # 2. RENDERIZAÇÃO DE ALTA PERFORMANCE
                if not hasattr(self, 'wave_line') or self.wave_line is None:
                    self.ax.clear()
                    
                    # Calcula o eixo de tempo e guarda na classe para reutilizar (micro-otimização)
                    duration = len(mix) / (self.config.sample_rate / 4)
                    self.t_axis = np.linspace(0, duration, len(mix))
                    
                    self.wave_line, = self.ax.plot(self.t_axis, mix, color='#1A7A2E', linewidth=2.0)
                    self.wave_fill = self.ax.fill_between(self.t_axis, mix, 0, color='#1A7A2E', alpha=0.3)
                    
                    self.ax.set_ylim(-1.1, 1.1)
                    self.ax.set_title("▶ Waveform Preview (Ao Vivo)", color='#1A7A2E', fontweight='bold', loc='left')
                    self.canvas.draw()
                else:
                    # Atualiza a posição Y da linha instantaneamente
                    self.wave_line.set_ydata(mix)
                    
                    # Para o preenchimento, o Matplotlib não tem set_ydata. 
                    # Truque: Removemos apenas a sombra antiga da memória e criamos uma nova.
                    if hasattr(self, 'wave_fill') and self.wave_fill in self.ax.collections:
                        self.wave_fill.remove()
                    
                    self.wave_fill = self.ax.fill_between(self.t_axis, mix, 0, color='cyan', alpha=0.3)
                    
                    # Pede para a placa de vídeo redesenhar quando tiver tempo livre
                    self.canvas.draw_idle()

        except Exception as e:
            pass # Ignora erros visuais para não derrubar o motor de áudio

        # Reagenda para 50ms (~20 FPS)
        self.visual_update_id = self.master.after(50, self.update_visuals)

    def start_visual_updates(self):
        """
        Inicia o loop de atualização visual com gerenciamento adequado de callbacks.

        Notas:
            - Atualiza a visualização a cada 100ms.
        """
        if self.visual_update_id:
            self.master.after_cancel(self.visual_update_id)
            
        def update():
            if not self.master.winfo_exists():
                return
            try:
                if not self.visual_paused:
                    self.update_visuals() 
                    pass
                
            except Exception as e:
                print(f"Erro na atualização visual: {e}")
            finally:
                self.visual_update_id = self.master.after(100, update)
                
        self.visual_update_id = self.master.after(100, update)

    

    def toggle_visual(self):
        """
        Alterna entre pausar e retomar a animação de rastreamento do gráfico visual.

        Modifica o estado booleano interno (`self.visual_paused`) e altera dinamicamente 
        o rótulo de texto do botão de controle na interface. Quando o estado muda para pausado, 
        força o desenho instantâneo de uma forma de onda estática padrão para indicar a interrupção.
        """
        self.visual_paused = not getattr(self, 'visual_paused', False)
        new_text = "▶ Retomar Visualização" if self.visual_paused else "⏸ Pausar Visualização"
        self.pause_button.config(text=new_text)

        # Se acabou de pausar, limpa a tela substituindo por uma onda estática estável
        if self.visual_paused:
            t = np.linspace(0, 0.03, 500)
            phase = 2 * np.pi * 440 * t
            wave = generate_static_wave(phase, self.config)
            update_waveform_plot(self.ax, t, wave, title="Waveform Preview (Pausado)")
            self.canvas.draw()

        
        if not self.synth.voice_manager.get_voices():
            # Gerar preview estático
            phase = 2 * np.pi * 440 * t
            wave = generate_static_wave(phase, self.config)
            update_waveform_plot(self.ax, t, wave, title="Waveform Preview (Modo Estático)")
            self.canvas.draw()
            return
        
        if len(t) > 500:  # Limita o número de pontos
             t = t[::len(t)//500]    
                                                                                                                                                                                                                                      
        try:
            t = np.linspace(0, 0.03, 1000)  # tempo de 30ms
            mix = np.zeros_like(t)

            with self.synth.voice_manager.get_lock():
                for voice in self.synth.config.last_audio_buffer:
                    wave = generate_wave(voice, t, self.synth.config)
                    adsr = calculate_adsr(voice, self.synth.config)
                    mix += wave * adsr * voice.velocity

            # Normalize (evita clipping no gráfico)
            mix = np.clip(mix, -1.0, 1.0)

            update_waveform_plot(self.ax, t, mix, title="Waveform Preview (ao vivo)")
            self.canvas.draw()

        except Exception as e:
            print(f"Erro na visualização: {e}")

        self.master.after(100, self.update_visuals)

    def on_close(self):
        """
        Fecha a janela e libera todos os recursos do sintetizador.

        Notas:
            - Cancela atualizações visuais, para o sintetizador e fecha a janela principal.
        """
        # Cancela atualizações visuais agendadas
        if self.visual_update_id:
            self.master.after_cancel(self.visual_update_id)
            self.visual_update_id = None

        # Para o sintetizador e libera recursos MIDI/áudio
        if hasattr(self, "synth") and self.synth:
            self.synth.stop()
            if hasattr(self.synth, "on_close"):
                self.synth.on_close()

        # Para o teclado MIDI virtual, se existir
        if hasattr(self, "keyboard_midi") and self.keyboard_midi:
            if hasattr(self.keyboard_midi, "stop"):
                self.keyboard_midi.stop()

        # Fecha a janela principal
        self.master.destroy()