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

class KeyboardMIDI:
    def __init__(self, synth):
        self.synth = synth
        self.octave_offset = 0  # 0 = oitava central
        self.key_to_note = {
    # --------------------------------------------------
    # Primeira Oitava (C3 - B3) - Teclas Z a M
    # --------------------------------------------------
    'z': 48,  # C3
    's': 49,  # C#3
    'x': 50,  # D3
    'd': 51,  # D#3
    'c': 52,  # E3
    'v': 53,  # F3
    'g': 54,  # F#3
    'b': 55,  # G3
    'h': 56,  # G#3
    'n': 57,  # A3
    'j': 58,  # A#3
    'm': 59,  # B3
    
    # --------------------------------------------------
    # Segunda Oitava (C4 - B4) - Teclas A a L
    # --------------------------------------------------
    'a': 60,  # C4
    'w': 61,  # C#4
    's': 62,  # D4
    'e': 63,  # D#4
    'd': 64,  # E4
    'f': 65,  # F4
    't': 66,  # F#4
    'g': 67,  # G4
    'y': 68,  # G#4
    'h': 69,  # A4
    'u': 70,  # A#4
    'j': 71,  # B4
    
    # --------------------------------------------------
    # Terceira Oitava (C5 - B5) - Teclas Q a P
    # --------------------------------------------------
    'q': 72,  # C5
    '2': 73,  # C#5
    'w': 74,  # D5
    '3': 75,  # D#5
    'e': 76,  # E5
    'r': 77,  # F5
    '5': 78,  # F#5
    't': 79,  # G5
    '6': 80,  # G#5
    'y': 81,  # A5
    '7': 82,  # A#5
    'u': 83,  # B5,
    
    # --------------------------------------------------
    # Teclas Adicionais (C6 - E6)
    # --------------------------------------------------
    'i': 84,  # C6
    '9': 85,  # C#6
    'o': 86,  # D6
    '0': 87,  # D#6
    'p': 88,   # E6
    '1': 'octave_down',  # Diminui a oitava
    '4': 'octave_up',     # Aumenta a oitava
    'shift_l': 'sustained_mode'
}
        self.listener = None

    def start(self):
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()

    def on_press(self, key):
        try:
            if key.char == '1':
                self.octave_offset -= 12  # Desce uma oitava
            elif key.char == '4':
                self.octave_offset += 12  # Sobe uma oitava
            else:
                note = self.key_to_note[key.char] + self.octave_offset
                self.synth._note_on(note, 0.7)
        except:
            pass

    def on_release(self, key):
        try:
            self.synth._note_off(self.key_to_note[key.char])
        except (KeyError, AttributeError):
            pass


