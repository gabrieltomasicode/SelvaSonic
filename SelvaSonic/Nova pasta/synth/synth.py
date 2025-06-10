<<<<<<< HEAD
from .config import SynthConfig
from .voices import  VoiceManager
from .audio import audio_callback
from .midi import midi_callback
from synth.utils import note_to_freq, get_time
import sounddevice as sd
from functools import partial
import mido

class MidiSynth:
    """
    Classe principal do sintetizador MIDI.

    Responsável por inicializar o áudio, processar eventos MIDI,
    gerenciar vozes, gerar áudio em tempo real e aplicar envelopes e filtros.
    """

    def __init__(self, config: SynthConfig = SynthConfig()):
        self.config = config
        self.voice_manager = VoiceManager(self.config.max_polyphony)
         
        try:
            if self.config.midi_port:
                self.midi_in = mido.open_input(
                    self.config.midi_port, 
                    callback=lambda msg: midi_callback(msg, self)
                )
            else:
                self.midi_in = None
                print("⚠️ Nenhuma porta MIDI especificada.")
        except OSError:
            self.midi_in = None
            print(f"⚠️ Porta MIDI '{self.config.midi_port}' não encontrada.")
            # Lista portas disponíveis
            available_ports = mido.get_input_names()
            if available_ports:
                print("Portas MIDI disponíveis:", available_ports)
            else:
                print("Nenhuma porta MIDI disponível no sistema.")
        self.running = False
        self.stream = sd.OutputStream(
            samplerate=self.config.sample_rate,
            blocksize=self.config.buffer_size,
            channels=2,
            callback=partial(
                audio_callback,
                config=self.config,
                voices=self.voice_manager.get_voices(),
                voices_lock=self.voice_manager.get_lock()
            )
        )
    
    
    def start(self):
        self.stream.start()
        self.running = True
        print("✅ Sintetizador iniciado.")

    def stop(self):
        self.stream.stop()
        self.running = False
        print("⏹️ Sintetizador parado.")
    
    def note_on(self, note: int, velocity: float):
        freq = note_to_freq(note)
        self.voice_manager.note_on(note, velocity, freq, self.get_time)
        print(f"Nota ligada: {note} freq: {freq:.2f}Hz vel: {velocity:.2f}")

    def note_off(self, note: int):
        self.voice_manager.note_off(note, self.get_time)
        print(f"Nota desligada: {note}")
    
    def on_close(self):
        """Encerra o sintetizador e libera recursos."""
        if self.running:
            self.stop()
        if self.midi_in is not None:
            self.midi_in.close()
        print("🛑 Recursos do sintetizador liberados.")

    def set_lfo_freq(self, value):
        """Atualiza a frequência do LFO em tempo real."""
        self.config.lfo_freq = float(value)

    def set_lfo_depth(self, value):
        """Atualiza a profundidade do LFO em tempo real."""
        self.config.lfo_depth = float(value)

    def set_lfo_target(self, value):
        """Atualiza o alvo do LFO em tempo real."""
        self.config.lfo_target = value

    def set_fm_freq(self, value):
        """Atualiza a frequência de modulação FM em tempo real."""
        self.config.fm_mod_freq = float(value)

    def set_fm_index(self, value):
        """Atualiza o índice de modulação FM em tempo real."""
        self.config.fm_mod_index = float(value)

    def set_hfo_freq(self, value):
        """Atualiza a frequência do HFO em tempo real."""
        self.config.hfo_freq = float(value)

    def set_hfo_depth(self, value):
        """Atualiza a profundidade do HFO em tempo real."""
        self.config.hfo_depth = float(value)

    def set_hfo_target(self, value):
        """Atualiza o alvo do HFO em tempo real."""
        self.config.hfo_target = value

    def set_additive(self, value):
        """Atualiza o parâmetro aditivo em tempo real."""
        self.config.additive = float(value)
    
    def set_waveform(self, waveform):
        self.config.default_waveform = waveform
    
    def set_pulse_width(self, value):
        self.config.pulse_width = float(value)

    def set_supersaw_voices(self, value):
        print("super_saw_voices:", value)
        try:
            self.config.super_saw_voices = int(float(value))
        except ValueError:
            print(f"Valor inválido para super_saw_voices: {value}")

    @staticmethod
    def __enter__(self):
        self.start()
        return self

    @staticmethod
    def get_time():
        return get_time()

    def __exit__(self, *args):
