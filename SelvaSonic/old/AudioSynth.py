"""
SelvaSonic AudioSynth

Sistema profissional de síntese de áudio MIDI em Python, projetado para aplicações musicais, experimentação sonora e integração com controladores MIDI.

Principais recursos:
- Suporte a 11 tipos de onda, incluindo Super Saw, Pulse, Noise, Pink/Brown Noise e Wavetable.
- Gestão avançada de polifonia com priorização e remoção automática de vozes antigas.
- Envelope ADSR configurável com curvas linear ou exponencial.
- Modulação FM, LFO e HFO com roteamento flexível (pitch, pulse, volume, etc).
- Filtros digitais (lowpass, highpass, bandpass) configuráveis em tempo real.
- Integração MIDI completa (note on/off, pitch bend, control change).
- Geração de áudio em tempo real com baixa latência usando sounddevice.
- Arquitetura modular, extensível e orientada a objetos.
- Suporte a síntese aditiva e wavetable customizada.
- Pronto para uso em aplicações interativas, como engine de áudio.

Autor: Gabriel Tomasi
Versão: 2.1.1
Data: 20/05/2025
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

# ==================== ENUMS E ESTRUTURAS ====================================================================================================
class WaveType(Enum):
    """
    Tipos de onda disponíveis para síntese.

    Valores:
        SINE: Onda senoidal clássica.
        SQUARE: Onda quadrada com duty cycle ajustável.
        TRIANGLE: Onda triangular simétrica.
        SAWTOOTH: Dente de serra ascendente.
        NOISE: Ruído branco não filtrado.
        PULSE: Onda pulsada com largura ajustável.
        SUPER_SAW: Múltiplas dentes de serra com detune.
        WAVETABLE: Síntese por tabela de onda.
        PINK_NOISE: Ruído com equalização 1/f.
        BROWN_NOISE: Ruído com equalização 1/f².
    """
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
    

class ADSRCurve(Enum):
    """
    Enumeração dos tipos de curva para o envelope ADSR.

    Valores:
        LINEAR: Curva linear de interpolação.
        EXPONENTIAL: Curva exponencial suave.
    """
    LINEAR = 'linear'      
    EXPONENTIAL = 'exponential'    

@dataclass
class SynthConfig:
    """
    Configurações globais do sintetizador.

    Atributos:
        sample_rate (int): Taxa de amostragem em Hz.
        buffer_size (int): Tamanho do buffer de áudio.
        max_polyphony (int): Número máximo de vozes simultâneas.
        midi_port (Optional[str]): Nome do dispositivo MIDI de entrada.
        default_waveform (WaveType): Tipo de onda padrão.
        fm_mod_freq (float): Frequência do modulador FM em Hz.
        fm_mod_index (float): Índice de modulação FM.
        pulse_width (float): Largura do pulso (0.1-0.9).
        wavetable (np.ndarray): Tabela de onda personalizada.
        attack_time (float): Tempo de ataque do envelope.
        decay_time (float): Tempo de decaimento do envelope.
        sustain_level (float): Nível de sustentação do envelope.
        release_time (float): Tempo de release do envelope.
        adsr_curve (ADSRCurve): Tipo de curva do envelope.
        additive_harmonics (int): Número de harmônicos para síntese aditiva.
        super_saw_voices (int): Número de vozes para Super Saw.
        lfo_freq (float): Frequência do LFO.
        lfo_depth (float): Profundidade do LFO.
        lfo_target (str): Parâmetro alvo do LFO.
        hfo_freq (float): Frequência do HFO.
        hfo_depth (float): Profundidade do HFO.
        hfo_target (str): Parâmetro alvo do HFO.
        filter_type (str): Tipo de filtro ('lowpass', 'highpass', 'bandpass').
        filter_freq (float): Frequência de corte do filtro.
        filter_q (float): Q do filtro.
    """
    sample_rate: int = 22050  # Menor taxa de amostragem reduz pela metade o custo computacional.
    buffer_size: int = 128    # Aumentar o buffer diminui a frequência de chamadas de áudio, melhor para performance.
    max_polyphony: int = 8    # Reduzir a polifonia reduz muito o custo por frame de áudio.
    midi_port: Optional[str] = None

    default_waveform: WaveType = WaveType.SINE  # Seno é o mais leve de gerar (1 operação trigonométrica por sample).
    fm_mod_freq: float = 0.0    # Desativa FM por padrão.
    fm_mod_index: float = 0.0   # Zero garante que FM não é processado.

    pulse_width: float = 0.5  # Valor padrão, mas evitar formas de onda pulsadas melhora performance.

    wavetable: np.ndarray = None  # Apenas use se necessário, e com waveforms pré-interpoladas de baixa resolução.

    attack_time: float = 0.01  # Ataques rápidos consomem menos CPU (menos samples para transições).
    decay_time: float = 0.05
    sustain_level: float = 0.7
    release_time: float = 0.05  # Releases curtos liberam vozes mais rápido.

    adsr_curve: ADSRCurve = ADSRCurve.LINEAR  # Linear é mais leve que exponencial.

    additive_harmonics: int = 3  # Menos harmônicos = menos somas senoidais = mais performance.
    super_saw_voices: int = 3    # Reduzir de 7 para 3 já simula o efeito mantendo performance.

    lfo_freq: float = 0.0   # Desativa LFO por padrão.
    lfo_depth: float = 0.0
    lfo_target: str = "pitch"

    hfo_freq: float = 0.0   # Desativa HFO (frequência alta = custo alto).
    hfo_depth: float = 0.0
    hfo_target: str = "pitch"

    filter_type: str = "lowpass"
    filter_freq: float = 5000.0  # Alta o suficiente para não cortar muito, mas evita recalcular filtros em tempo real.
    filter_q: float = 0.707      # Valor padrão (Butterworth), não ressonante.


    def validate(self):
        """
        Valida os parâmetros da configuração do sintetizador.

        Raises:
            ValueError: Se algum parâmetro for inválido.
        """
        if self.sample_rate <= 0:
            raise ValueError("Sample rate deve ser maior que 0.")
        if self.buffer_size <= 0:
            raise ValueError("Buffer size deve ser maior que 0.")
        if self.max_polyphony <= 0:
            raise ValueError("Max polyphony deve ser maior que 0.")

@dataclass
class VoiceState:
    """
    Estado de uma voz ativa no sintetizador.

    Atributos:
        frequency (float): Frequência atual da nota em Hz.
        velocity (float): Velocidade da nota (0.0-1.0).
        age (float): Tempo desde o início da nota em segundos.
        envelope (float): Valor atual do envelope (0.0-1.0).
        active (bool): Flag indicando se a nota está ativa.
        release_start_time (Optional[float]): Momento de início do release.
        phase (float): Fase atual da onda.
    """
    frequency: float
    velocity: float
    age: float = 0.0
    envelope: float = 0.0
    active: bool = True
    release_start_time: Optional[float] = None  
    phase: float = 0.0

# ==================== DECORATORS E UTILITIES ====================================================================================================
def validate_positive(func: Callable) -> Callable:
    """
    Decorador para validar que todos os parâmetros numéricos são positivos.

    Args:
        func (Callable): Função a ser decorada.

    Returns:
        Callable: Função decorada que lança ValueError para valores negativos.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for name, value in zip(func.__code__.co_varnames[1:], args):
            if isinstance(value, (int, float)) and value < 0:
                raise ValueError(f"Valor negativo não permitido para {name}: {value}")
        return func(self, *args, **kwargs)
    return wrapper

