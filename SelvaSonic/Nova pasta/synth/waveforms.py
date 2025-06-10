import numpy as np
from .config import SynthConfig
from .voices import VoiceState
from .filters import apply_filter, apply_modulations
from scipy.signal import lfilter
from .config import WaveType


def generate_wave( voice: VoiceState, t: np.ndarray, config: SynthConfig, amplitude=1.0) -> np.ndarray:
    """
    Gera a forma de onda para uma voz específica, aplicando modulações e filtros.

    Args:
        voice (VoiceState): Estado da voz.
        t (np.ndarray): Array de tempo.

    Returns:
        np.ndarray: Onda gerada para a voz.
    """
        # Aplica modulações e obtém fase e pulse_width
    phase, pulse_width = apply_modulations(voice, t, config)

    # Gerar onda base com a fase modulada
    match config.default_waveform:
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
            n_voices = int(config.super_saw_voices)
            if n_voices < 1:
                n_voices = 1
            detuned_freqs = [
                voice.frequency * (1 + detune * ((i/n_voices) - 0.5)) 
                for i in range(n_voices)
            ]
            saws = []
            for freq in detuned_freqs:
                phase_inc = 2 * np.pi * freq * (t - t[0])
                individual_phase = voice.phase + phase_inc
                saw = (individual_phase % (2*np.pi)) / np.pi - 1
                saws.append(saw)
            wave = np.mean(saws, axis=0)
            if config.additive_harmonics > 1:
                harmonics = config.additive_harmonics
                amps = [1/(i+1) for i in range(harmonics)]
                waves = [amps[i] * np.sin((i+1)*phase) for i in range(harmonics)]
                wave = np.sum(waves, axis=0)
                return wave.astype(np.float32)
            voice.phase += 2 * np.pi * voice.frequency * (t - t[0])
            voice.phase %= 2 * np.pi
        case WaveType.WAVETABLE:
            if config.wavetable is not None:
                wt_size = len(config.wavetable)
                position = (phase % (2*np.pi)) / (2*np.pi) * wt_size
                wave = np.interp(position, np.arange(wt_size), config.wavetable)
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
            wave -= np.mean(wave)
            wave = np.clip(wave, -1, 1)
        case _:
            raise ValueError(f"Tipo de onda não suportado: {config.default_waveform}")

    wave = apply_filter(wave, config)
    return wave.astype(np.float32)