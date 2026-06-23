import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi
from functools import lru_cache

@lru_cache(maxsize=16)
def get_filter_coeffs(filter_type: str, filter_freq: float, filter_q: float, sample_rate: int):
    """
    Calcula e armazena em cache os coeficientes (b, a) do filtro digital Butterworth.

    Esta função utiliza o decorador `lru_cache` para evitar o recálculo custoso dos
    coeficientes matemáticos a cada frame de áudio. Os coeficientes só são processados
    novamente quando os parâmetros do filtro (tipo, frequência, Q ou sample rate) 
    são alterados.

    Parâmetros:
        filter_type (str): Tipo do filtro ('lowpass', 'highpass' ou 'bandpass').
        filter_freq (float): Frequência de corte central do filtro em Hz.
        filter_q (float): Fator de qualidade (Q) ou largura de banda do filtro.
        sample_rate (int): Taxa de amostragem do sistema em Hz (ex: 44100).

    Retorna:
        tuple: Uma tupla (b, a) contendo os arrays de coeficientes do filtro.
               Retorna (None, None) se os parâmetros resultarem em um filtro inválido.

    Notas:
        - As frequências são automaticamente limitadas (clipping) para respeitar o
          teorema de Nyquist (metade da taxa de amostragem).
    """
    nyquist = 0.5 * sample_rate
    min_freq = 1.0
    max_freq = nyquist - 1.0
    freq = np.clip(filter_freq, min_freq, max_freq)
    norm_freq = freq / nyquist

    if filter_type == "lowpass" and 0 < norm_freq < 1:
        return butter(N=2, Wn=norm_freq, btype='low')
    elif filter_type == "highpass" and 0 < norm_freq < 1:
        return butter(N=2, Wn=norm_freq, btype='high')
    elif filter_type == "bandpass":
        bandwidth = freq / max(filter_q, 1e-6)
        low = max((freq - bandwidth/2) / nyquist, 1e-6)
        high = min((freq + bandwidth/2) / nyquist, 1 - 1e-6)
        if low < high:
            return butter(N=2, Wn=[low, high], btype='band')
            
    return None, None

def apply_filter(wave: np.ndarray, config, voice) -> np.ndarray:
    """
    Aplica o filtro configurado ao sinal de áudio, mantendo o estado contínuo da onda.

    Esta função aplica um filtro digital IIR (lowpass, highpass ou bandpass) ao
    sinal de entrada. Ela recupera os coeficientes cacheados e gerencia o estado
    da memória do filtro (zi e zf) dentro do objeto da voz. Isso garante que a onda
    seja processada de forma contínua entre os blocos (buffers) de áudio, eliminando
    estalos (clicks) de descontinuidade no som.

    Parâmetros:
        wave (np.ndarray): Array contendo o sinal de áudio do frame atual.
        config: Objeto SynthConfig contendo os parâmetros atuais do filtro.
        voice: Objeto VoiceState representando a voz atual. Usado para armazenar
               e recuperar o estado dinâmico da memória do filtro (`filter_state`).

    Retorna:
        np.ndarray: Sinal de áudio processado/filtrado.

    Notas:
        - Utiliza `scipy.signal.lfilter` passando o estado inicial `zi`.
        - Se o filtro for recém-criado, inicializa o estado perfeitamente através 
          da função `lfilter_zi`, multiplicando pelo primeiro sample da onda.
        - Salva o estado final `zf` na voz para o próximo ciclo do callback.

    Exceções:
        Nenhuma exceção é propagada. Erros são capturados, impressos no console,
        e o sinal original é retornado sem alterações (bypass).
    """
    try:
        b, a = get_filter_coeffs(
            config.filter_type, 
            config.filter_freq, 
            config.filter_q, 
            config.sample_rate
        )

        if b is None or a is None:
            return wave

        # --- A CORREÇÃO CRÍTICA ---
        # Garantimos que a onda seja 1D e livre de dimensões extras (ex: [512, 1] vira [512])
        # .squeeze() remove todas as dimensões de tamanho 1.
        wave_flat = np.squeeze(wave)
        
        # Se após o squeeze o array ainda não for 1D (ex: matriz vazia ou mal formada),
        # garantimos que ele seja um array flat.
        if wave_flat.ndim != 1:
            wave_flat = wave_flat.flatten()
        # --------------------------

        zi = getattr(voice, 'filter_state', None)
        if zi is None:
            zi = lfilter_zi(b, a) * wave_flat[0]

        filtered_1d, zf = lfilter(b, a, wave_flat, zi=zi)
        voice.filter_state = zf

        # Retornamos no formato original de entrada [frames, 1] ou [frames]
        if wave.ndim == 2:
            return filtered_1d.reshape(-1, 1)
        return filtered_1d
        
    except Exception:
        # Bypass silencioso para evitar travar a thread de áudio
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