from typing import Any

def midi_callback(message, synth):
    """
    Callback para eventos MIDI.

    Args:
        message: Mensagem MIDI.
        synth: Instância do MidiSynth.
    """
    try:
        match message.type:
            case "note_on":
                synth.note_on(message.note, message.velocity / 127)
            case "note_off":
                synth.note_off(message.note)
            case _:
                pass
    except Exception as e:
        print(f"Erro no MIDI callback: {e}")