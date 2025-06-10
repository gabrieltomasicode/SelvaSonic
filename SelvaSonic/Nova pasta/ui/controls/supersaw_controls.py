<<<<<<< HEAD
def update_ss_voices(config, value, label):
    """
    Atualiza o número de vozes para o oscilador Super Saw.
    """
    config.super_saw_voices = int(float(value))
=======
def update_ss_voices(config, value, label):
    """
    Atualiza o número de vozes para o oscilador Super Saw.
    """
    config.super_saw_voices = int(float(value))
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8
    label.config(text=str(int(float(value))))