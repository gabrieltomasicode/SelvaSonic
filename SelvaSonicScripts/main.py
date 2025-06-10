from ui.interface import FullSynthInterface
import tkinter as tk

if __name__ == "__main__":
    """
    Ponto de entrada principal para a aplicação SelvaSonic.

    Cria a janela principal do Tkinter, inicializa a interface gráfica do sintetizador
    e inicia o loop principal da aplicação.
    """
    root = tk.Tk()
    app = FullSynthInterface(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)  
    root.mainloop()