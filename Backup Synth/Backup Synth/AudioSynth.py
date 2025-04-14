"""
Sistema de síntese de áudio MIDI profissional com suporte a múltiplos tipos de onda
e gestão de polifonia avançada.

Características principais:
- Síntese de 11 tipos de onda diferentes
- Integração MIDI completa
- Gestão de vozes com priorização inteligente
- Geração de áudio em tempo real de baixa latência
- Arquitetura modular e extensível

Autor: Gabriel Tomasi
Versão: 1.0.0
Data: 04/04/2025
"""

import mido
import numpy as np
import sounddevice as sd
import soundfile as sf
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple, Callable
from functools import wraps
from enum import Enum
from scipy.signal import butter, lfilter, firwin

# ==================== ENUMS E ESTRUTURAS ====================
class WaveType(Enum):
    """Tipos de onda disponíveis para síntese"""
    SINE = 'sine'          # Onda senoidal clássica
    SQUARE = 'square'      # Onda quadrada com duty cycle ajustável
    TRIANGLE = 'triangle'  # Onda triangular simétrica
    SAWTOOTH = 'sawtooth'  # Dente de serra ascendente
    NOISE = 'noise'        # Ruído branco não filtrado
    PULSE = 'pulse'        # Onda pulsada com largura ajustável
    SUPER_SAW = 'super_saw'# Múltiplas dentes de serra com detune
    FM = 'fm'              # Síntese por modulação de frequência
    WAVETABLE = 'wavetable'# Síntese por tabela de onda
    PINK_NOISE = 'pink_noise' # Ruído com equalização 1/f
    BROWN_NOISE = 'brown_noise' # Ruído com equalização 1/f²
    ADDITIVE = 'additive'  # Síntese aditiva com harmônicos

class ADSRCurve(Enum):
    """Tipos de curva para o envelope ADSR"""
    LINEAR = 'linear'      # Curva linear de interpolação
    EXPONENTIAL = 'exp'    # Curva exponencial suave

@dataclass
class SynthConfig:
    """
    Configurações globais do sintetizador
    
    Parâmetros:
    - sample_rate: Taxa de amostragem em Hz (padrão: 44100)
    - buffer_size: Tamanho do buffer de áudio (potências de 2 recomendadas)
    - max_polyphony: Número máximo de vozes simultâneas
    - midi_port: Nome do dispositivo MIDI de entrada (opcional)
    - default_waveform: Tipo de onda padrão
    - fm_mod_freq: Frequência do modulador FM em Hz
    - fm_mod_index: Índice de modulação FM
    - pulse_width: Largura do pulso (0.1-0.9)
    - wavetable: Tabela de onda personalizada (numpy array)
    """
    sample_rate: int = 44100
    buffer_size: int = 1024
    max_polyphony: int = 16
    midi_port: Optional[str] = None
    default_waveform: WaveType = WaveType.SINE
    fm_mod_freq: float = 5.0
    fm_mod_index: float = 1.0
    pulse_width: float = 0.5
    wavetable: np.ndarray = None
    attack_time: float = 0.1
    decay_time: float = 0.2
    sustain_level: float = 0.7
    release_time: float = 0.3
    adsr_curve: ADSRCurve = ADSRCurve.LINEAR
    additive_harmonics: int = 8  # Número de harmônicos para síntese aditiva
    super_saw_voices: int = 7    # Número de vozes para Super Saw

@dataclass
class VoiceState:
    """
    Estado de uma voz ativa no sintetizador
    
    Campos:
    - frequency: Frequência atual da nota em Hz
    - velocity: Velocidade da nota (0.0-1.0)
    - age: Tempo desde o início da nota em segundos
    - envelope: Valor atual do envelope (0.0-1.0)
    - active: Flag indicando se a nota está ativa
    """
    frequency: float
    velocity: float
    age: float = 0.0
    envelope: float = 0.0
    active: bool = True

