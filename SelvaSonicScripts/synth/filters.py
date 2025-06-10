import numpy as np
from scipy.signal import butter, lfilter



def apply_filter(wave: np.ndarray, config) -> np.ndarray:
    """
    Aplica o filtro configurado ao sinal de áudio.

    Esta função aplica um filtro digital (lowpass, highpass ou bandpass) ao sinal de áudio de entrada,
    utilizando os parâmetros definidos no objeto de configuração.

    Parâmetros:
        wave (np.ndarray): Sinal de áudio de entrada.
        config: Objeto de configuração contendo os parâmetros do filtro (sample_rate, filter_type, filter_freq, filter_q).

    Retorna:
        np.ndarray: Sinal de áudio filtrado.

    Notas:
        - O filtro é implementado utilizando a função butterworth da biblioteca scipy.
        - Se os parâmetros estiverem fora dos limites válidos, o sinal original é retornado sem alterações.
        - Em caso de erro durante o processamento, o sinal original é retornado e uma mensagem de erro é exibida.
    """
    try:
        nyquist = 0.5 * config.sample_rate
        # Limite mínimo e máximo para a frequência de corte
        min_freq = 1.0
        max_freq = nyquist - 1.0
        freq = np.clip(config.filter_freq, min_freq, max_freq)
        norm_freq = freq / nyquist

        if config.filter_type == "lowpass":
            if not (0 < norm_freq < 1):
                return wave
            b, a = butter(N=2, Wn=norm_freq, btype='low')
        elif config.filter_type == "highpass":
            if not (0 < norm_freq < 1):
                return wave
            b, a = butter(N=2, Wn=norm_freq, btype='high')
        elif config.filter_type == "bandpass":
            bandwidth = freq / max(config.filter_q, 1e-6)
            low = (freq - bandwidth/2) / nyquist
            high = (freq + bandwidth/2) / nyquist
            # Garante que low/high estejam dentro do intervalo válido
            low = max(low, 1e-6)
            high = min(high, 1 - 1e-6)
            if not (0 < low < high < 1):
                return wave
            b, a = butter(N=2, Wn=[low, high], btype='band')
        else:
            return wave

        return lfilter(b, a, wave)
    except Exception as e:
        print(f"Erro no filtro: {e}")
        return wave
    
def apply_modulations(voice, t, config):
    """
    Aplica modulações LFO, HFO e FM à frequência da voz e retorna a fase e pulse_width.

    Esta função modifica a frequência base da voz utilizando LFO (Low Frequency Oscillator), HFO (High Frequency Oscillator)
    e FM (Frequency Modulation), de acordo com os parâmetros de configuração. Calcula a fase resultante para síntese de áudio
    e retorna também o valor de pulse_width.

    Parâmetros:
        voice: Objeto representando o estado da voz, contendo atributos como frequência e fase.
        t (np.ndarray): Vetor de tempo para o qual as modulações serão aplicadas.
        config: Objeto de configuração contendo os parâmetros das modulações (lfo_freq, lfo_depth, hfo_freq, hfo_depth, fm_mod_index, fm_mod_freq, pulse_width).

    Retorna:
        tuple: (phase, pulse_width), onde phase é um array com a fase resultante e pulse_width é o valor configurado.

    Notas:
        - As modulações são aplicadas apenas se a profundidade correspondente for maior que zero.
        - O valor da fase é atualizado no objeto voice.
        - Suporta modulação de pitch por LFO e HFO, além de FM.
    """
    t_diff = (t - t[0])
    base_freq = voice.frequency

    # LFO
    if config.lfo_depth > 0.0:
        lfo_wave = np.sin(2 * np.pi * config.lfo_freq * t)
        if config.lfo_target == "pitch":
            base_freq *= (1 + config.lfo_depth * lfo_wave)

    # HFO
    if config.hfo_depth > 0.0:
        hfo_wave = np.sin(2 * np.pi * config.hfo_freq * t)
        if config.hfo_target == "pitch":
            base_freq *= (1 + config.hfo_depth * hfo_wave)

    # Fase
    phase_increment = 2 * np.pi * base_freq * t_diff
    voice.phase += phase_increment[-1]
    voice.phase %= 2 * np.pi
    carrier_phase = voice.phase - phase_increment[::-1]
    phase = carrier_phase

    # FM
    if config.fm_mod_index > 0:
        modulator = config.fm_mod_index * np.sin(2 * np.pi * config.fm_mod_freq * t)
        phase = carrier_phase + modulator

    pulse_width = config.pulse_width
    return phase, pulse_width