=======
from .config import SynthConfig
from .voices import  VoiceManager
from .audio import audio_callback
from .midi import midi_callback
from synth.utils import note_to_freq, get_time
import sounddevice as sd
from functools import partial
import mido

class MidiSynth:
    """
    Classe principal do sintetizador MIDI.

    Responsável por inicializar o áudio, processar eventos MIDI,
    gerenciar vozes, gerar áudio em tempo real e aplicar envelopes e filtros.
    """

    def __init__(self, config: SynthConfig = SynthConfig()):
        self.config = config
        self.voice_manager = VoiceManager(self.config.max_polyphony)
         
        try:
            if self.config.midi_port:
                self.midi_in = mido.open_input(
                    self.config.midi_port, 
                    callback=lambda msg: midi_callback(msg, self)
                )
            else:
                self.midi_in = None
                print("⚠️ Nenhuma porta MIDI especificada.")
        except OSError:
            self.midi_in = None
            print(f"⚠️ Porta MIDI '{self.config.midi_port}' não encontrada.")
            # Lista portas disponíveis
            available_ports = mido.get_input_names()
            if available_ports:
                print("Portas MIDI disponíveis:", available_ports)
            else:
                print("Nenhuma porta MIDI disponível no sistema.")
        self.running = False
        self.stream = sd.OutputStream(
            samplerate=self.config.sample_rate,
            blocksize=self.config.buffer_size,
            channels=2,
            callback=partial(
                audio_callback,
                config=self.config,
                voices=self.voice_manager.get_voices(),
                voices_lock=self.voice_manager.get_lock()
            )
        )
    
    
    def start(self):
        self.stream.start()
        self.running = True
        print("✅ Sintetizador iniciado.")

    def stop(self):
        self.stream.stop()
        self.running = False
        print("⏹️ Sintetizador parado.")
    
    def note_on(self, note: int, velocity: float):
        freq = note_to_freq(note)
        self.voice_manager.note_on(note, velocity, freq, self.get_time)
        print(f"Nota ligada: {note} freq: {freq:.2f}Hz vel: {velocity:.2f}")

    def note_off(self, note: int):
        self.voice_manager.note_off(note, self.get_time)
        print(f"Nota desligada: {note}")
    
    def on_close(self):
        """Encerra o sintetizador e libera recursos."""
        if self.running:
            self.stop()
        if self.midi_in is not None:
            self.midi_in.close()
        print("🛑 Recursos do sintetizador liberados.")

    def set_lfo_freq(self, value):
        """Atualiza a frequência do LFO em tempo real."""
        self.config.lfo_freq = float(value)

    def set_lfo_depth(self, value):
        """Atualiza a profundidade do LFO em tempo real."""
        self.config.lfo_depth = float(value)

    def set_lfo_target(self, value):
        """Atualiza o alvo do LFO em tempo real."""
        self.config.lfo_target = value

    def set_fm_freq(self, value):
        """Atualiza a frequência de modulação FM em tempo real."""
        self.config.fm_mod_freq = float(value)

    def set_fm_index(self, value):
        """Atualiza o índice de modulação FM em tempo real."""
        self.config.fm_mod_index = float(value)

    def set_hfo_freq(self, value):
        """Atualiza a frequência do HFO em tempo real."""
        self.config.hfo_freq = float(value)

    def set_hfo_depth(self, value):
        """Atualiza a profundidade do HFO em tempo real."""
        self.config.hfo_depth = float(value)

    def set_hfo_target(self, value):
        """Atualiza o alvo do HFO em tempo real."""
        self.config.hfo_target = value

    def set_additive(self, value):
        """Atualiza o parâmetro aditivo em tempo real."""
        self.config.additive = float(value)
    
    def set_waveform(self, waveform):
        self.config.default_waveform = waveform
    
    def set_pulse_width(self, value):
        self.config.pulse_width = float(value)

    def set_supersaw_voices(self, value):
        print("super_saw_voices:", value)
        try:
            self.config.super_saw_voices = int(float(value))
        except ValueError:
            print(f"Valor inválido para super_saw_voices: {value}")

    @staticmethod
    def __enter__(self):
        self.start()
        return self

    @staticmethod
    def get_time():
        return get_time()

    def __exit__(self, *args):
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8
        self.stop()