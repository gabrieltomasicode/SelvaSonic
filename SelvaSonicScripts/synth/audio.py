import numpy as np
from .waveforms import generate_wave
from .envelopes import calculate_adsr

def audio_callback(outdata: np.ndarray, frames: int, time, status, config, voices, voices_lock):
    """
    Função de callback de áudio para geração em tempo real.

    Esta função é chamada pelo mecanismo de streaming de áudio para preencher o buffer de saída com dados de áudio sintetizados.
    Ela processa todas as vozes ativas, aplica envelopes ADSR, gera as formas de onda correspondentes e realiza a mixagem estéreo.
    As vozes que completam seu envelope são removidas. O sinal de saída é normalizado e limitado para evitar distorções.

    Parâmetros:
        outdata (np.ndarray): Buffer de saída a ser preenchido com amostras de áudio (formato: [frames, 2], dtype: float32).
        frames (int): Número de quadros de áudio a serem gerados.
        time: Objeto que fornece o tempo atual de reprodução (deve possuir o atributo 'currentTime').
        status: Indicador de status do stream; se não for None, indica um problema no fluxo de áudio.
        config: Objeto de configuração contendo parâmetros de áudio (ex: sample_rate).
        voices (dict): Dicionário de vozes ativas, indexado pela nota.
        voices_lock: Lock para garantir acesso thread-safe ao dicionário de vozes.

    Notas:
        - Esta função é projetada para ser thread-safe.
        - A saída é normalizada automaticamente se o pico de amplitude exceder 1.0.
        - Exceções são tratadas para evitar interrupções no áudio.

    Exceções:
        Nenhuma é propagada. Todas as exceções são capturadas e registradas; o buffer de saída é zerado em caso de erro.
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