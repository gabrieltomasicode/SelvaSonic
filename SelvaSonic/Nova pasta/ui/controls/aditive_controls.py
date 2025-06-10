<<<<<<< HEAD
def update_additive(config, value, label):
    """
    Atualiza o número de harmônicos para síntese aditiva.
    """
    config.additive_harmonics = int(float(value))
=======
def update_additive(config, value, label):
    """
    Atualiza o número de harmônicos para síntese aditiva.
    """
    config.additive_harmonics = int(float(value))
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8
    label.config(text=str(int(float(value))))