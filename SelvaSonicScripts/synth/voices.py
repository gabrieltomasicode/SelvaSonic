from dataclasses import dataclass
from typing import Optional
import math
from threading import Lock


@dataclass
class VoiceState:
    """
    Representa o estado de uma voz ativa no sintetizador.

    Atributos:
        frequency (float): Frequência atual da nota em Hz.
        velocity (float): Velocidade da nota (0.0-1.0).
        age (float): Tempo desde o início da nota em segundos.
        envelope (float): Valor atual do envelope (0.0-1.0).
        active (bool): Indica se a nota está ativa.
        release_start_time (Optional[float]): Momento de início do release.
        phase (float): Fase atual da onda.
    """
    frequency: float
    velocity: float
    age: float = 0.0
    envelope: float = 0.0
    active: bool = True
    release_start_time: Optional[float] = None  
    phase: float = 0.0

    def generate_sample(self, sample_rate: float = 44100.0, release_time: float = 0.3) -> float:
        """
        Gera um sample de áudio para a voz, considerando envelope, fase e release.

        Parâmetros:
            sample_rate (float): Taxa de amostragem em Hz (padrão: 44100.0).
            release_time (float): Tempo de release em segundos (padrão: 0.3).

        Retorna:
            float: Valor do sample gerado para a voz.

        Notas:
            - Se a voz estiver em release, calcula o decaimento do envelope.
            - Se a voz estiver inativa e o envelope zerado, retorna 0.0.
            - Gera uma onda senoidal básica, aplica envelope e velocity.
        """
        # Se a voz está em release, calcula o decaimento do envelope
        if self.release_start_time is not None:
            release_elapsed = self.age - self.release_start_time
            if release_elapsed >= 0:
                # Envelope decai linearmente durante o tempo de release
                self.envelope = max(0.0, 1.0 - (release_elapsed / release_time))
                if self.envelope == 0.0:
                    self.active = False  # Marca como inativa após o release

        if not self.active and self.envelope == 0.0:
            return 0.0

        # Gera forma de onda básica (senoidal)
        sample = math.sin(self.phase)

        # Atualiza fase
        self.phase += 2.0 * math.pi * self.frequency / sample_rate
        self.phase %= 2.0 * math.pi

        # Atualiza idade da voz
        self.age += 1.0 / sample_rate

        # Aplica envelope e velocidade
        return sample * self.envelope * self.velocity
    
class VoiceManager:
        """
        Gerencia as vozes ativas do sintetizador, controlando polifonia e concorrência.

        Responsável por adicionar, remover e atualizar vozes, garantindo thread safety.
        """
        def __init__(self, max_polyphony: int):
            """
            Inicializa o gerenciador de vozes.

            Parâmetros:
                max_polyphony (int): Número máximo de vozes simultâneas.
            """
            self.voices: dict[int, VoiceState] = {}
            self.lock = Lock()
            self.max_polyphony = max_polyphony

        def note_on(self, note: int, velocity: float, freq: float, get_time):
            """
            Ativa uma nova voz para a nota especificada.

            Parâmetros:
                note (int): Número da nota MIDI.
                velocity (float): Intensidade da nota (0.0 a 1.0).
                freq (float): Frequência da nota em Hz.
                get_time: Função para obter o tempo atual (não utilizada diretamente aqui).

            Notas:
                - Remove a voz antiga da mesma nota, se existir.
                - Se o limite de polifonia for atingido, remove a voz mais antiga.
            """
            with self.lock:
                if note in self.voices:
                    del self.voices[note]  # Remove imediatamente a voz antiga
                if len(self.voices) >= self.max_polyphony:
                    self._remove_oldest_voice()
                self.voices[note] = VoiceState(
                    frequency=freq,
                    velocity=velocity
                )

        def note_off(self, note: int, get_time):
            """
            Inicia o release da voz correspondente à nota.

            Parâmetros:
                note (int): Número da nota MIDI.
                get_time: Função para obter o tempo atual (não utilizada diretamente aqui).

            Notas:
                - O release só é iniciado se ainda não tiver sido iniciado anteriormente.
            """
            with self.lock:
                if note in self.voices:
                    # Inicia o release apenas se ainda não começou
                    if self.voices[note].release_start_time is None:
                        self.voices[note].release_start_time = self.voices[note].age

        def _remove_oldest_voice(self):
            """
            Inicia o release da voz correspondente à nota.

            Parâmetros:
                note (int): Número da nota MIDI.
                get_time: Função para obter o tempo atual (não utilizada diretamente aqui).

            Notas:
                - O release só é iniciado se ainda não tiver sido iniciado anteriormente.
            """
            with self.lock:
                if self.voices:
                    oldest_note = min(self.voices.keys(), key=lambda k: self.voices[k].age)
                    del self.voices[oldest_note]

        def get_voices(self):
            """
            Retorna o dicionário de vozes ativas.

            Retorna:
                dict[int, VoiceState]: Dicionário de vozes ativas indexado pela nota MIDI.
            """
            return self.voices

        def get_lock(self):
            """
            Retorna o lock utilizado para garantir acesso thread-safe às vozes.

            Retorna:
                Lock: Instância de threading.Lock.
            """
            return self.lock

    