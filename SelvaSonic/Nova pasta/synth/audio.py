import numpy as np
from .waveforms import generate_wave
from .envelopes import calculate_adsr

def audio_callback(outdata: np.ndarray, frames: int, time, status, config, voices, voices_lock):
    """
    Callback de áudio chamado pelo stream para gerar o áudio em tempo real.
    """
    if status:
        print(f"⚠️ Status do stream: {status}")

    try:
        output = np.zeros((frames, 2), dtype=np.float32)
        t = (time.currentTime + np.arange(frames) / config.sample_rate)[:, None]

        with voices_lock:
            current_voices = list(voices.items())
            to_remove = set()

            for note, voice in current_voices:
                try:
                    voice.age += frames / config.sample_rate
                    adsr = calculate_adsr(voice, config)
                    voice.envelope = adsr

                    if adsr > 1e-4:
                        wave = generate_wave(voice, t, config)
                        if wave.ndim == 1:
                            output += np.stack([wave, wave], axis=-1) * adsr * voice.velocity
                        else:
                            output += wave * adsr * voice.velocity
                    else:
                        to_remove.add(note)

                    if not voice.active and adsr <= 1e-6:
                        to_remove.add(note)

                except Exception as e:
                    print(f"Erro na voz {note}: {str(e)}")
                    to_remove.add(note)

            for note in to_remove:
                voices.pop(note, None)

        if np.max(np.abs(output)) > 1.0:
            output /= np.max(np.abs(output))
        np.clip(output, -1, 1, out=outdata)

        peak = np.max(np.abs(output))
        print(f"🔈 Pico de saída: {peak:.2f} | Vozes: {len(voices)}", end='\r')

    except Exception as e:
        print(f"⛔ ERRO NO CALLBACK: {str(e)}")
        outdata.fill(0)