def exp_curve(x: float, factor: float = 4.0) -> float:
    """
    Calcula uma curva exponencial suave para envelopes ADSR.

    Args:
        x (float): Valor de entrada (0 a 1).
        factor (float): Fator de suavização da curva.

    Returns:
        float: Valor suavizado.
    """
    return 1 - np.exp(-factor * x)


# ==================== CLASSE PRINCIPAL ====================================================================================================
class MidiSynth:
    """
    Classe principal do sintetizador MIDI.

    Responsável por inicializar o áudio, processar eventos MIDI,
    gerenciar vozes, gerar áudio em tempo real e aplicar envelopes e filtros.
    """
    
    def __init__(self, config: SynthConfig = SynthConfig()):
        """
        Inicializa o sintetizador com a configuração especificada.

        Args:
            config (SynthConfig): Objeto de configuração do sintetizador.
        """
        self.config = config
        self.voices: Dict[int, VoiceState] = {}
        self._stream: Optional[sd.OutputStream] = None
        self._midi_in: Optional[mido.ports.BaseInput] = None
        self.voices_lock = Lock()  # Protege o acesso ao dicionário de vozes
        self.lfo_value: float = 0.0
        
        self._init_audio_stream()
        self._init_midi()

    # ==================== INICIALIZAÇÃO ====================================================================================================
    def _init_audio_stream(self) -> None:
        """
        Inicializa o stream de áudio, configurando dispositivos e parâmetros.

        Raises:
            Exception: Em caso de falha na configuração do áudio.
        """
        devices = sd.query_devices()
        if not devices:
            raise RuntimeError("⛔ Nenhum dispositivo de áudio disponível!")

        print("Dispositivos disponíveis:")

        for i, d in enumerate(devices):
            print(f"  [{i}] {d['name']} ({d['max_output_channels']} canais)")
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
        """
        Inicializa a interface MIDI se especificado na configuração.
        """
        if self.config.midi_port:
            try:
                self._midi_in = mido.open_input(self.config.midi_port)
                self._midi_in.callback = self._midi_callback
            except Exception as e:
                print(f"Erro MIDI: {e}")

    # ==================== PROCESSAMENTO MIDI ====================================================================================================
    def _midi_callback(self, message: mido.Message) -> None:
        """
        Callback para processamento de mensagens MIDI recebidas.

        Args:
            message (mido.Message): Mensagem MIDI recebida.
        """
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
        """
        Processa o início de uma nota musical, criando uma nova voz.

        Args:
            note (int): Número da nota MIDI (0-127).
            velocity (float): Velocidade da nota (0.0-1.0).

        Raises:
            ValueError: Se a nota for inválida.
        """
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
                    phase=0.0,
                    active=True,
                    release_start_time=None
                )
                
                print(f"🎹 NOTE ON | Nota: {note} | Freq: {freq:.1f} Hz")

        except Exception as e:
            print(f"⛔ ERRO NO NOTE ON: {str(e)}")
            raise

    def _note_off(self, note: int) -> None:
        """
        Processa o término de uma nota musical, iniciando o release.

        Args:
            note (int): Número da nota MIDI.
        """
        with self.voices_lock:
            if note in self.voices:
                self.voices[note].active = False

    # ==================== GERAÇÃO DE ÁUDIO ====================================================================================================
    def _audio_callback(self, outdata: np.ndarray, frames: int, time, status) -> None:
        """
        Callback de áudio chamado pelo stream para gerar o áudio em tempo real.

        Args:
            outdata (np.ndarray): Buffer de saída de áudio.
            frames (int): Número de frames a serem processados.
            time: Objeto de tempo do stream.
            status: Status do stream.
        """
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
            if np.max(np.abs(output)) > 1.0:
                output /= np.max(np.abs(output))  # Normaliza o áudio para evitar clipping
            np.clip(output, -1, 1, out=outdata)
            
            # Debug de saída
            peak = np.max(np.abs(output))
            print(f"🔈 Pico de saída: {peak:.2f} | Vozes: {len(self.voices)}", end='\r')

        except Exception as e:
            print(f"⛔ ERRO NO CALLBACK: {str(e)}")
            outdata.fill(0)  # Evita ruídos no áudio

    def _generate_voice_wave(self, voice: VoiceState, t: np.ndarray) -> np.ndarray:
        """
        Gera a forma de onda para uma voz específica, aplicando modulações e filtros.

        Args:
            voice (VoiceState): Estado da voz.
            t (np.ndarray): Array de tempo.

        Returns:
            np.ndarray: Onda gerada para a voz.
        """
            # Calcula a frequência com LFO e HFO (como já tínhamos configurado)
        t_diff = (t[:, 0] - t[0, 0])
        base_freq = voice.frequency

        # LFO
        if self.config.lfo_depth > 0.0:
            lfo_wave = np.sin(2 * np.pi * self.config.lfo_freq * t[:, 0])
            if self.config.lfo_target == "pitch":
                base_freq *= (1 + self.config.lfo_depth * lfo_wave)

        # HFO
        if self.config.hfo_depth > 0.0:
            hfo_wave = np.sin(2 * np.pi * self.config.hfo_freq * t[:, 0])
            if self.config.hfo_target == "pitch":
                base_freq *= (1 + self.config.hfo_depth * hfo_wave)

        # Fase
        phase_increment = 2 * np.pi * base_freq * t_diff
        voice.phase += phase_increment[-1]
        voice.phase %= 2 * np.pi
        carrier_phase = voice.phase - phase_increment[::-1]
        phase = carrier_phase  # ✅ Isto resolve o erro: sempre define phase

                
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

                if self.config.additive_harmonics > 1:
                    harmonics = self.config.additive_harmonics
                    amps = [1/(i+1) for i in range(harmonics)]
                    waves = [amps[i] * np.sin((i+1)*phase) for i in range(harmonics)]
                    wave = np.sum(waves, axis=0)
                
                    return wave.astype(np.float32)
                
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
                
            case _:
                raise ValueError(f"Tipo de onda não suportado: {self.config.default_waveform}")
            # Aplicação de filtro se necessário
            
        wave = self._apply_filter(wave)
        return wave.astype(np.float32)

    # ==================== ENVELOPE ADSR ========================================================================================================================
    # AudioSynth.py - Método _calculate_adsr (Versão Corrigida)
    def _calculate_adsr(self, voice: VoiceState) -> float:
        """
        Calcula o valor do envelope ADSR para uma voz.

        Args:
            voice (VoiceState): Estado da voz.

        Returns:
            float: Valor do envelope (0.0 a 1.0).
        """
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
                adsr = exp_curve(adsr, factor=4.0)


            # Garantia de valores válidos
            adsr = np.clip(adsr, 0.0, 1.0).item()
            if np.isnan(adsr) or np.isinf(adsr):
                adsr = 0.0  # Garante que o valor seja válido

            # Debug seletivo
            if adsr > 0.01:
                print(
                    f"📈 Envelope: {adsr:.2f} | " +
                    f"Estado: {'Ativo' if voice.active else 'Release'} | " +
                    f"Freq: {voice.frequency:.1f} Hz"
                )
            # Se envelope estiver abaixo do limiar prático, corte a nota
            if adsr < 0.001:
                voice.active = False  # Garante que será removida na próxima rodada
                adsr = 0.0

            adsr = float(np.clip(adsr, 0.0, 1.0))
            if np.isnan(adsr) or np.isinf(adsr):
                adsr = 0.0
            
            # Segurança contra valores inválidos ou baixos demais
            if np.isnan(adsr) or np.isinf(adsr):
                adsr = 0.0

            if adsr < 0.001:
                voice.active = False
                adsr = 0.0

            return adsr
        

        except Exception as e:
            print(f"⛔ ERRO NO ADSR: {str(e)}")
            return 0.0

    
    def _apply_filter(self, wave: np.ndarray) -> np.ndarray:
        """
        Aplica o filtro configurado ao sinal de áudio.

        Args:
            wave (np.ndarray): Sinal de entrada.

        Returns:
            np.ndarray: Sinal filtrado.
        """
        try:
            nyquist = 0.5 * self.config.sample_rate
            norm_freq = self.config.filter_freq / nyquist
            norm_freq = np.clip(norm_freq, 0.0, 1.0)  # Etapa 1.2

            if self.config.filter_type == "lowpass":
                b, a = butter(N=2, Wn=norm_freq, btype='low')
            elif self.config.filter_type == "highpass":
                b, a = butter(N=2, Wn=norm_freq, btype='high')
            elif self.config.filter_type == "bandpass":
                bandwidth = self.config.filter_freq / self.config.filter_q
                low = (self.config.filter_freq - bandwidth/2) / nyquist
                high = (self.config.filter_freq + bandwidth/2) / nyquist
                low, high = np.clip([low, high], 0.0, 1.0)
                b, a = butter(N=2, Wn=[low, high], btype='band')
            else:
                return wave

            return lfilter(b, a, wave)

        except Exception as e:
            print(f"Erro no filtro: {e}")
            return wave


