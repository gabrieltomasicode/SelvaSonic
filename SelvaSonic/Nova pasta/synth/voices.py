from dataclasses import dataclass
from typing import Optional
import math
from threading import Lock


@dataclass
class VoiceState:
    """
    Estado de uma voz ativa no sintetizador.

    Atributos:
        frequency (float): Frequência atual da nota em Hz.
        velocity (float): Velocidade da nota (0.0-1.0).
        age (float): Tempo desde o início da nota em segundos.
        envelope (float): Valor atual do envelope (0.0-1.0).
        active (bool): Flag indicando se a nota está ativa.
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
        def __init__(self, max_polyphony: int):
            self.voices: dict[int, VoiceState] = {}
            self.lock = Lock()
            self.max_polyphony = max_polyphony

        def note_on(self, note: int, velocity: float, freq: float, get_time):
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
            with self.lock:
                if note in self.voices:
                    # Inicia o release apenas se ainda não começou
                    if self.voices[note].release_start_time is None:
                        self.voices[note].release_start_time = self.voices[note].age

        def _remove_oldest_voice(self):
            with self.lock:
                if self.voices:
                    oldest_note = min(self.voices.keys(), key=lambda k: self.voices[k].age)
                    del self.voices[oldest_note]

        def get_voices(self):
            return self.voices

        def get_lock(self):
            return self.lock

    