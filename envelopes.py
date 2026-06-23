import numpy as np
from .config import ADSRCurve
from .voices import VoiceState
from .utils import exp_curve, clamp

def calculate_adsr(voice: VoiceState, config, frames: int) -> np.ndarray:
    """
    Calcula o envelope ADSR vetorizado para um bloco inteiro de áudio.

    Em vez de retornar um único valor, esta função gera um array de envelope
    amostra por amostra para o tamanho do frame atual. Isso elimina o "zipper noise"
    (ruído de degrau) ao suavizar as transições de volume durante o buffer.

    Parâmetros:
        voice (VoiceState): Estado atual da voz.
        config: Objeto de configuração do sintetizador.
        frames (int): Número de amostras no bloco de áudio atual.

    Retorna:
        np.ndarray: Array de formato [frames, 1] contendo os valores do envelope.
    """
    try:
        # Cria um array com a "idade" exata da voz em cada sample do buffer
        ages = voice.age + np.arange(frames) / config.sample_rate
        adsr = np.zeros(frames, dtype=np.float32)

        if voice.release_start_time is None:
            attack_time = max(config.attack_time, 1e-6)
            decay_time = max(config.decay_time, 1e-6)

            # Fase Attack
            attack_mask = ages < attack_time
            adsr[attack_mask] = ages[attack_mask] / attack_time

            # Fase Decay
            decay_mask = (ages >= attack_time) & (ages < attack_time + decay_time)
            decay_progress = (ages[decay_mask] - attack_time) / decay_time
            adsr[decay_mask] = 1.0 - (1.0 - config.sustain_level) * decay_progress

            # Fase Sustain
            sustain_mask = ages >= attack_time + decay_time
            adsr[sustain_mask] = config.sustain_level

            # Salva o último valor do envelope para usar num futuro Release
            voice.envelope = float(adsr[-1])
        else:
            # Fase Release
            envelope_at_release = getattr(voice, "envelope_at_release", None)
            if envelope_at_release is None:
                envelope_at_release = voice.envelope
                voice.envelope_at_release = envelope_at_release

            release_time = max(config.release_time, 1e-6)
            release_elapsed = ages - voice.release_start_time
            release_progress = np.clip(release_elapsed / release_time, 0.0, 1.0)
            adsr = envelope_at_release * (1.0 - release_progress)

            voice.envelope = float(adsr[-1])

        # Aplicação da curva
        if config.adsr_curve == ADSRCurve.EXPONENTIAL:
            adsr = exp_curve(adsr, factor=4.0)

        # Garantia de limites
        adsr = np.clip(adsr, 0.0, 1.0)

        # Atualiza a idade da voz para o INÍCIO do próximo bloco de áudio
        voice.age += frames / config.sample_rate

        # Se no final do bloco a nota morreu, desativa a voz
        if adsr[-1] < 0.001 and voice.release_start_time is not None:
            voice.active = False

        # Retorna formatado como coluna para facilitar o broadcast na mixagem
        return adsr[:, None]

    except Exception as e:
        print(f"⛔ ERRO NO ADSR: {str(e)}")
        return np.zeros((frames, 1), dtype=np.float32)

def update_envelope(voice, attack: float = 0.01, decay: float = 0.1,
                    sustain: float = 0.7, release: float = 0.3) -> None:
    """
    Atualiza o envelope ADSR (Attack, Decay, Sustain, Release) de uma voz sintetizada.

    Esta função recalcula e atualiza o valor do envelope ADSR da voz com base em sua idade, estado de liberação
    e parâmetros fornecidos. O envelope controla a evolução da amplitude do som ao longo do tempo, permitindo
    simular o comportamento dinâmico típico de instrumentos musicais.

    Parâmetros:
        voice: Instância da voz a ser atualizada, contendo atributos como idade, envelope, ativo e release_start_time.
        attack (float): Tempo de ataque em segundos (valor padrão: 0.01).
        decay (float): Tempo de decaimento em segundos (valor padrão: 0.1).
        sustain (float): Nível de sustentação (0.0 a 1.0, valor padrão: 0.7).
        release (float): Tempo de liberação em segundos (valor padrão: 0.3).

    Notas:
        - Se a voz não estiver ativa, o envelope é zerado imediatamente.
        - Durante a fase de release, o envelope decresce até atingir zero e a voz é desativada.
        - Os valores de envelope são sempre limitados ao intervalo [0.0, 1.0].
        - Parâmetros negativos são ajustados para valores mínimos seguros.

    Exceções:
        Nenhuma exceção é propagada. Todos os casos são tratados internamente.
    """
    if attack <= 0: attack = 0.001
    if decay <= 0: decay = 0.001
    if release <= 0: release = 0.001
    if not voice.active:
        voice.envelope = 0.0
        return

    if voice.release_start_time is not None:
        release_time = voice.age - voice.release_start_time
        if release_time >= release:
            voice.active = False
            voice.envelope = 0.0
        else:
            voice.envelope = (1.0 - release_time / release) * sustain
        return

    if voice.age < attack:
        voice.envelope = voice.age / attack
    elif voice.age < attack + decay:
        decay_progress = (voice.age - attack) / decay
        voice.envelope = 1.0 - (1.0 - sustain) * decay_progress
    else:
        voice.envelope = sustain

    # garantindo valores entre 0 e 1
    voice.envelope = clamp(voice.envelope, 0.0, 1.0)