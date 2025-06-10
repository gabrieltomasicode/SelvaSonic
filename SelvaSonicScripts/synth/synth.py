from .config import SynthConfig
from .voices import  VoiceManager
from .audio import audio_callback
from .midi import midi_callback
from synth.utils import note_to_freq, get_time
import sounddevice as sd
from functools import partial
import mido

class MidiSynth:
    """
    Classe principal do sintetizador MIDI.

    Responsável por inicializar o áudio, processar eventos MIDI,
    gerenciar vozes, gerar áudio em tempo real e aplicar envelopes e filtros.
    Fornece métodos para controle dinâmico de parâmetros de síntese e gerenciamento de recursos.
    """

    def __init__(self, config: SynthConfig = SynthConfig()):
        """
        Inicializa o sintetizador MIDI.

        Parâmetros:
            config (SynthConfig): Objeto de configuração do sintetizador (opcional).

        Notas:
            - Inicializa o gerenciador de vozes, configura a porta MIDI e o stream de áudio.
            - Exibe mensagens informativas caso a porta MIDI não seja encontrada ou não especificada.
        """
        self.config = config
        self.voice_manager = VoiceManager(self.config.max_polyphony)
         
        try:
            if self.config.midi_port:
                self.midi_in = mido.open_input(
                    self.config.midi_port, 
                    callback=lambda msg: midi_callback(msg, self)
                )
            else:
                self.midi_in = None
                print("⚠️ Nenhuma porta MIDI especificada.")
        except OSError:
            self.midi_in = None
            print(f"⚠️ Porta MIDI '{self.config.midi_port}' não encontrada.")
            # Lista portas disponíveis
            available_ports = mido.get_input_names()
            if available_ports:
                print("Portas MIDI disponíveis:", available_ports)
            else:
                print("Nenhuma porta MIDI disponível no sistema.")
        self.running = False
        self.stream = sd.OutputStream(
            samplerate=self.config.sample_rate,
            blocksize=self.config.buffer_size,
            channels=2,
            callback=partial(
                audio_callback,
                config=self.config,
                voices=self.voice_manager.get_voices(),
                voices_lock=self.voice_manager.get_lock()
            )
        )
    
    
    def start(self):
        """
        Inicia o stream de áudio do sintetizador.

        Notas:
            - O sintetizador começa a processar e gerar áudio em tempo real.
            - Exibe mensagem de confirmação no console.
        """
        self.stream.start()
        self.running = True
        print("✅ Sintetizador iniciado.")

    def stop(self):
        """
        Interrompe o stream de áudio do sintetizador.

        Notas:
            - O processamento de áudio é pausado.
            - Exibe mensagem de confirmação no console.
        """
        self.stream.stop()
        self.running = False
        print("⏹️ Sintetizador parado.")
    
    def note_on(self, note: int, velocity: float):
        """
        Aciona uma nota no sintetizador.

        Parâmetros:
            note (int): Número da nota MIDI.
            velocity (float): Intensidade da nota (0.0 a 1.0).

        Notas:
            - Calcula a frequência correspondente e ativa a voz.
            - Exibe informações da nota no console.
        """
        freq = note_to_freq(note)
        self.voice_manager.note_on(note, velocity, freq, self.get_time)
        print(f"Nota ligada: {note} freq: {freq:.2f}Hz vel: {velocity:.2f}")

    def note_off(self, note: int):
        """
        Encerra uma nota no sintetizador.

        Parâmetros:
            note (int): Número da nota MIDI.

        Notas:
            - Libera a voz correspondente.
            - Exibe informações da nota no console.
        """
        self.voice_manager.note_off(note, self.get_time)
        print(f"Nota desligada: {note}")
    
    def on_close(self):
        """
        Encerra o sintetizador e libera todos os recursos.

        Notas:
            - Para o stream de áudio e fecha a porta MIDI, se aberta.
            - Exibe mensagem de encerramento no console.
        """
        if self.running:
            self.stop()
        if self.midi_in is not None:
            self.midi_in.close()
        print("🛑 Recursos do sintetizador liberados.")

    def set_lfo_freq(self, value):
        """
        Atualiza a frequência do LFO em tempo real.

        Parâmetros:
            value: Novo valor de frequência (float).
        """
        self.config.lfo_freq = float(value)

    def set_lfo_depth(self, value):
        """
        Atualiza a profundidade do LFO em tempo real.

        Parâmetros:
            value: Novo valor de profundidade (float).
        """
        self.config.lfo_depth = float(value)

    def set_lfo_target(self, value):
        """
        Atualiza o alvo do LFO em tempo real.

        Parâmetros:
            value: Novo alvo (string).
        """
        self.config.lfo_target = value

    def set_fm_freq(self, value):
        """
        Atualiza a frequência de modulação FM em tempo real.

        Parâmetros:
            value: Novo valor de frequência (float).
        """
        self.config.fm_mod_freq = float(value)

    def set_fm_index(self, value):
        """
        Atualiza o índice de modulação FM em tempo real.

        Parâmetros:
            value: Novo valor de índice (float).
        """
        self.config.fm_mod_index = float(value)

    def set_hfo_freq(self, value):
        """
        Atualiza a frequência do HFO em tempo real.

        Parâmetros:
            value: Novo valor de frequência (float).
        """
        self.config.hfo_freq = float(value)

    def set_hfo_depth(self, value):
        """
        Atualiza a profundidade do HFO em tempo real.

        Parâmetros:
            value: Novo valor de profundidade (float).
        """
        self.config.hfo_depth = float(value)

    def set_hfo_target(self, value):
        """
        Atualiza o alvo do HFO em tempo real.

        Parâmetros:
            value: Novo alvo (string).
        """
        self.config.hfo_target = value

    def set_additive(self, value):
        """
        Atualiza a quantidade de harmônicos aditivos em tempo real.

        Parâmetros:
            value: Novo valor de harmônicos (int).

        Notas:
            - Valores inválidos são tratados e uma mensagem é exibida.
        """
        try:
            self.config.additive_harmonics = int(round(float(value)))
            print(f"Quantidade de harmônicos aditivos atualizada para: {self.config.additive_harmonics}")
        except ValueError:
            print(f"Valor inválido para additive_harmonics: {value}")
    
    def set_waveform(self, waveform):
        """
        Atualiza a forma de onda padrão do sintetizador.

        Parâmetros:
            waveform: Nova forma de onda (enum ou string).
        """
        self.config.default_waveform = waveform
    
    def set_pulse_width(self, value):
        """
        Atualiza o pulse width em tempo real.

        Parâmetros:
            value: Novo valor de pulse width (float).
        """
        self.config.pulse_width = float(value)

    def set_supersaw_voices(self, value):
        """
        Atualiza a quantidade de vozes do modo SuperSaw em tempo real.

        Parâmetros:
            value: Novo valor de vozes (int).

        Notas:
            - Valores inválidos são tratados e uma mensagem é exibida.
        """
        print("super_saw_voices:", value)
        try:
            self.config.super_saw_voices = int(round(float(value)))
        except ValueError:
            print(f"Valor inválido para super_saw_voices: {value}")
    
    def set_polyphony(self, value):
        """
        Atualiza a polifonia máxima em tempo real.

        Parâmetros:
            value: Novo valor de polifonia (int).

        Notas:
            - Valores inválidos são tratados e uma mensagem é exibida.
        """
        try:
            poly = int(round(float(value)))
            self.config.max_polyphony = poly
            self.voice_manager.max_polyphony = poly
            print(f"Polifonia máxima atualizada para: {poly}")
        except ValueError:
            print(f"Valor inválido para polifonia: {value}")
            
    @staticmethod
    def __enter__(self):
        """
        Permite o uso do sintetizador como contexto (with statement).

        Retorna:
            self: Instância do sintetizador já iniciada.
        """
        self.start()
        return self

    @staticmethod
    def get_time():
        """
        Retorna o tempo atual do sistema para sincronização de eventos.

        Retorna:
            float: Tempo atual em segundos.
        """
        return get_time()

    def __exit__(self, *args):
        """
        Finaliza o sintetizador ao sair do contexto (with statement).

        Notas:
            - Para o stream de áudio automaticamente.
        """
        self.stop()