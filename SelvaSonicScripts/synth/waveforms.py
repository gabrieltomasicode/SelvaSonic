import numpy as np
from .config import SynthConfig
from .voices import VoiceState
from .filters import apply_filter, apply_modulations
from scipy.signal import lfilter
from .config import WaveType


def generate_wave( voice: VoiceState, t: np.ndarray, config: SynthConfig, amplitude=1.0) -> np.ndarray:
    """
    Gera a forma de onda para uma voz específica, aplicando modulações e filtros.

    Esta função sintetiza a forma de onda correspondente ao tipo selecionado no parâmetro de configuração,
    aplicando modulações (LFO, HFO, FM) e filtros digitais conforme necessário.

    Parâmetros:
        voice (VoiceState): Estado atual da voz a ser sintetizada.
        t (np.ndarray): Array de tempo para geração da onda.
        config (SynthConfig): Objeto de configuração do sintetizador, incluindo tipo de onda, filtros e modulações.
        amplitude (float, opcional): Amplitude máxima da onda (padrão: 1.0).

    Retorna:
        np.ndarray: Array de amostras da onda gerada para a voz, já filtrada e normalizada.

    Notas:
        - Suporta múltiplos tipos de onda: seno, quadrada, triangular, dente de serra, ruído, pulse, super saw, wavetable, pink noise e brown noise.
        - Para SuperSaw, gera múltiplas vozes levemente desafinadas e soma os resultados.
        - Para modos aditivos, soma harmônicos adicionais conforme configuração.
        - O resultado final é sempre convertido para float32.
        - Em caso de tipo de onda não suportado, lança ValueError.
    """
        # Aplica modulações e obtém fase e pulse_width
    phase, pulse_width = apply_modulations(voice, t, config)

    # 1. Recupera o número da nota MIDI a partir da frequência base da voz
    # Usamos max() para evitar divisão por zero ou log de zero.
    freq = max(voice.frequency, 1e-6)
    note_idx = int(round(69 + 12 * np.log2(freq / 440.0)))
    note_idx = np.clip(note_idx, 0, 127) # Garante que o índice exista no nosso dicionário

    # Gerar onda base com a fase modulada
    match config.default_waveform:
        case WaveType.SINE:
            wave = np.sin(phase)
        case WaveType.SQUARE:
            # 2. Busca a tabela perfeita para esta nota
            table = config.bandlimited_tables['square'][note_idx]
            table_size = len(table)
            
            # 3. Mapeia a fase (que vai de 0 a 2pi) para o tamanho da tabela (ex: 0 a 2048)
            position = (phase % (2 * np.pi)) / (2 * np.pi) * table_size
            
            # 4. Interpola os valores rapidamente
            wave = np.interp(position, np.arange(table_size), table)
        case WaveType.TRIANGLE:
            wave = (2 * np.arcsin(np.sin(phase)) / np.pi)
        case WaveType.SAWTOOTH:
            # Mesma lógica aplicada à Dente de Serra
            table = config.bandlimited_tables['sawtooth'][note_idx]
            table_size = len(table)
            
            position = (phase % (2 * np.pi)) / (2 * np.pi) * table_size
            wave = np.interp(position, np.arange(table_size), table)
        case WaveType.NOISE:
            wave = np.random.uniform(-1, 1, phase.shape)
        case WaveType.PULSE:
            wave = np.where(
                (phase % (2*np.pi)) < (2*np.pi * pulse_width), 
                1.0, -1.0
            )
        case WaveType.SUPER_SAW:
            detune = 0.2
            n_voices = max(1, int(config.super_saw_voices))

            # 1. Cria um array de spreads centrados, ex: [-0.5, 0, 0.5]
            spread = (np.arange(n_voices) / n_voices) - 0.5
            detuned_freqs = voice.frequency * (1 + detune * spread)
            phases_init = np.linspace(0, 2 * np.pi, n_voices, endpoint=False)

            # 2. Broadcasting: t tem shape (frames, 1), detuned_freqs tem shape (n_voices,)
            # O Numpy magicamente cria uma matriz bidimensional (frames, n_voices)
            t_diff = t - t[0]
            phase_inc = 2 * np.pi * detuned_freqs * t_diff

            # Fase individual completa para cada voz e cada sample
            individual_phases = voice.phase + phase_inc + phases_init

            # Geração das formas de onda dente de serra vetorizadas
            saws = (individual_phases % (2 * np.pi)) / np.pi - 1.0

            # 3. Soma as vozes na dimensão correta (axis=1) e mantém o shape (frames, 1)
            wave = np.sum(saws, axis=1, keepdims=True)

            # Normalização suave
            wave /= (np.max(np.abs(wave)) + 1e-8)

            # 4. Tratamento de harmônicos aditivos (também 100% vetorizado)
            if config.additive_harmonics > 1:
                harmonics = config.additive_harmonics
                h_indices = np.arange(1, harmonics + 1) # shape: (harmonics,)
                amps = 1 / h_indices
                
                # phase tem shape (frames, 1). Multiplicar gera matriz (frames, harmonics)
                h_phases = phase * h_indices
                waves = amps * np.sin(h_phases)
                
                # Soma os harmônicos e mantém o formato correto do buffer
                wave = np.sum(waves, axis=1, keepdims=True)

            # 5. Atualiza a fase base da voz para o próximo callback conectar perfeitamente
            step = 1.0 / config.sample_rate
            voice.phase += 2 * np.pi * voice.frequency * (t_diff[-1, 0] + step)
            voice.phase %= 2 * np.pi
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

    wave = apply_filter(wave, config, voice)
    return wave.astype(np.float32)