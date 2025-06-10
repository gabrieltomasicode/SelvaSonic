from ui.interface import FullSynthInterface
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = FullSynthInterface(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)  
    root.mainloop()