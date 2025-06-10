import numpy as np

def note_to_freq(note: int) -> float:
    """
    Converte número MIDI de nota para frequência em Hz.

    Esta função converte um número de nota MIDI (0-127) para sua frequência correspondente em Hertz,
    utilizando a afinação padrão (A4 = 440 Hz).

    Parâmetros:
        note (int): Número da nota MIDI.

    Retorna:
        float: Frequência em Hz correspondente à nota.
    """
    return 440.0 * (2.0 ** ((note - 69) / 12.0))

def exp_curve(x: float, factor: float = 4.0) -> float:
    """
    Calcula uma curva exponencial suave para envelopes ADSR.

    Esta função aplica uma curva exponencial ao valor de entrada, útil para suavizar envelopes de amplitude.

    Parâmetros:
        x (float): Valor de entrada (0 a 1).
        factor (float): Fator de suavização da curva.

    Retorna:
        float: Valor suavizado pela curva exponencial.
    """
    return 1 - np.exp(-factor * x)

def clamp(value, min_value, max_value):
    """
    Restringe um valor ao intervalo definido por min_value e max_value.

    Parâmetros:
        value: Valor a ser limitado.
        min_value: Valor mínimo permitido.
        max_value: Valor máximo permitido.

    Retorna:
        Valor limitado ao intervalo especificado.
    """
    return max(min_value, min(value, max_value))

def validate_adsr(param, value):
        """
        Garante que os valores de ADSR nunca sejam zero ou negativos.

        Esta função ajusta os valores dos parâmetros de envelope ADSR para garantir que estejam dentro de limites seguros.

        Parâmetros:
            param: Nome do parâmetro ('Attack', 'Decay', 'Sustain', 'Release').
            value: Valor a ser validado.

        Retorna:
            float: Valor ajustado para o parâmetro.
        """
        if param in ['Attack', 'Decay', 'Release']:
            return max(0.001, float(value))
        elif param == 'Sustain':
            return max(0.01, float(value))
        return float(value)

import time

def get_time():
    """
    Retorna o tempo atual em segundos.

    Utilizado para sincronização de eventos de áudio e MIDI.

    Retorna:
        float: Tempo atual em segundos desde a época.
    """
    return time.time()