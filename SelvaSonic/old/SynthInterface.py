import tkinter as tk
from tkinter import ttk, filedialog
import sounddevice as sd
import mido
import numpy as np
from AudioSynth import MidiSynth, SynthConfig, WaveType, ADSRCurve, VoiceState
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import soundfile as sf
from pynput import keyboard  
from scipy.signal import butter, lfilter
import json

class KeyboardMIDI:
    """
    Classe para gerenciar a entrada de teclado MIDI virtual.

    Atributos:
    - synth: Instância do sintetizador para processar eventos MIDI.
    - octave_offset: Offset da oitava para ajustar as notas tocadas.
    - master: Referência ao master para atualizações de UI.
    - key_to_note: Mapeamento de teclas do teclado para notas MIDI.
    """
    def __init__(self, synth, master):
        self.synth = synth
        self.octave_offset = 0  # 0 = oitava central
        self.master = master  # Referência ao master para atualizações de UI
        self.key_to_note = {
    # Primeira Oitava (C3-B3)
    'z': 48, 'x': 50, 'c': 52, 'v': 53, 'b': 55, 'n': 57, 'm': 59,
    's': 49,  # C#3
    'd': 51, 'g': 54, 'h': 56, 'j': 58,
    # Segunda Oitava (C4-B4)
    'a': 60, 'q': 61, 'w': 62, 'e': 63, 'r': 65, 't': 66, 'y': 67, 'u': 68,
    # Terceira Oitava (C5-B5)
    '1': 72, '2': 73, '3': 74, '4': 75, '5': 76, '6': 77, '7': 78
}
        self.listener = None

    def start(self):
        """
        Inicia o listener para capturar eventos de teclado.
        """
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()


    def on_press(self, key):
        """
        Processa eventos de pressionamento de teclas.

        Args:
        - key: Tecla pressionada.
        """
        try:
            if key.char == '1':
                self.octave_offset = max(-48, self.octave_offset - 12)
                return  # Impede processamento adicional
            elif key.char == '4':
                self.octave_offset = min(48, self.octave_offset + 12)
                return  # Impede processamento adicional
            
            note_info = self.key_to_note.get(key.char)
            if isinstance(note_info, int):
                note = note_info + self.octave_offset
                if 0 <= note <= 127:
                    def safe_note_on(n):
                        try:
                            self.synth._note_on(n, 0.7)
                        except Exception as e:
                            print(f"Erro ao tocar nota {n}: {e}")
                    self.master.after(0, lambda n=note: safe_note_on(n))    
                       
        except AttributeError:
            pass
        
    def on_release(self, key):
        """
        Processa eventos de liberação de teclas.

        Args:
        - key: Tecla liberada.
        """
        try:
            if hasattr(key, 'char') and key.char in self.key_to_note:
                note_info = self.key_to_note[key.char]
                if isinstance(note_info, int):
                    note = note_info + self.octave_offset
                    if 0 <= note <= 127:  # Verifica limites MIDI
                        self.synth._note_off(note)
        except AttributeError:
            pass


