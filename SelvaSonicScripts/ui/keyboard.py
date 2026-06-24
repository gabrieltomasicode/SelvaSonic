
from typing import Any, Dict

class KeyboardMIDI:
    """
    Classe para gerenciar a entrada de teclado MIDI virtual.

    Atributos:
        synth: Instância do sintetizador para processar eventos MIDI.
        octave_offset: Offset da oitava para ajustar as notas tocadas.
        master: Referência ao master para atualizações de UI.
        key_to_note: Mapeamento de teclas do teclado para notas MIDI.
    """
    def __init__(self, synth, master):
        """
        Inicializa o gerenciador de teclado MIDI virtual.

        Parâmetros:
            synth: Instância do sintetizador.
            master: Widget master para binds de eventos de teclado.
        """
        self.synth = synth
        self.octave_offset = 0  # 0 = oitava central
        self.master = master  # Referência ao master para atualizações de UI
        self.key_to_note = {
    # Primeira Oitava (C3-B3)
    'z': 48, 'x': 50, 'c': 52, 'v': 53, 'b': 55, 'n': 57, 'm': 59,
    's': 49,  # C#3
    'd': 51, 'g': 54, 'h': 56, 'j': 58,
    # Segunda Oitava (C4-B4)
    'a': 60, 'q': 61, 'w': 62, 'e': 63, 'r': 65, 't': 66, 'y': 67, 'u': 68,
    # Terceira Oitava (C5-B5)
    '1': 72, '2': 73, '3': 74, '4': 75, '5': 76, '6': 77, '7': 78
}
        self.pressed_notes = set()
        self.last_keycode = None

    def start(self):
        """
        Inicia o listener de teclado virtual, conectando os eventos do Tkinter.

        Notas:
            - Usa bind_all para capturar eventos de tecla pressionada e liberada.
        """
        # Substitua o listener por binds do Tkinter
        self.master.bind_all("<KeyPress>", self.on_press)
        self.master.bind_all("<KeyRelease>", self.on_release)

    def on_press(self, event):
        """
        Manipula o evento de tecla pressionada.
        """
        if event.keycode == self.last_keycode:
            return
        self.last_keycode = event.keycode

        key = event.char.lower() if event.char else ""
        if key == '-':
            self.octave_offset = max(-48, self.octave_offset - 12)
            return
        elif key == '=':
            self.octave_offset = min(48, self.octave_offset + 12)
            return

        note_info = self.key_to_note.get(key)
        if isinstance(note_info, int):
            note = note_info + self.octave_offset
            if 0 <= note <= 127 and note not in self.pressed_notes:
                self.pressed_notes.add(note)
                
                velocity = 0.70
                
                # 1. Envia a ordem para o Maestro (Áudio)
                if hasattr(self.synth, 'note_on'):
                    self.synth.note_on(note, velocity)
                
                # 2. Envia a ordem para a Interface (Visual)
                if hasattr(self, 'status_callback') and self.status_callback:
                    # Calcula a frequência para o painel
                    freq = 440.0 * (2.0 ** ((note - 69) / 12.0))
                    self.status_callback(is_on=True, note=note, freq=freq, velocity=velocity)


    def on_release(self, event):
        """
        Manipula o evento de tecla solta.
        """
        if event.keycode == self.last_keycode:
            self.last_keycode = None

        key = event.char.lower() if event.char else ""
        note_info = self.key_to_note.get(key)
        
        if isinstance(note_info, int):
            note = note_info + self.octave_offset
            if note in self.pressed_notes:
                self.pressed_notes.remove(note)
                
                # 1. Desliga o áudio
                if hasattr(self.synth, 'note_off'):
                    self.synth.note_off(note)
                
                # 2. Desliga a interface visual se nenhuma tecla estiver pressionada
                if hasattr(self, 'status_callback') and self.status_callback:
                    if len(self.pressed_notes) == 0:
                        self.status_callback(is_on=False)