# ==================== UTILITÁRIOS ====================================================================================================
    @staticmethod
    def _note_to_freq(note: int) -> float:
        """
        Converte um número de nota MIDI para frequência em Hz.

        Args:
            note (int): Número da nota MIDI (0-127).

        Returns:
            float: Frequência correspondente em Hz.

        Raises:
            ValueError: Se a nota for inválida.
        """
        if not isinstance(note, int) or not (0 <= note <= 127):
            raise ValueError(f"Nota inválida: {note}")
        return 440.0 * (2.0 ** ((note - 69) / 12.0))

    def _remove_oldest_voice(self) -> None:
        """
        Remove a voz mais antiga quando o limite de polifonia é atingido.
        """
        with self.voices_lock:
            oldest_note = min(self.voices.keys(), key=lambda k: (self.voices[k].age, -self.voices[k].velocity))
            del self.voices[oldest_note]

    # ==================== CONTROLE DE FLUXO ====================================================================================================
    def start(self) -> None:
        """
        Inicia a reprodução de áudio e o processamento MIDI.
        """
        self._stream = sd.OutputStream(
        callback=self._audio_callback,
        samplerate=self.config.sample_rate,
        blocksize=self.config.buffer_size,
        channels=2
        )
        try:
            self._stream.start()
            print("✅ Áudio iniciado com sucesso.")
        except Exception as e:
            print(f"⛔ ERRO ao iniciar áudio: {e}")

    def stop(self) -> None:
        """
        Para a reprodução de áudio e libera recursos do sintetizador.
        """
        if self._stream and self._stream.active:
            self._stream.close()
            self._stream = None
        if self._midi_in:
            self._midi_in.close()
            self._midi_in = None

    def __enter__(self):
        """
        Suporte para gerenciamento de contexto (with statement).

        Returns:
            MidiSynth: Instância do sintetizador.
        """
        self.start()
        return self

    def __exit__(self, *args):
        """
        Garante liberação de recursos ao sair do contexto.
        """
        self.stop()

# ==================== EXEMPLO DE USO ========================================================================================================================
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