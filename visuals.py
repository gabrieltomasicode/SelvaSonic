import matplotlib.pyplot as plt
import numpy as np
import numpy as np
from scipy.signal import lfilter
import matplotlib.pyplot as plt
from synth.config import SynthConfig, WaveType


def generate_static_wave(phase, config):
    """
    Gera uma forma de onda estática com base na fase e na configuração.

    Esta função gera uma forma de onda estática para visualização, de acordo com o tipo de onda definido na configuração.

    Parâmetros:
        phase (np.ndarray): Array de fases para a geração da onda.
        config: Objeto de configuração contendo o tipo de onda e parâmetros relevantes.

    Retorna:
        np.ndarray: Array da forma de onda gerada.

    Notas:
        - Suporta múltiplos tipos de onda: seno, quadrada, triangular, dente de serra, ruído, pulse, super saw, pink noise e brown noise.
        - Para SuperSaw, gera múltiplas vozes levemente desafinadas e soma os resultados.
        - Em caso de erro, retorna um array de zeros.
    """
    try:
        # Definimos a nota 69 (A4) como padrão para o desenho estático
        note_idx = 69
        match config.default_waveform:
            case WaveType.SINE:
                return np.sin(phase)
            case WaveType.SQUARE:
                # Busca a onda quadrada pré-calculada e sem aliasing do nosso cache
                table = config.bandlimited_tables['square'].get(note_idx)
                if table is not None:
                    table_size = len(table)
                    position = (phase % (2 * np.pi)) / (2 * np.pi) * table_size
                    return np.interp(position, np.arange(table_size), table)
                else:
                    return np.sign(np.sin(phase)) # Fallback seguro
            case WaveType.TRIANGLE:
                return (2 * np.arcsin(np.sin(phase)) / np.pi)
            case WaveType.SAWTOOTH:
                # Busca a onda dente de serra pré-calculada e sem aliasing do nosso cache
                table = config.bandlimited_tables['sawtooth'].get(note_idx)
                if table is not None:
                    table_size = len(table)
                    position = (phase % (2 * np.pi)) / (2 * np.pi) * table_size
                    return np.interp(position, np.arange(table_size), table)
                else:
                    return ((phase % (2*np.pi)) / np.pi - 1) # Fallback seguro
            case WaveType.NOISE:
                return np.random.uniform(-1, 1, phase.shape)
            case WaveType.PULSE:
                pulse_width = config.pulse_width
                return np.where(
                    (phase % (2*np.pi)) < (2*np.pi * pulse_width), 
                    1.0, -1.0
                )
            case WaveType.SUPER_SAW:
                detune = 0.2
                n_voices = int(config.super_saw_voices)
                if n_voices < 1:
                    n_voices = 1
                base_freq = 220  # Frequência padrão para visualização
                # Calcula o tempo relativo a partir da fase
                t = phase / (2 * np.pi * base_freq)
                phases_init = np.linspace(0, 2*np.pi, n_voices, endpoint=False)
                detuned_freqs = [
                    base_freq * (1 + detune * ((i/n_voices) - 0.5))
                    for i in range(n_voices)
                ]
                saws = []
                for idx, freq in enumerate(detuned_freqs):
                    phase_inc = 2 * np.pi * freq * t
                    individual_phase = phase_inc + phases_init[idx]
                    saw = (individual_phase % (2*np.pi)) / np.pi - 1
                    saws.append(saw)
                wave = np.mean(saws, axis=0)
                return wave.astype(np.float32)
                
            case WaveType.PINK_NOISE:
                white = np.random.uniform(-1, 1, phase.shape)
                b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
                a = [1, -2.494956002, 2.017265875, -0.522189400]
                return lfilter(b, a, white)
            case WaveType.BROWN_NOISE:
                white = np.random.uniform(-1, 1, phase.shape)
                brown = np.cumsum(white) * 0.02
                return np.clip(brown - np.mean(brown), -1, 1)
            case _:
                return np.zeros_like(phase)
    except Exception as e:
        print(f"Erro na geração estática: {e}")
        return np.zeros_like(phase)

def update_waveform_plot(ax, t, wave, title="Waveform Preview"):
    """
    Atualiza o gráfico da forma de onda.

    Esta função atualiza o gráfico do matplotlib com a nova forma de onda.

    Parâmetros:
        ax: Objeto Axes do matplotlib.
        t (np.ndarray): Array de tempo.
        wave (np.ndarray): Array da forma de onda.
        title (str): Título do gráfico.
    """
    ax.clear()
    ax.plot(t, wave, color='blue')
    ax.set_title(title)
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Amplitude")
    ax.set_ylim(-1.1, 1.1)
    ax.grid(True)
    
def plot_waveform(wave, sample_rate, title="Forma de Onda"):
    """
    Plota a forma de onda de um sinal de áudio do SelvaSonic.

    Esta função exibe um gráfico da forma de onda do sinal de áudio, seja mono ou estéreo.

    Parâmetros:
        wave (np.ndarray or list): Array de áudio (mono ou estéreo).
        sample_rate (int): Taxa de amostragem do áudio.
        title (str): Título do gráfico.
    """

    if isinstance(wave, list):
        wave = np.array(wave)
    # Garante que wave seja pelo menos 1D
    wave = np.squeeze(wave)
    if wave.ndim > 1:
        # Se for estéreo, pega o canal esquerdo
        wave = wave[:, 0]
    duration = len(wave) / sample_rate
    time = np.linspace(0, duration, len(wave))
    plt.figure(figsize=(10, 3))
    plt.plot(time, wave, color='royalblue')
    plt.title(title)
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.show()