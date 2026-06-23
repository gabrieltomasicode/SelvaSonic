import numpy as np

def generate_bandlimited_tables(sample_rate: int, table_size: int = 2048) -> dict:
    """
    Gera um banco de wavetables limitadas em banda para evitar aliasing.

    Calcula tabelas de onda (sawtooth e square) para todas as 128 notas MIDI.
    Cada tabela contém apenas os harmônicos que cabem abaixo da frequência 
    de Nyquist (sample_rate / 2) para a respectiva nota.

    Parâmetros:
        sample_rate (int): Taxa de amostragem do sistema em Hz.
        table_size (int): Resolução da tabela (quantidade de amostras por ciclo).

    Retorna:
        dict: Dicionário contendo 'sawtooth' e 'square', cada um mapeando 
              o número da nota MIDI (0-127) para o seu array np.ndarray.
    """
    tables = {
        'sawtooth': {},
        'square': {}
    }
    
    # Eixo de fase de 0 a 2*pi para um ciclo completo
    t = np.linspace(0, 2 * np.pi, table_size, endpoint=False)
    
    nyquist = sample_rate / 2.0

    print("⏳ Gerando Wavetables Limitadas em Banda...")

    for note in range(128):
        # Calcula a frequência fundamental da nota MIDI
        freq = 440.0 * (2.0 ** ((note - 69) / 12.0))
        
        # Se a frequência base já ultrapassa Nyquist, a onda será silenciosa
        if freq >= nyquist:
            tables['sawtooth'][note] = np.zeros(table_size, dtype=np.float32)
            tables['square'][note] = np.zeros(table_size, dtype=np.float32)
            continue

        # Calcula o número máximo de harmônicos permitidos
        max_harmonics = int(nyquist // freq)
        
        # Vetorização: Cria um array com os índices dos harmônicos [1, 2, 3, ..., max_harmonics]
        k_saw = np.arange(1, max_harmonics + 1)
        
        # Para a onda quadrada, usamos apenas harmônicos ímpares [1, 3, 5, ...]
        k_square = np.arange(1, max_harmonics + 1, 2)
        
        # Broadcasting para Sawtooth:
        # t[:, None] tem shape (2048, 1) e k_saw tem shape (max_harmonics,)
        # O resultado da multiplicação é (2048, max_harmonics)
        saw_phases = t[:, None] * k_saw
        saw_amps = 1.0 / k_saw
        # Soma todos os harmônicos (axis=1) multiplicados pela amplitude
        saw_wave = np.sum(np.sin(saw_phases) * saw_amps, axis=1)
        
        # Broadcasting para Square:
        square_phases = t[:, None] * k_square
        square_amps = 1.0 / k_square
        square_wave = np.sum(np.sin(square_phases) * square_amps, axis=1)

        # Normalização para garantir que o pico máximo não passe de [-1, 1]
        if np.max(np.abs(saw_wave)) > 0:
            saw_wave /= np.max(np.abs(saw_wave))
        if np.max(np.abs(square_wave)) > 0:
            square_wave /= np.max(np.abs(square_wave))

        # Salva as tabelas em formato float32 para otimizar memória e processamento
        tables['sawtooth'][note] = saw_wave.astype(np.float32)
        tables['square'][note] = square_wave.astype(np.float32)

    print("✅ Wavetables geradas com sucesso!")
    return tables