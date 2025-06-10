<<<<<<< HEAD

from typing import Any, Dict

class KeyboardMIDI:
    """
    Classe para gerenciar a entrada de teclado MIDI virtual.

    Atributos:
    - synth: Instância do sintetizador para processar eventos MIDI.
    - octave_offset: Offset da oitava para ajustar as notas tocadas.
    - master: Referência ao master para atualizações de UI.
    - key_to_note: Mapeamento de teclas do teclado para notas MIDI.
    """
    def __init__(self, synth, master):
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
        # Substitua o listener por binds do Tkinter
        self.master.bind_all("<KeyPress>", self.on_press)
        self.master.bind_all("<KeyRelease>", self.on_release)

    def on_press(self, event):
        # Ignora auto-repeat baseado em keycode (opcional)
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
                self.synth.note_on(note, 0.7)

    def on_release(self, event):
        self.last_keycode = None  # Libera para próxima tecla
        key = event.char.lower() if event.char else ""
        note_info = self.key_to_note.get(key)
        if isinstance(note_info, int):
            note = note_info + self.octave_offset
            if 0 <= note <= 127 and note in self.pressed_notes:
                self.pressed_notes.remove(note)
=======

from typing import Any, Dict

class KeyboardMIDI:
    """
    Classe para gerenciar a entrada de teclado MIDI virtual.

    Atributos:
    - synth: Instância do sintetizador para processar eventos MIDI.
    - octave_offset: Offset da oitava para ajustar as notas tocadas.
    - master: Referência ao master para atualizações de UI.
    - key_to_note: Mapeamento de teclas do teclado para notas MIDI.
    """
    def __init__(self, synth, master):
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
        # Substitua o listener por binds do Tkinter
        self.master.bind_all("<KeyPress>", self.on_press)
        self.master.bind_all("<KeyRelease>", self.on_release)

    def on_press(self, event):
        # Ignora auto-repeat baseado em keycode (opcional)
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
                self.synth.note_on(note, 0.7)

    def on_release(self, event):
        self.last_keycode = None  # Libera para próxima tecla
        key = event.char.lower() if event.char else ""
        note_info = self.key_to_note.get(key)
        if isinstance(note_info, int):
            note = note_info + self.octave_offset
            if 0 <= note <= 127 and note in self.pressed_notes:
                self.pressed_notes.remove(note)
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8
                self.synth.note_off(note)