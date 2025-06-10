import numpy as np
from .config import ADSRCurve
from .voices import VoiceState
from .utils import exp_curve, clamp

def calculate_adsr(voice: VoiceState, config) -> float:
    """
    Calcula o valor do envelope ADSR para uma voz.
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
    Atualiza o envelope ADSR da voz.
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