class FullSynthInterface:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Synth Controller")
        self.master.geometry("1000x800")
        
        self.config = SynthConfig()
        self.synth = MidiSynth(self.config)
        self.create_widgets()
        self.setup_bindings()
        self.current_waveform = self.config.default_waveform
        self.setup_visuals()
        self.synth.start()
        #
        # Funcionamento do MIDI Keyboard
        self.keyboard_midi = KeyboardMIDI(self.synth)
        self.create_keyboard_help()
        self.keyboard_midi.start()  # Inicia automaticamente

    def create_keyboard_help(self):
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
        notebook = ttk.Notebook(self.master)
        notebook.pack(fill=tk.BOTH, expand=True)

        # OSCILLATOR TAB
        osc_frame = ttk.Frame(notebook)
        self.create_oscillator_controls(osc_frame)
        notebook.add(osc_frame, text="Oscillator")

        # MODULATION TAB
        mod_frame = ttk.Frame(notebook)
        self.create_modulation_controls(mod_frame)
        notebook.add(mod_frame, text="Modulation")

        # ENVELOPE TAB
        env_frame = ttk.Frame(notebook)
        self.create_envelope_controls(env_frame)
        notebook.add(env_frame, text="Envelope")

        # SYSTEM TAB
        sys_frame = ttk.Frame(notebook)
        self.create_system_controls(sys_frame)
        notebook.add(sys_frame, text="System")

    def create_oscillator_controls(self, parent):
        # Waveform Selection
        ttk.Label(parent, text="Waveform:").grid(row=0, column=0, padx=5, pady=5)
        self.waveform = ttk.Combobox(parent, values=[w.value for w in WaveType])
        self.waveform.set(self.config.default_waveform.value)
        self.waveform.grid(row=0, column=1, padx=5, pady=5)
        
        # Pulse Width
        self.pulse_frame = ttk.LabelFrame(parent, text="Pulse Width")
        ttk.Label(self.pulse_frame, text="Width:").grid(row=0, column=0)
        self.pulse_scale = ttk.Scale(self.pulse_frame, from_=0.1, to=0.9, command=self.update_pulse)
        self.pulse_scale.set(self.config.pulse_width)
        self.pulse_scale.grid(row=0, column=1)
        self.pulse_label = ttk.Label(self.pulse_frame, text=f"{self.config.pulse_width:.2f}")
        self.pulse_label.grid(row=0, column=2)
        self.pulse_frame.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        # Super Saw
        self.super_saw_frame = ttk.LabelFrame(parent, text="Super Saw")
        ttk.Label(self.super_saw_frame, text="Voices:").grid(row=0, column=0)
        self.ss_voices = ttk.Scale(self.super_saw_frame, from_=2, to=12, command=self.update_ss_voices)
        self.ss_voices.set(self.config.super_saw_voices)
        self.ss_voices.grid(row=0, column=1)
        self.ss_voices_label = ttk.Label(self.super_saw_frame, text=str(self.config.super_saw_voices))
        self.ss_voices_label.grid(row=0, column=2)
        self.super_saw_frame.grid(row=2, column=0, padx=5, pady=5, sticky='w')

        # Additive Synthesis
        self.additive_frame = ttk.LabelFrame(parent, text="Additive")
        ttk.Label(self.additive_frame, text="Harmonics:").grid(row=0, column=0)
        self.additive_scale = ttk.Scale(self.additive_frame, from_=1, to=16, command=self.update_additive)
        self.additive_scale.set(self.config.additive_harmonics)
        self.additive_scale.grid(row=0, column=1)
        self.additive_label = ttk.Label(self.additive_frame, text=str(self.config.additive_harmonics))
        self.additive_label.grid(row=0, column=2)
        self.additive_frame.grid(row=3, column=0, padx=5, pady=5, sticky='w')

        # Noise Type
        self.noise_frame = ttk.LabelFrame(parent, text="Noise Type")
        self.noise_type = ttk.Combobox(self.noise_frame, values=['white', 'pink', 'brown'])
        self.noise_type.set('white')
        self.noise_type.grid(row=0, column=0)
        self.noise_frame.grid(row=4, column=0, padx=5, pady=5, sticky='w')

        self.update_waveform_visibility()

    def create_modulation_controls(self, parent):
        # FM Modulation
        ttk.Label(parent, text="FM Frequency:").grid(row=0, column=0)
        self.fm_freq = ttk.Scale(parent, from_=0.1, to=5000, command=self.update_fm_freq)
        self.fm_freq.set(self.config.fm_mod_freq)
        self.fm_freq.grid(row=0, column=1)
        self.fm_freq_label = ttk.Label(parent, text=f"{self.config.fm_mod_freq:.1f}")
        self.fm_freq_label.grid(row=0, column=2)

        ttk.Label(parent, text="FM Index:").grid(row=1, column=0)
        self.fm_index = ttk.Scale(parent, from_=0, to=10, command=self.update_fm_index)
        self.fm_index.set(self.config.fm_mod_index)
        self.fm_index.grid(row=1, column=1)
        self.fm_index_label = ttk.Label(parent, text=f"{self.config.fm_mod_index:.2f}")
        self.fm_index_label.grid(row=1, column=2)

    def create_envelope_controls(self, parent):
        # ADSR Controls
        adsr_params = [
            ('Attack', 0.0, 2.0, self.config.attack_time),
            ('Decay', 0.0, 2.0, self.config.decay_time),
            ('Sustain', 0.0, 1.0, self.config.sustain_level),
            ('Release', 0.0, 2.0, self.config.release_time)
        ]
        
        for i, (name, min_val, max_val, init_val) in enumerate(adsr_params):
            ttk.Label(parent, text=f"{name}:").grid(row=i, column=0)
            scale = ttk.Scale(parent, from_=min_val, to=max_val, 
                            command=lambda v, n=name: self.update_adsr(n, v))
            scale.set(init_val)
            scale.grid(row=i, column=1)
            label = ttk.Label(parent, text=f"{init_val:.2f}")
            label.grid(row=i, column=2)
            setattr(self, f"{name.lower()}_label", label)

        # ADSR Curve Type
        ttk.Label(parent, text="Curve Type:").grid(row=4, column=0)
        self.adsr_curve = ttk.Combobox(parent, values=['Linear', 'Exponential'])
        self.adsr_curve.set(self.config.adsr_curve.value.capitalize())
        self.adsr_curve.grid(row=4, column=1)

    def create_system_controls(self, parent):
        # MIDI Devices
        ttk.Label(parent, text="MIDI Input:").grid(row=0, column=0)
        self.midi_devices = ttk.Combobox(parent, values=mido.get_input_names())
        self.midi_devices.grid(row=0, column=1)
        
        # Polyphony
        ttk.Label(parent, text="Max Polyphony:").grid(row=1, column=0)
        self.polyphony = ttk.Scale(parent, from_=1, to=64, command=self.update_polyphony)
        self.polyphony.set(self.config.max_polyphony)
        self.polyphony.grid(row=1, column=1)
        self.polyphony_label = ttk.Label(parent, text=str(self.config.max_polyphony))
        self.polyphony_label.grid(row=1, column=2)
        
        # Wavetable Loader
        ttk.Button(parent, text="Load Wavetable", command=self.load_wavetable).grid(row=2, column=0)

    def setup_bindings(self):
        self.waveform.bind('<<ComboboxSelected>>', self.on_waveform_change)
        self.adsr_curve.bind('<<ComboboxSelected>>', self.update_adsr_curve)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_waveform_visibility(self):
        wave = WaveType(self.waveform.get())
        visibility = {
            WaveType.PULSE: [self.pulse_frame],
            WaveType.SUPER_SAW: [self.super_saw_frame],
            WaveType.ADDITIVE: [self.additive_frame],
            WaveType.NOISE: [self.noise_frame],
            WaveType.PINK_NOISE: [self.noise_frame],
            WaveType.BROWN_NOISE: [self.noise_frame]
        }
        
        # Hide all first
        for f in [self.pulse_frame, self.super_saw_frame, 
                self.additive_frame, self.noise_frame]:
            f.grid_remove()
        
        # Show relevant frames
        for wt in visibility.get(wave, []):
            wt.grid()

    def on_waveform_change(self, event):
        new_wave = WaveType(self.waveform.get())
        self.config.default_waveform = new_wave
        
        # Handle noise type selection
        if new_wave in [WaveType.NOISE, WaveType.PINK_NOISE, WaveType.BROWN_NOISE]:
            self.config.default_waveform = WaveType(self.noise_type.get())
        
        self.update_waveform_visibility()

    def update_pulse(self, value):
        self.config.pulse_width = float(value)
        self.pulse_label.config(text=f"{float(value):.2f}")

    def update_ss_voices(self, value):
        self.config.super_saw_voices = int(float(value))
        self.ss_voices_label.config(text=str(int(float(value))))

    def update_additive(self, value):
        self.config.additive_harmonics = int(float(value))
        self.additive_label.config(text=str(int(float(value))))

    def update_fm_freq(self, value):
        self.config.fm_mod_freq = float(value)
        self.fm_freq_label.config(text=f"{float(value):.1f}")

    def update_fm_index(self, value):
        self.config.fm_mod_index = float(value)
        self.fm_index_label.config(text=f"{float(value):.2f}")

    def update_adsr(self, param, value):
        value = float(value)
        getattr(self, f"{param.lower()}_label").config(text=f"{value:.2f}")
        
        if param == 'Sustain':
            self.config.sustain_level = value
        else:
            setattr(self.config, f"{param.lower()}_time", value)

    def update_adsr_curve(self, event):
        curve = self.adsr_curve.get().lower()
        self.config.adsr_curve = ADSRCurve(curve)

    def update_polyphony(self, value):
        self.config.max_polyphony = int(float(value))
        self.polyphony_label.config(text=str(self.config.max_polyphony))
        
        while len(self.synth.voices) > self.config.max_polyphony:
            self.synth._remove_oldest_voice()

    def load_wavetable(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if file_path:
            try:
                data, _ = sf.read(file_path)
                self.config.wavetable = data
            except Exception as e:
                print(f"Error loading wavetable: {e}")

    def setup_visuals(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.update_visuals()

    def update_visuals(self):
        try:
            t = np.linspace(0, 0.02, 1000)
            phase = 2 * np.pi * 440 * t
            
            # Generate wave sample based on current config
            wave = self.synth._generate_voice_wave(VoiceState(frequency=440, velocity=1), t[:, None])

            self.ax.clear()
            self.ax.plot(t, wave)
            self.ax.set_title("Waveform Preview")
            self.ax.set_ylim(-1.1, 1.1)
            self.canvas.draw()
        except Exception as e:
            print(f"Visualization error: {e}")
        finally:
            self.master.after(100, self.update_visuals)

    def on_close(self):
        self.synth.stop()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FullSynthInterface(root)
    root.mainloop()