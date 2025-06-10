import numpy as np
from scipy.signal import butter, lfilter



def apply_filter(wave: np.ndarray, config) -> np.ndarray:
    """
    Aplica o filtro configurado ao sinal de áudio.

    Args:
        wave (np.ndarray): Sinal de entrada.
        config: Objeto de configuração com atributos de filtro.

    Returns:
        np.ndarray: Sinal filtrado.
    """
    try:
        nyquist = 0.5 * config.sample_rate
        norm_freq = config.filter_freq / nyquist
        norm_freq = np.clip(norm_freq, 0.0, 1.0)

        if config.filter_type == "lowpass":
            b, a = butter(N=2, Wn=norm_freq, btype='low')
        elif config.filter_type == "highpass":
            b, a = butter(N=2, Wn=norm_freq, btype='high')
        elif config.filter_type == "bandpass":
            bandwidth = config.filter_freq / config.filter_q
            low = (config.filter_freq - bandwidth/2) / nyquist
            high = (config.filter_freq + bandwidth/2) / nyquist
            low, high = np.clip([low, high], 0.0, 1.0)
            b, a = butter(N=2, Wn=[low, high], btype='band')
        else:
            return wave

        return lfilter(b, a, wave)
    except Exception as e:
        print(f"Erro no filtro: {e}")
        return wave
    
def apply_modulations(voice, t, config):
    """
    Aplica LFO, HFO e FM à frequência e retorna a fase e pulse_width.
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