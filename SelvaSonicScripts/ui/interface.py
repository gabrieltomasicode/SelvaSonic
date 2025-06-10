import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
    def __init__(self, master):
        """
        Inicializa a interface gráfica do sintetizador.

        Parâmetros:
            master: Instância principal do Tkinter.
        """
        self.master = master
        self.master.title("Advanced Synth Controller")
        self.master.geometry("1000x800")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        # Frame principal para organizar notebook e canvas
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.rowconfigure(0, weight=1)  # notebook cresce
        self.main_frame.rowconfigure(1, weight=0)  # canvas não cresce
        self.main_frame.columnconfigure(0, weight=1)

        self.config = SynthConfig()
        self.synth = MidiSynth()
        self.keyboard_midi = KeyboardMIDI(self.synth, self.master)

        self.visual_update_id = None
        self.setup_visuals()
        self.synth.start()

        self.create_widgets()
        self.setup_bindings()
        self.current_waveform = self.config.default_waveform
        self.setup_visuals()
        self.synth.start()

        self.create_keyboard_help()
        self.keyboard_midi.start()
    
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
            load_config(self.config, filename=file_path)
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
        self.update_visuals()  # <-- Adicione esta linha
        ])

        self.osc_frame.grid(row=0, column=0, sticky="nsew")
        notebook.add(osc_frame, text="Oscilador")

        # Envelope (ADSR) em aba separada
        env_frame, env_sliders, env_labels, curve_combo = create_envelope_controls(
            notebook, self.config,
            lambda param, v, lbl: [update_adsr(self.config, param, v, lbl), self.update_adsr_param(param, v)],
            lambda e: update_adsr_curve(self.config, curve_combo)
        )
        env_frame.rowconfigure(0, weight=1)      # <-- Adicione aqui
        env_frame.columnconfigure(0, weight=1)   # <-- Adicione aqui
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
        """
        Configura a visualização da forma de onda.

        Notas:
            - Cria o canvas do matplotlib e o botão de pausar/retomar visualização.
        """
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="ew")

        self.visual_paused = False
        self.pause_button = ttk.Button(self.master, text="⏸ Pausar Visualização", command=self.toggle_visual)
        self.pause_button.grid(row=3, column=0, pady=5, sticky="ew")

        self.start_visual_updates()

    def update_visuals(self):
        """
        Atualiza a visualização da forma de onda em tempo real.

        Notas:
            - Mostra preview estático se não houver vozes ativas.
            - Mostra preview ao vivo se houver vozes.
        """
          # Debug 1
        t = np.linspace(0, 0.03, 1000)
        mix = np.zeros_like(t)
        voices = self.synth.voice_manager.get_voices()
        if not voices:
            # Mostra preview estático se não houver vozes
            phase = 2 * np.pi * 440 * t
            wave = generate_static_wave(phase, self.config)
            update_waveform_plot(self.ax, t, wave, title="Waveform Preview (Modo Estático)")
            self.canvas.draw()
            
            return

        with self.synth.voice_manager.get_lock():
            for voice in self.synth.voice_manager.get_voices().values():
                print("Processando voz:", voice)  # Debug 2
                wave = generate_wave(voice, t, self.synth.config)
                adsr = calculate_adsr(voice, self.synth.config)
                print("Max wave:", np.max(wave), "ADSR:", adsr)  # Debug 3
                mix += wave * adsr * voice.velocity

        print("Mix max:", np.max(mix), "min:", np.min(mix))  # Debug 4

        mix = np.clip(mix, -1.0, 1.0)
        update_waveform_plot(self.ax, t, mix, title="Waveform Preview (ao vivo)")
        self.canvas.draw()
        print("Desenhou canvas")  # Debug 5

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
            except Exception as e:
                print(f"Erro na atualização visual: {e}")
            finally:
                self.visual_update_id = self.master.after(100, update)
                
        self.visual_update_id = self.master.after(100, update)

    

    def toggle_visual(self):
        """
        Alterna entre pausar e retomar a visualização da forma de onda.

        Notas:
            - Atualiza o texto do botão de pausa/retomada.
            - Mostra preview estático se não houver vozes.
        """
        self.visual_paused = not self.visual_paused
        new_text = "▶ Retomar Visualização" if self.visual_paused else "⏸ Pausar Visualização"
        self.pause_button.config(text=new_text)

        
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
                for voice in self.synth.voice_manager.get_voices().values():
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