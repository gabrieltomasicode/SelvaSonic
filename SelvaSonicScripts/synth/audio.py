import numpy as np
from .waveforms import generate_wave
from .envelopes import calculate_adsr
from queue import Queue
visual_queue = Queue(maxsize=2)

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
                    # O cálculo vetorizado do ADSR recebe os frames e já atualiza voice.age
                    adsr_array = calculate_adsr(voice, config, frames)

                    # Se o pico máximo do array de envelope for audível, geramos a onda
                    if np.max(adsr_array) > 1e-4:
                        wave = generate_wave(voice, t, config)
                        
                        # Garante que a wave seja 2D [frames, 1] para o broadcasting funcionar
                        if wave.ndim == 1:
                            wave = wave[:, None]
                            
                        # gain agora é um array do tamanho do bloco, moldando o volume perfeitamente
                        gain = adsr_array * voice.velocity
                        
                        # Mixagem Estéreo Direta (Melhoria 2 já aplicada aqui)
                        output[:, 0] += (wave * gain)[:, 0]
                        output[:, 1] += (wave * gain)[:, 0]
                    else:
                        to_remove.add(note)

                    # Remove vozes inativas que já completaram o release
                    if not voice.active and adsr_array[-1, 0] <= 1e-6:
                        to_remove.add(note)

                except Exception as e:
                    print(f"Erro na voz {note}: {str(e)}")
                    to_remove.add(note)

            for note in to_remove:
                voices.pop(note, None)

        # Soft Clipping: A função tanh curva suavemente os picos que ultrapassam 1.0, 
        # criando uma saturação harmônica ("quente") em vez de um corte digital abrupto.
        # O parâmetro out=outdata garante que o resultado vá direto para o buffer de saída.
        np.tanh(output, out=outdata)

        visual_queue.put(outdata.copy())

        try:
            if visual_queue.full():
                visual_queue.get_nowait() # Remove o buffer antigo para dar lugar ao novo
            visual_queue.put_nowait(outdata.copy())
        except:
            pass
        peak = np.max(np.abs(outdata)) # Atualizado para ler o outdata já clipado
        print(f"🔈 Pico de saída: {peak:.2f} | Vozes: {len(voices)}", end='\r')

    except Exception as e:
        print(f"⛔ ERRO NO CALLBACK: {str(e)}")
        outdata.fill(0)