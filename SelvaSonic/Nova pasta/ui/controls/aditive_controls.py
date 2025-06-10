def update_additive(config, value, label):
    """
    Atualiza o número de harmônicos para síntese aditiva.
    """
    config.additive_harmonics = int(float(value))
    label.config(text=str(int(float(value))))