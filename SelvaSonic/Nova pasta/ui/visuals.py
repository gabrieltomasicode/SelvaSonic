import matplotlib.pyplot as plt
import numpy as np
import numpy as np
from scipy.signal import lfilter
import matplotlib.pyplot as plt
from synth.config import SynthConfig, WaveType


def generate_static_wave(phase, config):
    """
    Gera uma forma de onda estática com base na fase e na configuração.
    """
    try:
        match config.default_waveform:
            case WaveType.SINE:
                return np.sin(phase)
            case WaveType.SQUARE:
                return np.sign(np.sin(phase))
            case WaveType.TRIANGLE:
                return (2 * np.arcsin(np.sin(phase)) / np.pi)
            case WaveType.SAWTOOTH:
                return ((phase % (2*np.pi)) / np.pi - 1)
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
                voices = [
                    ((phase * (1 + detune * i)) % (2*np.pi) / np.pi - 1)
                    for i in np.linspace(-0.5, 0.5, 7)
                ]
                return np.mean(voices, axis=0)
            case WaveType.WAVETABLE:
                if config.wavetable is not None:
                    wt_size = len(config.wavetable)
                    position = (phase % (2*np.pi)) / (2*np.pi) * wt_size
                    return np.interp(position, np.arange(wt_size), config.wavetable)
                return np.zeros_like(phase)
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

    Args:
        ax: O objeto Axes do matplotlib.
        t: Array de tempo.
        wave: Array da forma de onda.
        title: Título do gráfico.
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

    Args:
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