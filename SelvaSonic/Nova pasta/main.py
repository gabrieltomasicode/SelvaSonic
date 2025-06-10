<<<<<<< HEAD
from ui.interface import FullSynthInterface
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = FullSynthInterface(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)  
=======
from ui.interface import FullSynthInterface
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = FullSynthInterface(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)  
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8
    root.mainloop()