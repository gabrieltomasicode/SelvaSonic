import tkinter as tk
from synth.config import SynthConfig
from synth.synth import MidiSynth
from ui.interface import FullSynthInterface  

def main():
    print("🎛️ Inicializando o Ecossistema SelvaSonic...")
    
    # 1. Cria a configuração ÚNICA global
    config = SynthConfig()
    
    # 2. Inicializa o motor de áudio ÚNICO usando essa configuração
    synth = MidiSynth(config=config)
    
    # 3. Inicia a janela do Tkinter
    root = tk.Tk()
    root.title("SelvaSonic MIDI Synth")
    
    # 4. INJEÇÃO DE DEPENDÊNCIA: Passamos o synth já pronto para a UI
    app = FullSynthInterface(master=root, synth=synth)
    
    # 5. Roda o loop principal da interface
    root.mainloop()

if __name__ == "__main__":
    main()