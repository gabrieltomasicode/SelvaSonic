from typing import Any

def midi_callback(message, synth):
    """
    Callback para eventos MIDI.

    Esta função é chamada sempre que uma mensagem MIDI é recebida. Ela interpreta o tipo de mensagem
    e executa a ação correspondente no sintetizador, como iniciar ou parar uma nota.

    Parâmetros:
        message: Mensagem MIDI recebida (deve possuir atributos como type, note e velocity).
        synth: Instância do sintetizador MIDI (MidiSynth) responsável pelo processamento das notas.

    Notas:
        - Suporta eventos "note_on" e "note_off".
        - A velocidade (velocity) da nota é normalizada para o intervalo [0.0, 1.0].
        - Outros tipos de mensagem MIDI são ignorados.
        - Em caso de erro, uma mensagem é exibida no console.

    Exceções:
        Nenhuma exceção é propagada. Todas as exceções são capturadas e tratadas internamente.
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