<<<<<<< HEAD
def update_pulse(config, value, label):
    """
    Atualiza o valor da largura de pulso.
    """
    config.pulse_width = float(value)
=======
def update_pulse(config, value, label):
    """
    Atualiza o valor da largura de pulso.
    """
    config.pulse_width = float(value)
>>>>>>> ea848717f8f45d665d58c2022fd4f5fa1aa4b1a8
    label.config(text=f"{float(value):.2f}")