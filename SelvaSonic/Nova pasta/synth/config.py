from enum import Enum
from dataclasses import dataclass
import numpy as np
from typing import Optional


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