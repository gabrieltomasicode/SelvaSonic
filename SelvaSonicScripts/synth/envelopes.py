import numpy as np
from .config import ADSRCurve
from .voices import VoiceState
from .utils import exp_curve, clamp

def calculate_adsr(voice: VoiceState, config) -> float:
    """
    Calcula o valor do envelope ADSR (Attack, Decay, Sustain, Release) para uma voz sintetizada.

    Esta função determina o valor atual do envelope ADSR de uma voz, com base em seu tempo de vida (age),
    estado de liberação (release) e parâmetros de configuração. O envelope é utilizado para modelar a evolução
    da amplitude do som ao longo do tempo, proporcionando maior realismo e controle dinâmico.

    Parâmetros:
        voice (VoiceState): Instância representando o estado atual da voz, incluindo idade, envelope e status de liberação.
        config: Objeto de configuração contendo os parâmetros do envelope ADSR (attack_time, decay_time, sustain_level, release_time, adsr_curve).

    Retorna:
        float: Valor do envelope ADSR no instante atual, variando entre 0.0 e 1.0.

    Notas:
        - O envelope é atualizado automaticamente no objeto da voz.
        - Suporta curvas lineares e exponenciais, conforme definido em config.adsr_curve.
        - Se ocorrer erro durante o cálculo, retorna 0.0 e imprime mensagem de erro.
        - Quando o envelope atinge valor inferior a 0.001, a voz é marcada como inativa.

    Exceções:
        Nenhuma exceção é propagada. Todas as exceções são capturadas e tratadas internamente.
    """
    try:
        total_time = voice.age

        if voice.release_start_time is None:
            # Fases Attack, Decay, Sustain
            if total_time < config.attack_time:
                adsr = total_time / max(config.attack_time, 1e-6)
            elif total_time < (config.attack_time + config.decay_time):
                decay_progress = (total_time - config.attack_time) / max(config.decay_time, 1e-6)
                adsr = 1 - (1 - config.sustain_level) * decay_progress
            else:
                adsr = config.sustain_level
            # Atualiza o envelope para o valor atual
            voice.envelope = adsr
        else:
            # Release
            release_elapsed = total_time - voice.release_start_time
            # O envelope inicial do release deve ser o valor do envelope no momento do note_off
            envelope_at_release = getattr(voice, "envelope_at_release", None)
            if envelope_at_release is None:
                envelope_at_release = voice.envelope
                voice.envelope_at_release = envelope_at_release
            release_progress = min(release_elapsed / max(config.release_time, 1e-6), 1.0)
            adsr = max(0.0, envelope_at_release * (1 - release_progress))

        # Aplicação da curva
        if config.adsr_curve == ADSRCurve.EXPONENTIAL:
            adsr = exp_curve(adsr, factor=4.0)

        # Garantia de valores válidos
        adsr = clamp(adsr, 0.0, 1.0)
        if np.isnan(adsr) or np.isinf(adsr):
            adsr = 0.0

        # Se envelope estiver abaixo do limiar prático, corte a nota
        if adsr < 0.001:
            voice.active = False
            adsr = 0.0

        return float(adsr)

    except Exception as e:
        print(f"⛔ ERRO NO ADSR: {str(e)}")
        return 0.0

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