class FullSynthInterface:
    """
    Interface gráfica para controle do sintetizador.

    Atributos:
    - master: Janela principal do Tkinter.
    - config: Configuração do sintetizador.
    - synth: Instância do sintetizador MIDI.
    - keyboard_midi: Instância do teclado MIDI virtual.
    """
    def __init__(self, master):
        """
        Inicializa a interface gráfica e os componentes do sintetizador.

        Args:
        - master: Janela principal do Tkinter.
        """
        self.master = master
        self.master.title("Advanced Synth Controller")
        self.master.geometry("1000x800")
        
        self.config = SynthConfig()
        self.synth = MidiSynth(self.config)
        self.keyboard_midi = KeyboardMIDI(self.synth, self.master)  
        
        self.create_widgets()
        self.setup_bindings()
        self.current_waveform = self.config.default_waveform
        self.setup_visuals()
        self.synth.start()
        
        
        self.create_keyboard_help()
        self.keyboard_midi.start()  # Inicia o teclado MIDI
    
    def save_config(self):
        """
        Salva as configurações do sintetizador em um arquivo JSON.
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.config.__dict__, f, indent=4)
                print(f"Configuração salva em {file_path}")
            except Exception as e:
                print(f"Erro ao salvar configuração: {e}")

    def load_config(self):
        """
        Carrega as configurações do sintetizador de um arquivo JSON.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        setattr(self.config, key, value)
                         # Adiciona validação das configurações carregadas
                self.config.validate()
                self.restart_audio_stream()  # Reinicia o stream com as novas configurações
                print(f"Configuração carregada de {file_path}")
            except Exception as e:
                print(f"Erro ao carregar configuração: {e}")

    def create_keyboard_help(self):
        """
        Cria uma seção de ajuda para o teclado MIDI virtual.
        """
        help_frame = ttk.LabelFrame(self.master, text="Teclado MIDI")
        help_frame.pack(padx=10, pady=10)
        
        keys = [
            "A-K: Notas naturais",
            "W,E,T,Y,U: Sustenidos",
            "Pressione as teclas para tocar"
        ]
        
        for text in keys:
            ttk.Label(help_frame, text=text).pack(anchor='w')

    def create_widgets(self):
        # Crie o notebook
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill="both", expand=True)

        # Crie frames para cada aba
        self.osc_tab = ttk.Frame(self.notebook)
        self.env_tab = ttk.Frame(self.notebook)
        self.mod_tab = ttk.Frame(self.notebook)
        self.sys_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.osc_tab, text="Oscillator")
        self.notebook.add(self.env_tab, text="Envelope")
        self.notebook.add(self.mod_tab, text="Modulation")
        self.notebook.add(self.sys_tab, text="System")

        # OSCILLATOR TAB
        osc_widgets = create_oscillator_controls(
            self.osc_tab, self.config,
            self.on_waveform_change,
            self.on_pulse,
            self.on_ss_voices,
            self.on_noise_type_change
        )
        # Salve os frames específicos como atributos para update_waveform_visibility
        self.pulse_frame = osc_widgets["pulse_frame"]
        self.super_saw_frame = osc_widgets["super_saw_frame"]
        self.noise_frame = osc_widgets["noise_frame"]
        self.waveform_combo = osc_widgets["waveform_combo"]
        self.noise_type = osc_widgets["noise_type"]

        # ENVELOPE TAB
        env_widgets = create_envelope_controls(
            self.env_tab, self.config,
            self.on_adsr_change,
            self.on_curve_change
        )
        # Se precisar acessar widgets específicos do envelope, salve-os aqui

        # MODULATION TAB
        mod_widgets = create_modulation_controls(
            self.mod_tab, self.config,
            self.on_fm_freq,
            self.on_fm_index,
            self.on_additive,
            self.on_lfo_freq,
            self.on_lfo_depth,
            self.on_lfo_target,
            self.on_hfo_freq,
            self.on_hfo_depth,
            self.on_hfo_target
        )
        # Se precisar acessar widgets específicos da modulação, salve-os aqui

        # SYSTEM TAB
        sys_widgets = create_system_controls(
            self.sys_tab, self.config,
            self.on_sample_rate,
            self.on_buffer_size,
            self.on_polyphony,
            self.save_config,
            self.load_config,
            self.load_wavetable
        )
        # Se precisar acessar widgets específicos do sistema, salve-os aqui

        # Chame update_waveform_visibility para garantir que só o frame correto aparece
        self.update_waveform_visibility()

    def create_modulation_controls(self, parent):
        """
        Cria os controles de modulação.

        Args:
        - parent: Widget pai para os controles.
        """
        # FM Frequency
        ttk.Label(parent, text="FM Frequency:").grid(row=0, column=0)
        
        # Cria o label primeiro
        self.fm_freq_label = ttk.Label(parent, text=f"{self.config.fm_mod_freq:.1f}")
        self.fm_freq_label.grid(row=0, column=2)
        
        # Configura a escala após o label
        self.fm_freq = ttk.Scale(parent, from_=0.1, to=5000)
        self.fm_freq.grid(row=0, column=1)
        self.fm_freq.config(command=self.update_fm_freq)  # Comando após label existir
        self.fm_freq.set(self.config.fm_mod_freq)

        # FM Index
        ttk.Label(parent, text="FM Index:").grid(row=1, column=0)
        
        # Cria o label primeiro
        self.fm_index_label = ttk.Label(parent, text=f"{self.config.fm_mod_index:.2f}")
        self.fm_index_label.grid(row=1, column=2)
        
        # Configura a escala após o label
        self.fm_index = ttk.Scale(parent, from_=0, to=10)
        self.fm_index.grid(row=1, column=1)
        self.fm_index.config(command=self.update_fm_index)  # Comando após label existir
        self.fm_index.set(self.config.fm_mod_index)

        ttk.Label(parent, text="Additive Harmonics:").grid(row=2, column=0)
    
        self.additive_label = ttk.Label(parent, text=str(self.config.additive_harmonics))
        self.additive_label.grid(row=2, column=2)
        
        self.additive_scale = ttk.Scale(parent, from_=1, to=16)
        self.additive_scale.grid(row=2, column=1)
        self.additive_scale.config(command=self.update_additive)
        self.additive_scale.set(self.config.additive_harmonics)

        # === LFO ===========================================================================================================================
        ttk.Label(parent, text="LFO Freq:").grid(row=3, column=0)
        self.lfo_freq_label = ttk.Label(parent, text=f"{self.config.lfo_freq:.2f} Hz")
        self.lfo_freq_label.grid(row=3, column=2)

        self.lfo_freq = ttk.Scale(parent, from_=0.1, to=20.0, command=self.update_lfo_freq)
        self.lfo_freq.set(self.config.lfo_freq)
        self.lfo_freq.grid(row=3, column=1)

        ttk.Label(parent, text="LFO Depth:").grid(row=4, column=0)
        self.lfo_depth_label = ttk.Label(parent, text=f"{self.config.lfo_depth:.2f}")
        self.lfo_depth_label.grid(row=4, column=2)

        self.lfo_depth = ttk.Scale(parent, from_=0.0, to=1.0, command=self.update_lfo_depth)
        self.lfo_depth.set(self.config.lfo_depth)
        self.lfo_depth.grid(row=4, column=1)

        ttk.Label(parent, text="LFO Target:").grid(row=5, column=0)
        self.lfo_target = ttk.Combobox(parent, values=["pitch", "pulse"])
        self.lfo_target.set(self.config.lfo_target)
        self.lfo_target.grid(row=5, column=1)
        self.lfo_target.bind('<<ComboboxSelected>>', self.update_lfo_target)

        # === HFO ==================================================================================================================
        ttk.Label(parent, text="HFO Freq:").grid(row=6, column=0)
        self.hfo_freq_label = ttk.Label(parent, text=f"{self.config.hfo_freq:.1f} Hz")
        self.hfo_freq_label.grid(row=6, column=2)

        self.hfo_freq = ttk.Scale(parent, from_=20, to=8000, command=self.update_hfo_freq)
        self.hfo_freq.set(self.config.hfo_freq)
        self.hfo_freq.grid(row=6, column=1)

        ttk.Label(parent, text="HFO Depth:").grid(row=7, column=0)
        self.hfo_depth_label = ttk.Label(parent, text=f"{self.config.hfo_depth:.2f}")
        self.hfo_depth_label.grid(row=7, column=2)

        self.hfo_depth = ttk.Scale(parent, from_=0.0, to=1.0, command=self.update_hfo_depth)
        self.hfo_depth.set(self.config.hfo_depth)
        self.hfo_depth.grid(row=7, column=1)

        ttk.Label(parent, text="HFO Target:").grid(row=8, column=0)
        self.hfo_target = ttk.Combobox(parent, values=["pitch"])
        self.hfo_target.set(self.config.hfo_target)
        self.hfo_target.grid(row=8, column=1)
        self.hfo_target.bind('<<ComboboxSelected>>', self.update_hfo_target)

        # === FILTER ============================================================================================================
        filter_frame = ttk.LabelFrame(parent, text="Filter")
        filter_frame.grid(row=9, column=0, columnspan=3, pady=10, sticky='ew')

        ttk.Label(filter_frame, text="Type:").grid(row=0, column=0)
        self.filter_type = ttk.Combobox(filter_frame, values=["lowpass", "highpass", "bandpass"])
        self.filter_type.set(self.config.filter_type)
        self.filter_type.grid(row=0, column=1)
        self.filter_type.bind("<<ComboboxSelected>>", self.update_filter_type)

        ttk.Label(filter_frame, text="Cutoff (Hz):").grid(row=1, column=0)
        self.filter_freq_label = ttk.Label(filter_frame, text=f"{self.config.filter_freq:.0f}")
        self.filter_freq_label.grid(row=1, column=2)

        self.filter_freq = ttk.Scale(filter_frame, from_=20, to=20000, command=self.update_filter_freq)
        self.filter_freq.set(self.config.filter_freq)
        self.filter_freq.grid(row=1, column=1)

        ttk.Label(filter_frame, text="Q:").grid(row=2, column=0)
        self.filter_q_label = ttk.Label(filter_frame, text=f"{self.config.filter_q:.2f}")
        self.filter_q_label.grid(row=2, column=2)

        self.filter_q = ttk.Scale(filter_frame, from_=0.1, to=10.0, command=self.update_filter_q)
        self.filter_q.set(self.config.filter_q)
        self.filter_q.grid(row=2, column=1)

    def create_envelope_controls(self, parent):
        """
        Cria os controles de envelope ADSR.

        Args:
        - parent: Widget pai para os controles.
        """
        # ADSR Controls
        adsr_params = [
            ('Attack', 0.0, 2.0, self.config.attack_time),
            ('Decay', 0.0, 2.0, self.config.decay_time),
            ('Sustain', 0.0, 1.0, self.config.sustain_level),
            ('Release', 0.0, 2.0, self.config.release_time)
        ]
        
        for i, (name, min_val, max_val, init_val) in enumerate(adsr_params):
            ttk.Label(parent, text=f"{name}:").grid(row=i, column=0)
            
            # Cria o label primeiro
            label = ttk.Label(parent, text=f"{init_val:.2f}")
            label.grid(row=i, column=2)
            setattr(self, f"{name.lower()}_label", label)  # Garanta que o nome está correto
            
            # Configura a escala após o label
            scale = ttk.Scale(parent, from_=min_val, to=max_val)
            scale.grid(row=i, column=1)
            scale.config(command=lambda v, n=name: self.update_adsr(n, v))
            scale.set(init_val)  # Valor inicial após configuração

        # ADSR Curve Type
        ttk.Label(parent, text="Curve Type:").grid(row=4, column=0)
        self.adsr_curve = ttk.Combobox(parent, values=['Linear', 'Exponential'])
        self.adsr_curve.set(self.config.adsr_curve.value.capitalize())
        self.adsr_curve.grid(row=4, column=1)

    def create_system_controls(self, parent):
        """
        Cria os controles do sistema, como taxa de amostragem e polifonia.

        Args:
        - parent: Widget pai para os controles.
        """
        # MIDI Devices ============================================================================================================
        ttk.Label(parent, text="MIDI Input:").grid(row=0, column=0)
        self.midi_devices = ttk.Combobox(parent, values=mido.get_input_names())
        self.midi_devices.grid(row=0, column=1)

        # Polyphony ============================================================================================================
        ttk.Label(parent, text="Max Polyphony:").grid(row=1, column=0)
        self.max_polyphony = ttk.Scale(parent, from_=1, to=64)
        self.max_polyphony.grid(row=1, column=1)
        self.max_polyphony.set(self.config.max_polyphony)

        # Qualidade de Áudio ============================================================================================================
        ttk.Label(parent, text="Sample Rate (Hz):").grid(row=3, column=0)
        self.sample_rate = ttk.Combobox(parent, values=[22050, 32000, 44100, 48000, 96000])
        self.sample_rate.set(self.config.sample_rate)
        self.sample_rate.grid(row=3, column=1)
        self.sample_rate.bind('<<ComboboxSelected>>', self.update_sample_rate)

        ttk.Label(parent, text="Buffer Size:").grid(row=4, column=0)
        self.buffer_size = ttk.Combobox(parent, values=[32, 64, 128, 256, 512])
        self.buffer_size.set(self.config.buffer_size)
        self.buffer_size.grid(row=4, column=1)
        self.buffer_size.bind('<<ComboboxSelected>>', self.update_buffer_size)

        # Botões de configuração =========================================================================================================
        ttk.Button(parent, text="Salvar Configuração", command=self.save_config).grid(row=5, column=0, pady=10)
        ttk.Button(parent, text="Carregar Configuração", command=self.load_config).grid(row=5, column=1, pady=10)


        # Cria o label primeiro ============================================================================================================
        self.polyphony_label = ttk.Label(parent, text=str(self.config.max_polyphony))
        self.polyphony_label.grid(row=1, column=2)

        # Configura a escala após o label ======================================================================================================
        self.polyphony = ttk.Scale(parent, from_=1, to=64)
        self.polyphony.grid(row=1, column=1)
        self.polyphony.config(command=self.update_polyphony)  # Configure o comando depois
        self.polyphony.set(self.config.max_polyphony)
                
        # Wavetable Loader =====================================================================================================================
        ttk.Button(parent, text="Load Wavetable", command=self.load_wavetable).grid(row=2, column=0)

    def setup_bindings(self):
        """
        Configura os bindings de eventos para a interface gráfica.
        """
        self.waveform.bind('<<ComboboxSelected>>', self.on_waveform_change)
        self.adsr_curve.bind('<<ComboboxSelected>>', self.update_adsr_curve)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        # Binding global para bloquear entrada de teclado em Combobox
        self.master.bind_all("<Key>", self.block_keyboard_input)
        self.master.bind("<Control-s>", lambda e: self.save_config())
        self.master.bind("<Control-o>", lambda e: self.load_config())
    
    def block_keyboard_input(self, event):
        """
        Bloqueia a entrada de teclado em widgets interativos.

        Args:
        - event: Evento de teclado.
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
        Atualiza a visibilidade dos controles de forma de onda.
        """
        wave = WaveType(self.waveform.get())
        visibility = {
            WaveType.PULSE: [self.pulse_frame],
            WaveType.SUPER_SAW: [self.super_saw_frame],
            WaveType.NOISE: [self.noise_frame],
            WaveType.PINK_NOISE: [self.noise_frame],
            WaveType.BROWN_NOISE: [self.noise_frame]
        }
        
        # Hide all first
        for f in [self.pulse_frame, self.super_saw_frame, self.noise_frame]:
            f.grid_remove()
        
        # Show relevant frames
        for wt in visibility.get(wave, []):
            wt.grid()

    def on_waveform_change(self, event):
        """
        Processa mudanças na forma de onda selecionada.

        Args:
        - event: Evento de seleção.
        """
        new_wave = WaveType(self.waveform.get())
        self.config.default_waveform = new_wave
        
        if new_wave in [WaveType.NOISE, WaveType.PINK_NOISE, WaveType.BROWN_NOISE]:
            selected_noise = self.noise_type.get()
            try:
                self.config.default_waveform = WaveType(selected_noise)
            except ValueError:
                self.config.default_waveform = WaveType.NOISE
        
        self.update_waveform_visibility()

    def update_pulse(self, value):
        """
        Atualiza o valor da largura de pulso.

        Args:
        - value: Novo valor da largura de pulso.
        """
        self.config.pulse_width = float(value)
        self.pulse_label.config(text=f"{float(value):.2f}")

    def update_ss_voices(self, value):
        """
        Atualiza o número de vozes para o oscilador Super Saw.

        Args:
        - value: Novo número de vozes.
        """
        self.config.super_saw_voices = int(float(value))
        self.ss_voices_label.config(text=str(int(float(value))))

    def update_additive(self, value):
        """
        Atualiza o número de harmônicos para síntese aditiva.

        Args:
        - value: Novo número de harmônicos.
        """
        self.config.additive_harmonics = int(float(value))
        self.additive_label.config(text=str(int(float(value))))

    def update_fm_freq(self, value):
        """
        Atualiza a frequência de modulação em frequência (FM).

        Args:
        - value: Nova frequência de modulação.
        """
        self.config.fm_mod_freq = float(value)
        self.fm_freq_label.config(text=f"{float(value):.1f}")

    def update_fm_index(self, value):
        """
        Atualiza o índice de modulação em frequência (FM).

        Args:
        - value: Novo índice de modulação.
        """
        self.config.fm_mod_index = float(value)
        self.fm_index_label.config(text=f"{float(value):.2f}")

    def update_adsr(self, param, value):
        """
        Atualiza os parâmetros do envelope ADSR.

        Args:
        - param: Nome do parâmetro a ser atualizado (Attack, Decay, Sustain, Release).
        - value: Novo valor para o parâmetro.
        """
        value = float(value)
        getattr(self, f"{param.lower()}_label").config(text=f"{value:.2f}")
        
        if param == 'Sustain':
            self.config.sustain_level = value
        else:
            setattr(self.config, f"{param.lower()}_time", value)

    def update_adsr_curve(self, event):
        """
        Atualiza a curva do envelope ADSR.

        Args:
        - event: Evento de seleção.
        """
        curve = self.adsr_curve.get().lower()
        self.config.adsr_curve = ADSRCurve(curve)

    def update_polyphony(self, value):
        """
        Atualiza o número máximo de vozes simultâneas.

        Args:
        - value: Novo número máximo de vozes.
        """
        self.config.max_polyphony = int(float(value))
        self.polyphony_label.config(text=str(self.config.max_polyphony))
    
    def update_lfo_freq(self, value):
        """
        Atualiza a frequência do LFO.

        Args:
        - value: Nova frequência do LFO.
        """
        val = float(value)
        self.config.lfo_freq = val
        self.lfo_freq_label.config(text=f"{val:.2f} Hz")

    def update_lfo_depth(self, value):
        """
        Atualiza a profundidade do LFO.

        Args:
        - value: Nova profundidade do LFO.
        """
        val = float(value)
        self.config.lfo_depth = val
        self.lfo_depth_label.config(text=f"{val:.2f}")

    def update_lfo_target(self, event):
        """
        Atualiza o alvo do LFO.

        Args:
        - event: Evento de seleção.
        """
        self.config.lfo_target = self.lfo_target.get()

    def update_hfo_freq(self, value):
        """
        Atualiza a frequência do HFO.

        Args:
        - value: Nova frequência do HFO.
        """
        val = float(value)
        self.config.hfo_freq = val
        self.hfo_freq_label.config(text=f"{val:.1f} Hz")

    def update_hfo_depth(self, value):
        """
        Atualiza a profundidade do HFO.

        Args:
        - value: Nova profundidade do HFO.
        """
        val = float(value)
        self.config.hfo_depth = val
        self.hfo_depth_label.config(text=f"{val:.2f}")

    def update_hfo_target(self, event):
        """
        Atualiza o alvo do HFO.

        Args:
        - event: Evento de seleção.
        """
        self.config.hfo_target = self.hfo_target.get()

    def update_filter_type(self, event):
        """
        Atualiza o tipo de filtro.
        """
        self.config.filter_type = self.filter_type.get()

    def update_filter_freq(self, value):
        """
        Atualiza a frequência do filtro.

        Args:
        - value: Nova frequência do filtro.
        """
        val = float(value)
        self.config.filter_freq = val
        self.filter_freq_label.config(text=f"{val:.0f}")

    def update_filter_q(self, value):
        """
        Atualiza o fator de qualidade (Q) do filtro.

        Args:
        - value: Novo fator de qualidade (Q) do filtro.
        """
        val = float(value)
        self.config.filter_q = val
        self.filter_q_label.config(text=f"{val:.2f}")

    def load_wavetable(self):
        """
        Carrega uma tabela de ondas a partir de um arquivo WAV.
        """
        file_path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if file_path:
            try:
                data, _ = sf.read(file_path)
                if data is None or len(data) == 0:
                    raise ValueError("⚠️ Arquivo WAV inválido ou vazio.")
                self.config.wavetable = data

            except Exception as e:
                print(f"Error loading wavetable: {e}")
    def update_sample_rate(self, event):
        """
        Atualiza a taxa de amostragem do sintetizador.
        """
        try:
            new_rate = int(self.sample_rate.get())
            self.config.sample_rate = new_rate
            self.restart_audio_stream()
        except Exception as e:
            print(f"Erro ao atualizar sample rate: {e}")

    def update_buffer_size(self, event):
        """
        Atualiza o tamanho do buffer do sintetizador.
        """
        try:
            new_size = int(self.buffer_size.get())
            self.config.buffer_size = new_size
            self.restart_audio_stream()
        except Exception as e:
            print(f"Erro ao atualizar buffer size: {e}")

    def restart_audio_stream(self):
        """
        Reinicia o stream de áudio com as novas configurações.
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
        """
        Configura a visualização da forma de onda.
        """
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Botão para pausar/retomar visualização
        self.visual_paused = False
        self.pause_button = ttk.Button(self.master, text="⏸ Pausar Visualização", command=self.toggle_visual)
        self.pause_button.pack()

        self.update_visuals()
    
    def toggle_visual(self):
        """
        Alterna entre pausar e retomar a visualização da forma de onda.
        """
        self.visual_paused = not self.visual_paused
        new_text = "▶ Retomar Visualização" if self.visual_paused else "⏸ Pausar Visualização"
        self.pause_button.config(text=new_text)


    def update_visuals(self, force=False):
        """
        Atualiza a visualização da forma de onda.
        """
        if self.visual_paused:
            self.master.after(200, self.update_visuals)
            return

        t = np.linspace(0, 0.03, 1000)
        
        if not self.synth.voices:
            # Gerar preview estático
            phase = 2 * np.pi * 440 * t
            wave = self._generate_static_wave(phase)
            self.ax.clear()
            self.ax.plot(t, wave)
            self.ax.set_title("Waveform Preview (Modo Estático)")
            self.canvas.draw()
            self.master.after(200, self.update_visuals)
            return
        
        if len(t) > 500:  # Limita o número de pontos
             t = t[::len(t)//500]    
                                                                                                                                                                                                                                      
        try:
            t = np.linspace(0, 0.03, 1000)  # tempo de 30ms
            mix = np.zeros_like(t)

            with self.synth.voices_lock:
                for voice in self.synth.voices.values():
                    wave = self.synth._generate_voice_wave(voice, t[:, None])
                    adsr = self.synth._calculate_adsr(voice)
                    mix += wave * adsr * voice.velocity

            # Normalize (evita clipping no gráfico)
            mix = np.clip(mix, -1.0, 1.0)

            self.ax.clear()
            self.ax.plot(t, mix)
            self.ax.set_ylim(-1.1, 1.1)
            self.ax.set_title("Waveform Preview (ao vivo)")
            self.canvas.draw()

        except Exception as e:
            print(f"Erro na visualização: {e}")

        self.master.after(100, self.update_visuals)

    def _generate_static_wave(self, phase):
        """
        Gera uma forma de onda estática com base na fase e na forma de onda selecionada.
        """
        config = self.config
        try:
            match config.default_waveform:
                case WaveType.SINE:
                    return np.sin(phase)
                    
                case WaveType.SQUARE:
                    return np.sign(np.sin(phase))
                    
                case WaveType.TRIANGLE:
                    return (2 * np.arcsin(np.sin(phase)) / np.pi)
                    
                case WaveType.SAWTOOTH:
                    return ((phase % (2*np.pi)) / np.pi - 1)
                    
                case WaveType.NOISE:
                    return np.random.uniform(-1, 1, phase.shape)
                    
                case WaveType.PULSE:
                    pulse_width = config.pulse_width
                    return np.where(
                        (phase % (2*np.pi)) < (2*np.pi * pulse_width), 
                        1.0, -1.0
                    )
                    
                case WaveType.SUPER_SAW:
                    # Versão simplificada para preview
                    detune = 0.2
                    voices = [
                        ((phase * (1 + detune * i)) % (2*np.pi) / np.pi - 1)
                        for i in np.linspace(-0.5, 0.5, 7)
                    ]
                    return np.mean(voices, axis=0)
                    
                case WaveType.WAVETABLE:
                    if config.wavetable is not None:
                        wt_size = len(config.wavetable)
                        position = (phase % (2*np.pi)) / (2*np.pi) * wt_size
                        return np.interp(position, np.arange(wt_size), config.wavetable)
                    return np.zeros_like(phase)
                    
                case WaveType.PINK_NOISE:
                    white = np.random.uniform(-1, 1, phase.shape)
                    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
                    a = [1, -2.494956002, 2.017265875, -0.522189400]
                    return lfilter(b, a, white)
                    
                case WaveType.BROWN_NOISE:
                    white = np.random.uniform(-1, 1, phase.shape)
                    brown = np.cumsum(white) * 0.02
                    return np.clip(brown - np.mean(brown), -1, 1)
                    
                case _:
                    return np.zeros_like(phase)
                    
        except Exception as e:
            print(f"Erro na geração estática: {e}")
            return np.zeros_like(phase)

    def on_close(self):
        """
        Fecha a janela e para o sintetizador.
        """
        self.synth.stop()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FullSynthInterface(root)
    root.mainloop()