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
from threading import Lock

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
    WAVETABLE = 'wavetable'# Síntese por tabela de onda
    PINK_NOISE = 'pink_noise' # Ruído com equalização 1/f
    BROWN_NOISE = 'brown_noise' # Ruído com equalização 1/f²
    ADDITIVE = 'additive'  # Síntese aditiva com harmônicos

class ADSRCurve(Enum):
    """Tipos de curva para o envelope ADSR"""
    LINEAR = 'linear'      # Curva linear de interpolação
    EXPONENTIAL = 'exponential'    # Curva exponencial suave

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
    buffer_size: int = 64
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
    release_start_time: Optional[float] = None  
    phase: float = 0.0

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
        self.voices_lock = Lock()  # Protege o acesso ao dicionário de vozes
        self.lfo_value: float = 0.0
        
        self._init_audio_stream()
        self._init_midi()

    # ==================== INICIALIZAÇÃO ====================
    def _init_audio_stream(self) -> None:
        """Configuração robusta do stream de áudio com verificação de dispositivos"""
        try:
            print("=== Configuração de Áudio ===")
            print(f"Dispositivos disponíveis:\n{sd.query_devices()}\n")
            
            sd.default.samplerate = self.config.sample_rate
            sd.default.blocksize = self.config.buffer_size
            sd.default.device = None  # Usa dispositivo padrão
            print(f"Taxa de amostragem: {self.config.sample_rate} Hz")
            print(f"Tamanho do buffer: {self.config.buffer_size} samples")
            print(f"Dispositivo selecionado: {sd.default.device}\n")
            
        except Exception as e:
            print(f"FALHA NA INICIALIZAÇÃO DO ÁUDIO: {str(e)}")
            raise

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

    # AudioSynth.py - Método _note_on (Versão Corrigida)
    def _note_on(self, note: int, velocity: float) -> None:
        """Implementação robusta com validação completa"""
        try:
            # Validação rigorosa
            if not isinstance(note, int) or not (0 <= note <= 127):
                raise ValueError(f"Nota MIDI inválida: {note}")
            if not (0.0 <= velocity <= 1.0):
                velocity = np.clip(velocity, 0.0, 1.0)

            with self.voices_lock:
                # Remove nota existente
                if note in self.voices:
                    self._note_off(note)

                # Controle de polifonia
                if len(self.voices) >= self.config.max_polyphony:
                    self._remove_oldest_voice()

                # Cria nova voz
                freq = self._note_to_freq(note)
                self.voices[note] = VoiceState(
                    frequency=freq,
                    velocity=velocity,
                    phase=0.0,  # Reset crítico de fase
                    active=True,
                    release_start_time=None
                )
                
                print(f"🎹 NOTE ON | Nota: {note} | Freq: {freq:.1f} Hz")

        except Exception as e:
            print(f"⛔ ERRO NO NOTE ON: {str(e)}")
            raise

    def _note_off(self, note: int) -> None:
        """Processa o término de uma nota musical"""
        if note in self.voices:
            self.voices[note].active = False

    # ==================== GERAÇÃO DE ÁUDIO ====================
    def _audio_callback(self, outdata: np.ndarray, frames: int, time, status) -> None:
        """Callback de áudio com monitoramento completo"""
        if status:
            print(f"⚠️ Status do stream: {status}")

        try:
            output = np.zeros((frames, 2), dtype=np.float32)
            t = (time.currentTime + np.arange(frames)/self.config.sample_rate)[:, None]
            
            with self.voices_lock:
                current_voices = list(self.voices.items())
                to_remove = set()

                # Processamento de cada voz
                for note, voice in current_voices:
                    try:
                        voice.age += frames/self.config.sample_rate
                        adsr = self._calculate_adsr(voice)
                        voice.envelope = adsr

                        # Geração condicional de áudio
                        if adsr > 1e-4:  # Threshold de audibilidade
                            wave = self._generate_voice_wave(voice, t)
                            output += (wave * adsr * voice.velocity)[:, None]
                        else:
                            to_remove.add(note)

                        # Verificação de release finalizado
                        if not voice.active and adsr <= 1e-6:
                            to_remove.add(note)

                    except Exception as e:
                        print(f"Erro na voz {note}: {str(e)}")
                        to_remove.add(note)

                # Remoção segura de vozes
                for note in to_remove:
                    self.voices.pop(note, None)

            # Prevenção de clipping e saída
            np.clip(output, -1, 1, out=outdata)
            
            # Debug de saída
            peak = np.max(np.abs(output))
            print(f"🔈 Pico de saída: {peak:.2f} | Vozes: {len(self.voices)}", end='\r')

        except Exception as e:
            print(f"⛔ ERRO NO CALLBACK: {str(e)}")
            raise

    def _generate_voice_wave(self, voice: VoiceState, t: np.ndarray) -> np.ndarray:
        # Calcula a fase incremental
        phase_increment = 2 * np.pi * voice.frequency * (t[:,0] - t[0,0])
        voice.phase += phase_increment[-1]  # Atualiza a fase final para próxima callback
        carrier_phase = voice.phase - phase_increment[::-1]  # Corrige a direção
        
        # Aplicar modulação FM se habilitada
        if self.config.fm_mod_index > 0:
            modulator = self.config.fm_mod_index * np.sin(2 * np.pi * self.config.fm_mod_freq * t[:,0])
            phase = carrier_phase + modulator
        else:
            phase = carrier_phase

        pulse_width = self.config.pulse_width
        
        # Gerar onda base com a fase modulada
        match self.config.default_waveform:
            case WaveType.SINE:
                wave = np.sin(phase)
                
            case WaveType.SQUARE:
                wave = np.sign(np.sin(phase))
                
            case WaveType.TRIANGLE:
                wave = (2 * np.arcsin(np.sin(phase)) / np.pi)
                
            case WaveType.SAWTOOTH:
                wave = ((phase % (2*np.pi)) / np.pi - 1)
                
            case WaveType.NOISE:
                wave = np.random.uniform(-1, 1, phase.shape)
                
            case WaveType.PULSE:
                wave = np.where(
                    (phase % (2*np.pi)) < (2*np.pi * pulse_width), 
                    1.0, -1.0
                )
                
            case WaveType.SUPER_SAW:
                detune = 0.2
                detuned_freqs = [
                    voice.frequency * (1 + detune * ((i/self.config.super_saw_voices) - 0.5)) 
                    for i in range(self.config.super_saw_voices)
                ]
                
                saws = []
                for freq in detuned_freqs:
                    # Calcula a fase individual para cada oscilador detuned
                    phase_inc = 2 * np.pi * freq * (t[:,0] - t[0,0])
                    individual_phase = voice.phase + phase_inc  # Mantém fase única por voz
                    
                    saw = (individual_phase % (2*np.pi)) / np.pi - 1
                    saws.append(saw)
                
                wave = np.mean(saws, axis=0)
                
                # Atualiza a fase principal APENAS uma vez (evita acumulação múltipla)
                voice.phase += 2 * np.pi * voice.frequency * (t[-1,0] - t[0,0])
                voice.phase %= 2 * np.pi  # Mantém a fase dentro de 0-2π
                            
            case WaveType.WAVETABLE:
                if self.config.wavetable is not None:
                    wt_size = len(self.config.wavetable)
                    position = (phase % (2*np.pi)) / (2*np.pi) * wt_size
                    wave = np.interp(position, np.arange(wt_size), self.config.wavetable)
                else:
                    wave = np.zeros_like(phase)
                    
            case WaveType.PINK_NOISE:
                white = np.random.uniform(-1, 1, phase.shape)
                b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
                a = [1, -2.494956002, 2.017265875, -0.522189400]
                wave = lfilter(b, a, white)
                
            case WaveType.BROWN_NOISE:
                white = np.random.uniform(-1, 1, phase.shape)
                wave = np.cumsum(white) * 0.02
                wave -= np.mean(wave)  # Centralizar
                wave = np.clip(wave, -1, 1)  # Evitar clipping
                
            case WaveType.ADDITIVE:
                harmonics = self.config.additive_harmonics
                amps = [1/(i+1) for i in range(harmonics)]
                waves = [amps[i] * np.sin((i+1)*phase) for i in range(harmonics)]
                wave = np.sum(waves, axis=0)
                
            case _:
                raise ValueError(f"Tipo de onda não suportado: {self.config.default_waveform}")
        
        return wave.astype(np.float32)

    # ==================== ENVELOPE ADSR ====================
    # AudioSynth.py - Método _calculate_adsr (Versão Corrigida)
    def _calculate_adsr(self, voice: VoiceState) -> float:
        """Cálculo do envelope com proteção completa"""
        try:
            total_time = voice.age
            
            if voice.active:
                # Attack
                if total_time < self.config.attack_time:
                    adsr = total_time / self.config.attack_time
                # Decay
                elif total_time < (self.config.attack_time + self.config.decay_time):
                    decay_progress = (total_time - self.config.attack_time) / self.config.decay_time
                    adsr = 1 - (1 - self.config.sustain_level) * decay_progress
                # Sustain
                else:
                    adsr = self.config.sustain_level
            else:
                # Release
                if voice.release_start_time is None:
                    voice.release_start_time = total_time
                
                release_elapsed = total_time - voice.release_start_time
                release_progress = min(release_elapsed / self.config.release_time, 1.0)
                adsr = max(0.0, voice.envelope * (1 - release_progress))

            # Aplicação da curva
            if self.config.adsr_curve == ADSRCurve.EXPONENTIAL:
                adsr **= 1.5  # Suavização exponencial

            # Garantia de valores válidos
            adsr = np.clip(adsr, 0.0, 1.0).item()

            # Debug seletivo
            if adsr > 0.01:
                print(
                    f"📈 Envelope: {adsr:.2f} | " +
                    f"Estado: {'Ativo' if voice.active else 'Release'} | " +
                    f"Freq: {voice.frequency:.1f} Hz"
                )

            return adsr

        except Exception as e:
            print(f"⛔ ERRO NO ADSR: {str(e)}")
            return 0.0

    # ==================== UTILITÁRIOS ====================
    @staticmethod
    def _note_to_freq(note: int) -> float:
        """Conversão segura com validação"""
        if not isinstance(note, int) or not (0 <= note <= 127):
            raise ValueError(f"Nota inválida: {note}")
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