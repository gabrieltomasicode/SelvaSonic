import numpy as np

def note_to_freq(note: int) -> float:
    """Converte número MIDI de nota para frequência em Hz."""
    return 440.0 * (2.0 ** ((note - 69) / 12.0))

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

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def validate_adsr(param, value):
        """
        Garante que os valores de ADSR nunca sejam zero ou negativos.
        """
        if param in ['Attack', 'Decay', 'Release']:
            return max(0.001, float(value))
        elif param == 'Sustain':
            return max(0.01, float(value))
        return float(value)

import time

def get_time():
    """Retorna o tempo atual em segundos."""
    return time.time()