# ==================== DECORATORS E UTILITIES ====================
def validate_positive(func: Callable) -> Callable:
    """Decorator para validar parâmetros numéricos positivos"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for name, value in zip(func.__code__.co_varnames[1:], args):
            if isinstance(value, (int, float)) and value < 0:
                raise ValueError(f"Valor negativo não permitido para {name}: {value}")
        return func(self, *args, **kwargs)
    return wrapper

# ==================== CLASSE PRINCIPAL ====================
class MidiSynth:
    """Classe principal do sintetizador MIDI"""
    
    def __init__(self, config: SynthConfig = SynthConfig()):
        """
        Inicializa o sintetizador com a configuração especificada
        
        Args:
            config: Objeto SynthConfig com parâmetros de configuração
        """
        self.config = config
        self.voices: Dict[int, VoiceState] = {}
        self._stream: Optional[sd.OutputStream] = None
        self._midi_in: Optional[mido.ports.BaseInput] = None
        self.lfo_value: float = 0.0
        
        self._init_audio_stream()
        self._init_midi()

    # ==================== INICIALIZAÇÃO ====================
    def _init_audio_stream(self) -> None:
        """Configura os parâmetros do stream de áudio"""
        sd.default.samplerate = self.config.sample_rate
        sd.default.blocksize = self.config.buffer_size
        sd.default.latency = 'high'
        sd.default.channels = 2

    def _init_midi(self) -> None:
        """Inicializa a interface MIDI se especificado na configuração"""
        if self.config.midi_port:
            try:
                self._midi_in = mido.open_input(self.config.midi_port)
                self._midi_in.callback = self._midi_callback
            except Exception as e:
                print(f"Erro MIDI: {e}")

    # ==================== PROCESSAMENTO MIDI ====================
    def _midi_callback(self, message: mido.Message) -> None:
        """Callback para processamento de mensagens MIDI recebidas"""
        match message.type:
            case 'note_on' if message.velocity > 0:
                self._note_on(message.note, message.velocity/127)
            case 'note_off' | 'note_on':
                self._note_off(message.note)
            case 'control_change':
                self._handle_control_change(message.control, message.value)
            case 'pitchwheel':
                self._handle_pitch_bend(message.pitch)

    def _note_on(self, note: int, velocity: float) -> None:
        """Processa o início de uma nota musical"""
        if len(self.voices) >= self.config.max_polyphony:
            self._remove_oldest_voice()
        freq = self._note_to_freq(note)
        self.voices[note] = VoiceState(frequency=freq, velocity=velocity)

    def _note_off(self, note: int) -> None:
        """Processa o término de uma nota musical"""
        if note in self.voices:
            self.voices[note].active = False

    # ==================== GERAÇÃO DE ÁUDIO ====================
    def _audio_callback(self, outdata: np.ndarray, frames: int, time, status) -> None:
        """
        Callback principal para geração de áudio em tempo real
        
        Args:
            outdata: Buffer de saída de áudio (preenchido pelo método)
            frames: Número de frames a serem gerados
            time: Informações temporais do stream
            status: Status do stream de áudio
        """
        if status:
            print(f"Status do stream de áudio: {status}")
        
        # Gera o sinal para cada voz ativa
        t = (time.currentTime + np.arange(frames)/self.config.sample_rate)[:, None]
        output = np.zeros((frames, 2), dtype=np.float32)
        
        for note, voice in list(self.voices.items()):
            voice.age += frames/self.config.sample_rate
            wave = self._generate_voice_wave(voice, t)
            adsr = self._calculate_adsr(voice)
            output += (wave * adsr * voice.velocity)[:, None]
            
            # Remove vozes com envelope zerado
            if adsr <= 0:
                del self.voices[note]

        # Prevenção de clipping e conversão final
        output = np.clip(output, -1, 1).astype(np.float32)
        outdata[:] = output

    def _generate_voice_wave(self, voice: VoiceState, t: np.ndarray) -> np.ndarray:
        """
        Gera a forma de onda para uma voz específica
        
        Args:
            voice: Estado da voz a ser gerada
            t: Array de tempos normalizados
            
        Returns:
            Array numpy com os samples gerados
        """
        phase = 2 * np.pi * voice.frequency * t[:,0]
        mod_phase = 2 * np.pi * self.config.fm_mod_freq * t[:,0]
        pulse_width = self.config.pulse_width
        
        # Seleção do tipo de onda com match pattern
        match self.config.default_waveform:
            case WaveType.SINE:
                return np.sin(phase).astype(np.float32)
                
            case WaveType.SQUARE:
                return np.sign(np.sin(phase)).astype(np.float32)
            
            case WaveType.TRIANGLE:
                return (2 * np.arcsin(np.sin(phase)) / np.pi).astype(np.float32)
            
            case WaveType.SAWTOOTH:
                return ((phase % (2*np.pi)) / np.pi - 1).astype(np.float32)
            
            case WaveType.NOISE:
                return np.random.uniform(-1, 1, phase.shape).astype(np.float32)
            
            case WaveType.PULSE:
                duty_cycle = pulse_width
                return np.where(
                    (phase % (2*np.pi)) < (2*np.pi * duty_cycle), 
                    1.0, -1.0
                ).astype(np.float32)
            
            case WaveType.SUPER_SAW:
                detune = 0.2
                voices = 7
                detuned = [voice.frequency * (1 + detune * ((i/voices) - 0.5)) 
                          for i in range(voices)]
                saws = [((2 * np.pi * freq * t[:,0]) % (2*np.pi)) / np.pi - 1 
                       for freq in detuned]
                return np.mean(saws, axis=0).astype(np.float32)
            
            case WaveType.FM:
                modulator = self.config.fm_mod_index * np.sin(mod_phase)
                return np.sin(phase + modulator).astype(np.float32)
            
            case WaveType.WAVETABLE:
                wt_size = 512
                wave_table = np.linspace(0, 2*np.pi, wt_size)
                position = (phase % (2*np.pi)) / (2*np.pi) * wt_size
                return np.interp(position, wave_table, 
                                self.config.wavetable).astype(np.float32)
            
            case WaveType.PINK_NOISE:
                white = np.random.uniform(-1, 1, phase.shape)
                b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
                a = [1, -2.494956002, 2.017265875, -0.522189400]
                return lfilter(b, a, white).astype(np.float32)
            
            case WaveType.BROWN_NOISE:
                white = np.random.uniform(-1, 1, phase.shape)
                return np.cumsum(white) * 0.02
            
            case WaveType.ADDITIVE:
                harmonics = 8
                amps = [1/(i+1) for i in range(harmonics)]
                waves = [amps[i] * np.sin((i+1)*phase) for i in range(harmonics)]
                return np.sum(waves, axis=0).astype(np.float32)
            
            case _:
                raise ValueError(f"Tipo de onda não suportado: {self.config.default_waveform}")

    # ==================== ENVELOPE ADSR ====================
    def _calculate_adsr(self, voice: VoiceState) -> float:
        total_time = voice.age
        attack = self.config.attack_time
        decay = self.config.decay_time
        sustain = self.config.sustain_level
        release = self.config.release_time

        if voice.active:
            if total_time < attack:
                return total_time / attack
            elif total_time < attack + decay:
                return 1 - (1 - sustain) * ((total_time - attack) / decay)
            else:
                return sustain
        else:
            release_start = max(attack + decay, 0)
            release_progress = (total_time - release_start) / release
            return max(0.0, sustain * (1 - release_progress))

    # ==================== UTILITÁRIOS ====================
    @staticmethod
    def _note_to_freq(note: int) -> float:
        """Converte valor MIDI para frequência em Hz (A4 = 440Hz)"""
        return 440.0 * (2.0 ** ((note - 69) / 12.0))

    def _remove_oldest_voice(self) -> None:
        """Remove a voz mais antiga quando atinge a polifonia máxima"""
        oldest_note = min(self.voices.keys(), key=lambda k: self.voices[k].age)
        del self.voices[oldest_note]

    # ==================== CONTROLE DE FLUXO ====================
    def start(self) -> None:
        """Inicia a reprodução de áudio e processamento MIDI"""
        self._stream = sd.OutputStream(
            callback=self._audio_callback,
            samplerate=self.config.sample_rate,
            blocksize=self.config.buffer_size,
            channels=2
        )
        self._stream.start()

    def stop(self) -> None:
        """Para a reprodução e libera recursos"""
        if self._stream:
            self._stream.close()
        if self._midi_in:
            self._midi_in.close()

    def __enter__(self):
        """Suporte para gerenciamento de contexto"""
        self.start()
        return self

    def __exit__(self, *args):
        """Garante liberação de recursos ao sair do contexto"""
        self.stop()

# ==================== EXEMPLO DE USO ====================
if __name__ == "__main__":
    # Configuração básica para teste
    config = SynthConfig(
        midi_port="Dispositivo MIDI",  # Altere para seu dispositivo
        max_polyphony=24,
        default_waveform=WaveType.SUPER_SAW
    )
    
    # Execução segura com gerenciamento de contexto
    with MidiSynth(config) as synth:
        input("Pressione Enter para parar...")