def update_ss_voices(config, value, label):
    """
    Atualiza o número de vozes para o oscilador Super Saw.
    """
    config.super_saw_voices = int(float(value))
    label.config(text=str(int(float(value))))